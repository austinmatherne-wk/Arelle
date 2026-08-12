import assert from 'node:assert/strict'
import { access, readFile } from 'node:fs/promises'
import { createServer } from 'node:http'
import { extname, join, normalize } from 'node:path'
import { test, before, after } from 'node:test'
import { fileURLToPath } from 'node:url'

import puppeteer from 'puppeteer-core'

const output = fileURLToPath(new URL('./public/', import.meta.url))
const storageKey = 'ixbrl-viewer-theme'
const products = ['gui', 'cli', 'python', 'docker', 'plugin']
const chromeCandidates = [
  process.env.CHROME_PATH,
  process.env.CHROME_BIN,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
  '/usr/bin/google-chrome-stable',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
].filter(Boolean)
const contentTypes = new Map([
  ['.css', 'text/css'],
  ['.htm', 'text/html'],
  ['.html', 'text/html'],
  ['.ico', 'image/x-icon'],
  ['.jpg', 'image/jpeg'],
  ['.js', 'text/javascript'],
  ['.json', 'application/json'],
  ['.png', 'image/png'],
  ['.svg', 'image/svg+xml'],
  ['.avif', 'image/avif'],
  ['.webp', 'image/webp'],
  ['.xml', 'application/xml'],
  ['.xsd', 'application/xml'],
])

let browser
let origin
let server

async function chromeExecutable() {
  for (const candidate of chromeCandidates) {
    try {
      await access(candidate)
      return candidate
    } catch {}
  }
  throw new Error('Chrome was not found; set CHROME_PATH to run served-artifact acceptance tests')
}

async function artifact(request, response) {
  const requestedPath = decodeURIComponent(new URL(request.url, 'http://localhost').pathname)
  const relativePath = requestedPath.endsWith('/') ? `${requestedPath}index.html` : requestedPath
  const filePath = join(output, normalize(relativePath).replace(/^(\.\.(\/|\\|$))+/, ''))

  try {
    const body = await readFile(filePath)
    response.writeHead(200, { 'content-type': contentTypes.get(extname(filePath)) ?? 'application/octet-stream' })
    response.end(body)
  } catch (error) {
    if (error.code !== 'ENOENT' && error.code !== 'EISDIR') throw error
    response.writeHead(404, { 'content-type': 'text/html' })
    response.end(await readFile(join(output, '404.html')))
  }
}

async function pageFor(scheme = 'light') {
  const context = await browser.createBrowserContext()
  const page = await context.newPage()
  await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }])
  return { context, page }
}

async function withPage(scheme, test) {
  const { context, page } = await pageFor(scheme)
  try {
    return await test(page)
  } finally {
    await context.close()
  }
}

before(async () => {
  server = createServer((request, response) => {
    artifact(request, response).catch((error) => {
      response.writeHead(500, { 'content-type': 'text/plain' })
      response.end(error.stack)
    })
  })
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve))
  origin = `http://127.0.0.1:${server.address().port}`
  browser = await puppeteer.launch({
    executablePath: await chromeExecutable(),
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  })
})

after(async () => {
  await browser?.close()
  if (server?.listening) {
    await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()))
  }
})

test('theme follows the operating system until the visitor makes a persisted choice', async () => {
  const { context, page } = await pageFor('dark')
  try {
    await page.goto(origin, { waitUntil: 'networkidle0' })
    assert.deepEqual(
      await page.evaluate((key) => ({
        background: getComputedStyle(document.body).backgroundColor,
        colorScheme: getComputedStyle(document.documentElement).colorScheme,
        fontFamily: getComputedStyle(document.body).fontFamily,
        label: document.querySelector('[data-theme-toggle]').ariaLabel,
        savedTheme: localStorage.getItem(key),
        theme: document.documentElement.dataset.theme ?? null,
      }), storageKey),
      {
        background: 'rgb(13, 16, 23)',
        colorScheme: 'dark',
        fontFamily: '"Instrument Sans", system-ui, sans-serif',
        label: 'Switch to light',
        savedTheme: null,
        theme: null,
      },
    )

    await page.locator('[data-theme-toggle]').click()
    assert.deepEqual(
      await page.evaluate((key) => ({
        background: getComputedStyle(document.body).backgroundColor,
        label: document.querySelector('[data-theme-toggle]').ariaLabel,
        savedTheme: localStorage.getItem(key),
        theme: document.documentElement.dataset.theme ?? null,
      }), storageKey),
      { background: 'rgb(247, 247, 244)', label: 'Switch to dark', savedTheme: 'light', theme: 'light' },
    )

    await page.reload({ waitUntil: 'networkidle0' })
    assert.deepEqual(
      await page.evaluate(() => ({
        colorScheme: getComputedStyle(document.documentElement).colorScheme,
        label: document.querySelector('[data-theme-toggle]').ariaLabel,
        theme: document.documentElement.dataset.theme,
      })),
      { colorScheme: 'light', label: 'Switch to dark', theme: 'light' },
    )
  } finally {
    await context.close()
  }
})

test('homepage comparison tabs progressively enhance mouse and keyboard input', async () => {
  const { context, page } = await pageFor('light')
  try {
    await page.setViewport({ width: 320, height: 300 })
    await page.goto(origin, { waitUntil: 'networkidle0' })
    assert.equal(await page.evaluate(() => window.scrollY), 0)
    const state = () => page.evaluate(() => ({
      tabs: [...document.querySelectorAll('[role="tab"]')].map((tab) => ({
        id: tab.id,
        selected: tab.getAttribute('aria-selected'),
        tabIndex: tab.tabIndex,
        focused: tab === document.activeElement,
      })),
      panels: [...document.querySelectorAll('[role="tabpanel"]')].map((panel) => ({
        id: panel.id,
        hidden: panel.hidden,
      })),
    }))

    assert.deepEqual(await state(), {
      tabs: [
        { id: 'tab-gui', selected: 'true', tabIndex: 0, focused: false },
        { id: 'tab-cli', selected: 'false', tabIndex: -1, focused: false },
        { id: 'tab-python', selected: 'false', tabIndex: -1, focused: false },
        { id: 'tab-docker', selected: 'false', tabIndex: -1, focused: false },
        { id: 'tab-plugin', selected: 'false', tabIndex: -1, focused: false },
      ],
      panels: [
        { id: 'panel-gui', hidden: false },
        { id: 'panel-cli', hidden: true },
        { id: 'panel-python', hidden: true },
        { id: 'panel-docker', hidden: true },
        { id: 'panel-plugin', hidden: true },
      ],
    })

    const originalUrl = page.url()
    await page.locator('#tab-cli').click()
    assert.equal(page.url(), originalUrl)
    assert.deepEqual(
      await state(),
      {
        tabs: [
          { id: 'tab-gui', selected: 'false', tabIndex: -1, focused: false },
          { id: 'tab-cli', selected: 'true', tabIndex: 0, focused: true },
          { id: 'tab-python', selected: 'false', tabIndex: -1, focused: false },
          { id: 'tab-docker', selected: 'false', tabIndex: -1, focused: false },
          { id: 'tab-plugin', selected: 'false', tabIndex: -1, focused: false },
        ],
        panels: [
          { id: 'panel-gui', hidden: true },
          { id: 'panel-cli', hidden: false },
          { id: 'panel-python', hidden: true },
          { id: 'panel-docker', hidden: true },
          { id: 'panel-plugin', hidden: true },
        ],
      },
    )

    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-python')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-python').hidden, false)

    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-docker')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-docker').hidden, false)

    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-plugin')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-plugin').hidden, false)

    await page.keyboard.press('ArrowLeft')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-docker')
    await page.keyboard.press('ArrowLeft')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-python')
    await page.keyboard.press('ArrowLeft')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-cli')
    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-python')
    await page.keyboard.press('Home')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-gui')
    await page.keyboard.press('End')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-plugin')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-plugin').hidden, false)
    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-gui')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-gui').hidden, false)
    await page.keyboard.press('ArrowLeft')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-plugin')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-plugin').hidden, false)

    await page.evaluate(() => {
      window.__tabDefaultPrevented = null
      document.querySelector('[role="tablist"]').addEventListener('keydown', (event) => {
        window.__tabDefaultPrevented = event.defaultPrevented
      })
      window.scrollTo(0, 0)
    })
    await page.keyboard.press('ArrowRight')
    assert.equal(await page.evaluate(() => window.__tabDefaultPrevented), true)
    assert.equal(await page.evaluate(() => window.scrollY), 0)

    await page.setViewport({ width: 320, height: 900 })
    await page.locator('#tab-gui').click()
    const visibility = await page.evaluate(() => {
      const list = document.querySelector('[role="tablist"]').getBoundingClientRect()
      const tab = document.querySelector('#tab-cli').getBoundingClientRect()
      return {
        pageOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
        selectedTabInList: tab.left >= list.left - 1 && tab.right <= list.right + 1,
      }
    })
    assert.equal(visibility.pageOverflow, false)
    await page.keyboard.press('End')
    assert.equal(
      await page.evaluate(() => {
        const list = document.querySelector('[role="tablist"]').getBoundingClientRect()
        const tab = document.querySelector('#tab-plugin').getBoundingClientRect()
        return tab.left >= list.left - 1 && tab.right <= list.right + 1
      }),
      true,
    )

    await page.evaluate(() => window.scrollTo(0, 0))
    await page.reload({ waitUntil: 'networkidle0' })
    const reset = await state()
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-gui').selected, 'true')
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-cli').selected, 'false')
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-python').selected, 'false')
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-docker').selected, 'false')
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-plugin').selected, 'false')
    assert.equal(reset.panels.find((panel) => panel.id === 'panel-cli').hidden, true)
    assert.equal(reset.panels.find((panel) => panel.id === 'panel-python').hidden, true)
    assert.equal(reset.panels.find((panel) => panel.id === 'panel-docker').hidden, true)
    assert.equal(reset.panels.find((panel) => panel.id === 'panel-plugin').hidden, true)
  } finally {
    await context.close()
  }
})

test('homepage product panels remain in document order without JavaScript', async () => {
  const context = await browser.createBrowserContext()
  const page = await context.newPage()
  try {
    await page.setJavaScriptEnabled(false)
    await page.goto(origin, { waitUntil: 'networkidle0' })
    assert.deepEqual(
      await page.$$eval('[role="tabpanel"]', (panels) => panels.map((panel) => ({
        id: panel.id,
        display: getComputedStyle(panel).display,
        hidden: panel.hidden,
      }))),
      [
        { id: 'panel-gui', display: 'block', hidden: false },
        { id: 'panel-cli', display: 'block', hidden: false },
        { id: 'panel-python', display: 'block', hidden: false },
        { id: 'panel-docker', display: 'block', hidden: false },
        { id: 'panel-plugin', display: 'block', hidden: false },
      ],
    )
  } finally {
    await context.close()
  }
})

test('homepage tab relationships remain valid in rendered browser output', async () => {
  await withPage('light', async (page) => {
    await page.goto(origin, { waitUntil: 'networkidle0' })
    assert.deepEqual(
      await page.$$eval('[role="tab"]', (tabs) => tabs.map((tab) => {
        const panel = document.getElementById(tab.getAttribute('aria-controls'))
        return {
          id: tab.id,
          controls: tab.getAttribute('aria-controls'),
          panelId: panel?.id,
          panelRole: panel?.getAttribute('role'),
          panelLabelledBy: panel?.getAttribute('aria-labelledby'),
        }
      })),
      products.map((product) => ({
        id: `tab-${product}`,
        controls: `panel-${product}`,
        panelId: `panel-${product}`,
        panelRole: 'tabpanel',
        panelLabelledBy: `tab-${product}`,
      })),
    )
  })
})

test('homepage remains usable at 320 pixels across the shell, panels, and matrix', async () => {
  await withPage('light', async (page) => {
    await page.setViewport({ width: 320, height: 900 })
    await page.goto(origin, { waitUntil: 'networkidle0' })

    const narrowLayout = await page.evaluate(() => {
      const viewportWidth = document.documentElement.clientWidth
      const fitsViewport = (element) => {
        const { left, right } = element.getBoundingClientRect()
        return left >= -1 && right <= viewportWidth + 1
      }
      const tablist = document.querySelector('[role="tablist"]')
      const setup = document.querySelector('.product-setup')
      const rows = [...document.querySelectorAll('.support-table tbody tr')]

      return {
        pageOverflow: document.documentElement.scrollWidth > viewportWidth,
        navigationFits: [...document.querySelectorAll(
          '.primary-navigation a, .primary-navigation button',
        )].every(fitsViewport),
        tabsFit: fitsViewport(tablist),
        tabsScroll: tablist.scrollWidth > tablist.clientWidth,
        setupStacked: getComputedStyle(setup).flexDirection === 'column',
        tableIsSemantic: document.querySelector('.support-table') instanceof HTMLTableElement,
        longNamesWrap: [...document.querySelectorAll(
          '.support-table h3, .support-table p, .support-items li',
        )].every((element) => element.scrollWidth <= element.clientWidth),
        rowsStacked: rows.every((row) => {
          const group = row.querySelector('th').getBoundingClientRect()
          const supported = row.querySelector('td').getBoundingClientRect()
          return group.bottom <= supported.top + 1
        }),
      }
    })

    assert.deepEqual(narrowLayout, {
      pageOverflow: false,
      navigationFits: true,
      tabsFit: true,
      tabsScroll: true,
      setupStacked: true,
      tableIsSemantic: true,
      longNamesWrap: true,
      rowsStacked: true,
    })

    for (const product of products) {
      await page.locator(`#tab-${product}`).click()
      const selectedPanel = await page.evaluate(() => {
        const viewportWidth = document.documentElement.clientWidth
        const panel = document.querySelector('[role="tabpanel"]:not([hidden])')
        const tablist = document.querySelector('[role="tablist"]')
        const selectedTab = tablist.querySelector('[aria-selected="true"]').getBoundingClientRect()
        const tablistBounds = tablist.getBoundingClientRect()
        return {
          pageOverflow: document.documentElement.scrollWidth > viewportWidth,
          contentFits: [...panel.querySelectorAll('*')].every((element) => (
            element.getBoundingClientRect().right <= viewportWidth + 1
          )),
          selectedTabVisible: selectedTab.left >= tablistBounds.left - 1
            && selectedTab.right <= tablistBounds.right + 1,
        }
      })
      assert.equal(selectedPanel.pageOverflow, false, `tab-${product} should not create page overflow`)
      assert.equal(selectedPanel.contentFits, true, `tab-${product} content should fit the viewport`)
      assert.equal(selectedPanel.selectedTabVisible, true, `tab-${product} should remain visible`)
    }
  })
})

test('homepage removes animation and transitions when reduced motion is requested', async () => {
  await withPage('light', async (page) => {
    await page.emulateMediaFeatures([
      { name: 'prefers-color-scheme', value: 'light' },
      { name: 'prefers-reduced-motion', value: 'reduce' },
    ])
    await page.goto(origin, { waitUntil: 'networkidle0' })

    assert.deepEqual(
      await page.evaluate(() => ({
        scrollBehavior: getComputedStyle(document.documentElement).scrollBehavior,
        heroAnimation: getComputedStyle(document.querySelector('.homepage-introduction > *')).animationName,
        actionTransition: getComputedStyle(document.querySelector('.homepage-actions a')).transitionProperty,
        navigationTransition: getComputedStyle(document.querySelector('.primary-navigation li a')).transitionProperty,
        themeTransition: getComputedStyle(document.querySelector('.theme-toggle')).transitionProperty,
        tabTransition: getComputedStyle(document.querySelector('.product-tabs button')).transitionProperty,
        tabIndicatorTransition: getComputedStyle(
          document.querySelector('.product-tabs button'),
          '::after',
        ).transitionProperty,
        panelTransition: getComputedStyle(document.querySelector('.product-panel')).transitionProperty,
      })),
      {
        scrollBehavior: 'auto',
        heroAnimation: 'none',
        actionTransition: 'none',
        navigationTransition: 'none',
        themeTransition: 'none',
        tabTransition: 'none',
        tabIndicatorTransition: 'none',
        panelTransition: 'none',
      },
    )
  })
})

test('homepage only fetches the effective GUI capture after it becomes visible', async () => {
  for (const scheme of ['light', 'dark']) {
    const inactiveScheme = scheme === 'light' ? 'dark' : 'light'
    await withPage(scheme, async (page) => {
      const requests = []
      page.on('request', (request) => {
        const path = new URL(request.url()).pathname
        if (/gui-(?:light|dark)/.test(path)) requests.push(path)
      })
      await page.goto(origin, { waitUntil: 'networkidle0' })
      await page.$eval('.product-shot', (element) => element.scrollIntoView({ block: 'center' }))
      await new Promise((resolve) => setTimeout(resolve, 500))

      assert.equal(
        requests.some((path) => path.includes(`gui-${scheme}`)),
        true,
        `${scheme} capture should load when it enters the viewport`,
      )
      assert.equal(
        requests.some((path) => path.includes(`gui-${inactiveScheme}`)),
        false,
        `${scheme} capture should not load its inactive variant`,
      )
    })
  }
})

test('homepage keyboard focus follows navigation, hero, tabs, panel action, and footer', async () => {
  for (const scheme of ['light', 'dark']) {
    await withPage(scheme, async (page) => {
      await page.goto(origin, { waitUntil: 'networkidle0' })
      await page.evaluate(() => document.body.focus())

      for (const selector of [
        '.wordmark',
        '.primary-navigation a[href="/download/"]',
        '.primary-navigation a[href="/blog/"]',
        '.primary-navigation a[href="https://arelle.readthedocs.io/"]',
        '.primary-navigation a[href="https://github.com/Arelle/Arelle"]',
        '[data-theme-toggle]',
        '.homepage-action-primary',
        '.homepage-action-secondary',
        '.homepage-certification a',
        '#tab-gui',
        '#panel-gui .product-setup a',
        '.footer-navigation a[href="/about/"]',
        '.footer-navigation a[href="https://groups.google.com/d/forum/arelle-users"]',
        '.footer-navigation a[href="https://arelle.readthedocs.io/en/latest/contributor_guides/contributing.html"]',
        '.footer-navigation a[href="mailto:support@arelle.org"]',
      ]) {
        await page.keyboard.press('Tab')
        assert.equal(
          await page.evaluate((expected) => document.activeElement.matches(expected), selector),
          true,
          `expected focus to move to ${selector}`,
        )
        if (selector === '.wordmark') {
          assert.deepEqual(
            await page.evaluate(() => {
              const style = getComputedStyle(document.activeElement)
              return { outlineStyle: style.outlineStyle, outlineWidth: style.outlineWidth }
            }),
            { outlineStyle: 'solid', outlineWidth: '2px' },
          )
        }
      }
    })
  }
})

test('Docker panel is selectable through the public tab interface', async () => {
  const { context, page } = await pageFor('light')
  try {
    await page.goto(origin, { waitUntil: 'networkidle0' })
    await page.locator('#tab-docker').click()
    assert.deepEqual(
      await page.evaluate(() => ({
        selected: document.querySelector('#tab-docker').getAttribute('aria-selected'),
        focused: document.activeElement.id,
        panelHidden: document.querySelector('#panel-docker').hidden,
        setup: document.querySelector('#panel-docker .product-setup').textContent.replace(/\s+/g, ' ').trim(),
      })),
      {
        selected: 'true',
        focused: 'tab-docker',
        panelHidden: false,
        setup: 'Use DockerPull the published image with docker pull arelleproject/arelleOpen Docker Hub →',
      },
    )
  } finally {
    await context.close()
  }
})

test('Plugin panel is selectable through the public tab interface', async () => {
  const { context, page } = await pageFor('light')
  try {
    await page.goto(origin, { waitUntil: 'networkidle0' })
    await page.locator('#tab-plugin').click()
    assert.deepEqual(
      await page.evaluate(() => ({
        selected: document.querySelector('#tab-plugin').getAttribute('aria-selected'),
        focused: document.activeElement.id,
        panelHidden: document.querySelector('#panel-plugin').hidden,
        setup: document.querySelector('#panel-plugin .product-setup').textContent.replace(/\s+/g, ' ').trim(),
      })),
      {
        selected: 'true',
        focused: 'tab-plugin',
        panelHidden: false,
        setup: 'Build a pluginUse the maintained plugin scaffolding rather than mounting raw validation hooks by hand. Plugins extend validation, loading, UI, export, and other behavior.Read the plugin development guide →',
      },
    )
  } finally {
    await context.close()
  }
})

test('GUI captures follow system and explicit visitor themes', async () => {
  const { context, page } = await pageFor('dark')
  try {
    await page.goto(origin, { waitUntil: 'networkidle0' })
    const captureDisplay = () => page.evaluate(() => ({
      light: getComputedStyle(document.querySelector('picture.shot-light')).display,
      dark: getComputedStyle(document.querySelector('picture.shot-dark')).display,
    }))
    assert.deepEqual(await captureDisplay(), { light: 'none', dark: 'block' })

    await page.locator('[data-theme-toggle]').click()
    assert.deepEqual(await captureDisplay(), { light: 'block', dark: 'none' })
    assert.equal(await page.evaluate(() => document.documentElement.dataset.theme), 'light')
  } finally {
    await context.close()
  }
})

test('Python API source and output remain distinct in both themes', async () => {
  for (const scheme of ['light', 'dark']) {
    const { context, page } = await pageFor(scheme)
    try {
      await page.goto(origin, { waitUntil: 'networkidle0' })
      await page.locator('#tab-python').click()
      const [sourceStyle, outputStyle] = await page.evaluate(() => [
        '.python-example-source',
        '.python-example-output',
      ].map((selector) => {
        const element = document.querySelector(`#panel-python ${selector}`)
        const style = getComputedStyle(element)
        const code = getComputedStyle(element.querySelector('code'))
        return {
          display: style.display,
          borderLeftColor: style.borderLeftColor,
          codeColor: code.color,
        }
      }))
      assert.equal(sourceStyle.display, 'block')
      assert.equal(outputStyle.display, 'block')
      assert.notEqual(sourceStyle.borderLeftColor, outputStyle.borderLeftColor)
      assert.notEqual(sourceStyle.codeColor, 'rgba(0, 0, 0, 0)')
      assert.notEqual(outputStyle.codeColor, 'rgba(0, 0, 0, 0)')
    } finally {
      await context.close()
    }
  }
})

test('keyboard focus, current navigation, and reduced motion remain observable in the artifact', async () => {
  const { context, page } = await pageFor()
  try {
    await page.emulateMediaFeatures([
      { name: 'prefers-color-scheme', value: 'light' },
      { name: 'prefers-reduced-motion', value: 'reduce' },
    ])
    await page.goto(`${origin}/download/`, { waitUntil: 'networkidle0' })

    const current = await page.$eval('.primary-navigation a[aria-current="page"]', (link) => {
      const style = getComputedStyle(link)
      return {
        backgroundColor: style.backgroundColor,
        borderColor: style.borderColor,
        color: style.color,
        fontWeight: style.fontWeight,
        label: link.textContent.trim(),
        transitionDuration: style.transitionDuration,
      }
    })
    assert.deepEqual(current, {
      backgroundColor: 'rgb(255, 255, 255)',
      borderColor: 'rgb(201, 199, 191)',
      color: 'rgb(20, 23, 28)',
      fontWeight: '700',
      label: 'Download',
      transitionDuration: '0s',
    })

    const footer = await page.$eval('.site-footer', (element) => {
      const style = getComputedStyle(element)
      const trademark = getComputedStyle(element.querySelector('.footer-trademark'))
      return {
        borderTopColor: style.borderTopColor,
        color: style.color,
        display: style.display,
        fontFamily: style.fontFamily,
        trademarkBorderTopColor: trademark.borderTopColor,
        trademarkOpacity: trademark.opacity,
      }
    })
    assert.deepEqual(footer, {
      borderTopColor: 'rgb(227, 226, 220)',
      color: 'rgb(113, 118, 127)',
      display: 'grid',
      fontFamily: '"Instrument Sans", system-ui, sans-serif',
      trademarkBorderTopColor: 'rgb(227, 226, 220)',
      trademarkOpacity: '0.8',
    })

    await page.keyboard.press('Tab')
    const focus = await page.evaluate(() => {
      const focused = document.activeElement
      const style = getComputedStyle(focused)
      return {
        href: focused.getAttribute('href'),
        outlineStyle: style.outlineStyle,
        outlineWidth: style.outlineWidth,
      }
    })
    assert.equal(focus.href, '/')
    assert.equal(focus.outlineStyle, 'solid')
    assert.notEqual(focus.outlineWidth, '0px')
  } finally {
    await context.close()
  }
})

test('the generated Viewer consumes the website theme choice', async () => {
  const { context, page } = await pageFor()
  try {
    await page.goto(origin, { waitUntil: 'networkidle0' })
    await page.locator('[data-theme-toggle]').click()
    assert.equal(await page.evaluate((key) => localStorage.getItem(key), storageKey), 'dark')

    await page.goto(`${origin}/demo/ixbrl-viewer/viewer.htm`, { waitUntil: 'networkidle0' })
    assert.deepEqual(
      await page.evaluate((key) => ({
        background: getComputedStyle(document.body).backgroundColor,
        darkModeSelected: document.querySelector('#dark-mode-on').classList.contains('selected'),
        savedTheme: localStorage.getItem(key),
      }), storageKey),
      { background: 'rgb(0, 0, 0)', darkModeSelected: true, savedTheme: 'dark' },
    )
  } finally {
    await context.close()
  }
})
