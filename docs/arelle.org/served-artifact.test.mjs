import assert from 'node:assert/strict'
import { access, readFile } from 'node:fs/promises'
import { createServer } from 'node:http'
import { extname, join, normalize } from 'node:path'
import { test, before, after } from 'node:test'
import { fileURLToPath } from 'node:url'

import puppeteer from 'puppeteer-core'

const output = fileURLToPath(new URL('./public/', import.meta.url))
const storageKey = 'ixbrl-viewer-theme'
const products = ['gui', 'cli', 'docker', 'python', 'plugin', 'webserver']
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
      { background: 'rgb(242, 241, 236)', label: 'Switch to dark', savedTheme: 'light', theme: 'light' },
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
        { id: 'tab-docker', selected: 'false', tabIndex: -1, focused: false },
        { id: 'tab-python', selected: 'false', tabIndex: -1, focused: false },
        { id: 'tab-plugin', selected: 'false', tabIndex: -1, focused: false },
        { id: 'tab-webserver', selected: 'false', tabIndex: -1, focused: false },
      ],
      panels: [
        { id: 'panel-gui', hidden: false },
        { id: 'panel-cli', hidden: true },
        { id: 'panel-docker', hidden: true },
        { id: 'panel-python', hidden: true },
        { id: 'panel-plugin', hidden: true },
        { id: 'panel-webserver', hidden: true },
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
          { id: 'tab-docker', selected: 'false', tabIndex: -1, focused: false },
          { id: 'tab-python', selected: 'false', tabIndex: -1, focused: false },
          { id: 'tab-plugin', selected: 'false', tabIndex: -1, focused: false },
          { id: 'tab-webserver', selected: 'false', tabIndex: -1, focused: false },
        ],
        panels: [
          { id: 'panel-gui', hidden: true },
          { id: 'panel-cli', hidden: false },
          { id: 'panel-docker', hidden: true },
          { id: 'panel-python', hidden: true },
          { id: 'panel-plugin', hidden: true },
          { id: 'panel-webserver', hidden: true },
        ],
      },
    )

    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-docker')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-docker').hidden, false)

    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-python')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-python').hidden, false)

    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-plugin')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-plugin').hidden, false)

    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-webserver')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-webserver').hidden, false)

    await page.keyboard.press('ArrowLeft')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-plugin')
    await page.keyboard.press('ArrowLeft')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-python')
    await page.keyboard.press('ArrowLeft')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-docker')
    await page.keyboard.press('ArrowLeft')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-cli')
    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-docker')
    await page.keyboard.press('Home')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-gui')
    await page.keyboard.press('End')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-webserver')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-webserver').hidden, false)
    await page.keyboard.press('ArrowRight')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-gui')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-gui').hidden, false)
    await page.keyboard.press('ArrowLeft')
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-webserver')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-webserver').hidden, false)

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
        const tab = document.querySelector('#tab-webserver').getBoundingClientRect()
        return tab.left >= list.left - 1 && tab.right <= list.right + 1
      }),
      true,
    )

    await page.evaluate(() => window.scrollTo(0, 0))
    await page.reload({ waitUntil: 'networkidle0' })
    const reset = await state()
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-gui').selected, 'true')
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-cli').selected, 'false')
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-docker').selected, 'false')
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-python').selected, 'false')
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-plugin').selected, 'false')
    assert.equal(reset.tabs.find((tab) => tab.id === 'tab-webserver').selected, 'false')
    assert.equal(reset.panels.find((panel) => panel.id === 'panel-cli').hidden, true)
    assert.equal(reset.panels.find((panel) => panel.id === 'panel-docker').hidden, true)
    assert.equal(reset.panels.find((panel) => panel.id === 'panel-python').hidden, true)
    assert.equal(reset.panels.find((panel) => panel.id === 'panel-plugin').hidden, true)
    assert.equal(reset.panels.find((panel) => panel.id === 'panel-webserver').hidden, true)
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
        { id: 'panel-docker', display: 'block', hidden: false },
        { id: 'panel-python', display: 'block', hidden: false },
        { id: 'panel-plugin', display: 'block', hidden: false },
        { id: 'panel-webserver', display: 'block', hidden: false },
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
      const columns = (rects) => {
        const lefts = []
        for (const rect of rects) {
          if (!lefts.some((left) => Math.abs(left - rect.left) < 2)) lefts.push(rect.left)
        }
        return lefts.length
      }
      const tablist = document.querySelector('[role="tablist"]')
      const setup = document.querySelector('.product-setup')
      const cards = [...document.querySelectorAll('.support-split-card')]
      const nav = document.querySelector('.primary-navigation').getBoundingClientRect()
      const wordmark = document.querySelector('.wordmark').getBoundingClientRect()
      const theme = document.querySelector('[data-theme-toggle]').getBoundingClientRect()
      const destinationLinks = [...document.querySelectorAll('.primary-navigation ul a')]
      const destinations = destinationLinks.map((link) => link.getBoundingClientRect())
      const linkRow = document.querySelector('.primary-navigation ul').getBoundingClientRect()
      const tabs = [...tablist.querySelectorAll('[role="tab"]')]
        .map((tab) => tab.getBoundingClientRect())

      return {
        pageOverflow: document.documentElement.scrollWidth > viewportWidth,
        navigationFits: [...document.querySelectorAll(
          '.primary-navigation a, .primary-navigation button',
        )].every(fitsViewport),
        themeBesideWordmark: theme.left >= wordmark.right - 1
          && theme.top < wordmark.bottom
          && theme.bottom > wordmark.top,
        linksBelowWordmark: destinations.every((link) => link.top >= wordmark.bottom - 1),
        linkRowSpansNav: Math.abs(linkRow.width - nav.width) <= 2,
        labelsFit: destinationLinks.every((link) => link.scrollWidth <= link.clientWidth + 1),
        labelsContained: destinationLinks.every((link) => {
          const a = link.getBoundingClientRect()
          const li = link.parentElement.getBoundingClientRect()
          return a.top >= li.top - 1 && a.bottom <= li.bottom + 1
        }),
        navColumns: columns(destinations),
        tabsFit: fitsViewport(tablist),
        tabsScroll: tablist.scrollWidth > tablist.clientWidth,
        tabColumns: columns(tabs),
        allTabsVisible: [...tablist.querySelectorAll('[role="tab"]')].every((tab) => {
          const bounds = tab.getBoundingClientRect()
          const list = tablist.getBoundingClientRect()
          return fitsViewport(tab)
            && bounds.left >= list.left - 1
            && bounds.right <= list.right + 1
            && bounds.top >= list.top - 1
            && bounds.bottom <= list.bottom + 1
        }),
        setupStacked: getComputedStyle(setup).flexDirection === 'column',
        cardsStacked: cards.length === 2 && cards[0].getBoundingClientRect().bottom <= cards[1].getBoundingClientRect().top + 1,
        longNamesWrap: [...document.querySelectorAll(
          '.support-split-card h3, .support-split-card h4, .support-split-card p, .support-items li',
        )].every((element) => element.scrollWidth <= element.clientWidth),
      }
    })

    assert.deepEqual(narrowLayout, {
      pageOverflow: false,
      navigationFits: true,
      themeBesideWordmark: true,
      linksBelowWordmark: true,
      linkRowSpansNav: true,
      labelsFit: true,
      labelsContained: true,
      navColumns: 1,
      tabsFit: true,
      tabsScroll: false,
      tabColumns: 1,
      allTabsVisible: true,
      setupStacked: true,
      cardsStacked: true,
      longNamesWrap: true,
    })

    await page.setViewport({ width: 400, height: 900 })
    const twoColumnLayout = await page.evaluate(() => {
      const columns = (rects) => {
        const lefts = []
        for (const rect of rects) {
          if (!lefts.some((left) => Math.abs(left - rect.left) < 2)) lefts.push(rect.left)
        }
        return lefts.length
      }
      return {
        navColumns: columns([...document.querySelectorAll('.primary-navigation ul a')]
          .map((link) => link.getBoundingClientRect())),
        tabColumns: columns([...document.querySelectorAll('[role="tab"]')]
          .map((tab) => tab.getBoundingClientRect())),
      }
    })
    assert.deepEqual(twoColumnLayout, { navColumns: 2, tabColumns: 2 })

    await page.setViewport({ width: 800, height: 900 })
    const threeColumnLayout = await page.evaluate(() => {
      const columns = (rects) => {
        const lefts = []
        for (const rect of rects) {
          if (!lefts.some((left) => Math.abs(left - rect.left) < 2)) lefts.push(rect.left)
        }
        return lefts.length
      }
      return {
        tabColumns: columns([...document.querySelectorAll('[role="tab"]')]
          .map((tab) => tab.getBoundingClientRect())),
      }
    })
    assert.deepEqual(threeColumnLayout, { tabColumns: 3 })

    await page.setViewport({ width: 1200, height: 900 })
    const sixColumnLayout = await page.evaluate(() => {
      const columns = (rects) => {
        const lefts = []
        for (const rect of rects) {
          if (!lefts.some((left) => Math.abs(left - rect.left) < 2)) lefts.push(rect.left)
        }
        return lefts.length
      }
      return {
        tabColumns: columns([...document.querySelectorAll('[role="tab"]')]
          .map((tab) => tab.getBoundingClientRect())),
      }
    })
    assert.deepEqual(sixColumnLayout, { tabColumns: 6 })

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
        '.primary-navigation a[href="/updates/"]',
        '.primary-navigation a[href="https://arelle.readthedocs.io/"]',
        '.primary-navigation a[href="https://github.com/Arelle/Arelle"]',
        '[data-theme-toggle]',
        '.homepage-action-primary',
        '.homepage-certification a',
        '#tab-gui',
        '#panel-gui .product-setup a',
        '.footer-navigation a[href="/about/"]',
        '.footer-navigation a[href="https://groups.google.com/g/arelle-users"]',
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

test('Web server panel is selectable through the public tab interface', async () => {
  const { context, page } = await pageFor('light')
  try {
    await page.goto(origin, { waitUntil: 'networkidle0' })
    await page.locator('#tab-webserver').click()
    assert.deepEqual(
      await page.evaluate(() => ({
        selected: document.querySelector('#tab-webserver').getAttribute('aria-selected'),
        focused: document.activeElement.id,
        panelHidden: document.querySelector('#panel-webserver').hidden,
        setup: (() => {
          const setup = document.querySelector('#panel-webserver .product-setup')
          return [
            setup.querySelector('.product-setup-label').textContent,
            setup.querySelector('p').textContent,
            setup.querySelector('a').textContent,
          ].map((text) => text.trim()).join(' ')
        })(),
      })),
      {
        selected: 'true',
        focused: 'tab-webserver',
        panelHidden: false,
        setup: 'Run the web server Use the local HTTP development server. Read the webserver security policy →',
      },
    )
  } finally {
    await context.close()
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
        setup: (() => {
          const setup = document.querySelector('#panel-docker .product-setup')
          return [
            setup.querySelector('.product-setup-label').textContent,
            setup.querySelector('p').textContent,
            setup.querySelector('a').textContent,
          ].map((text) => text.trim()).join(' ')
        })(),
      })),
      {
        selected: 'true',
        focused: 'tab-docker',
        panelHidden: false,
        setup: 'Use Docker Pull the official image with docker pull arelleproject/arelle Open Docker Hub →',
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
        setup: (() => {
          const setup = document.querySelector('#panel-plugin .product-setup')
          return [
            setup.querySelector('.product-setup-label').textContent,
            setup.querySelector('p').textContent,
            setup.querySelector('a').textContent,
          ].map((text) => text.trim()).join(' ')
        })(),
      })),
      {
        selected: 'true',
        focused: 'tab-plugin',
        panelHidden: false,
        setup: "Build a plugin Extend Arelle's capabilities with custom validation rules, data extraction, or UI enhancements. Read the plugin development guide →",
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

test('source example commands scroll within stacked narrow panels', async () => {
  await withPage('light', async (page) => {
    await page.setViewport({ width: 320, height: 900 })
    await page.goto(origin, { waitUntil: 'networkidle0' })

    for (const product of ['python', 'plugin']) {
      await page.locator(`#tab-${product}`).click()
      const command = await page.$eval(
        `#panel-${product} .${product}-example-output pre:first-of-type`,
        (element) => {
          const style = getComputedStyle(element)
          const frame = element.closest('.python-example-frame, .plugin-example-frame')
          return {
            columns: getComputedStyle(frame).gridTemplateColumns.split(/\s+/).length,
            overflowX: style.overflowX,
            whiteSpace: style.whiteSpace,
          }
        },
      )
      assert.deepEqual(command, {
        columns: 1,
        overflowX: 'auto',
        whiteSpace: 'pre',
      })

      const source = await page.$eval(
        `#panel-${product} .${product}-example-source pre`,
        (element) => {
          const style = getComputedStyle(element)
          return {
            horizontalOverflow: element.scrollWidth > element.clientWidth,
            overflowWrap: style.overflowWrap,
            overflowX: style.overflowX,
            whiteSpace: style.whiteSpace,
          }
        },
      )
      assert.deepEqual(source, {
        horizontalOverflow: true,
        overflowWrap: 'normal',
        overflowX: 'auto',
        whiteSpace: 'pre',
      })
    }
  })
})

test('source examples stack before medium layouts become cramped', async () => {
  await withPage('light', async (page) => {
    for (const [width, columns] of [[1024, 1], [1200, 2]]) {
      await page.setViewport({ width, height: 900 })
      await page.goto(origin, { waitUntil: 'networkidle0' })

      for (const product of ['python', 'plugin']) {
        await page.locator(`#tab-${product}`).click()
        assert.equal(
          await page.$eval(
            `#panel-${product} .${product}-example-frame`,
            (element) => getComputedStyle(element).gridTemplateColumns.split(/\s+/).length,
          ),
          columns,
          `${product} should use ${columns} column(s) at ${width}px`,
        )
        if (columns === 1) {
          assert.deepEqual(
            await page.$eval(
              `#panel-${product} .${product}-example-source pre`,
              (element) => {
                const style = getComputedStyle(element)
                return {
                  overflowWrap: style.overflowWrap,
                  whiteSpace: style.whiteSpace,
                }
              },
            ),
            { overflowWrap: 'normal', whiteSpace: 'pre' },
          )
        }
      }
    }
  })
})

test('CLI example switches to shell continuations in narrow containers', async () => {
  await withPage('light', async (page) => {
    const commandDisplay = () => page.evaluate(() => ({
      wide: getComputedStyle(document.querySelector('#panel-cli .console-command-wide')).display,
      narrow: getComputedStyle(document.querySelector('#panel-cli .console-command-narrow')).display,
    }))

    await page.setViewport({ width: 320, height: 900 })
    await page.goto(origin, { waitUntil: 'networkidle0' })
    await page.locator('#tab-cli').click()
    assert.deepEqual(await commandDisplay(), { wide: 'none', narrow: 'block' })

    await page.setViewport({ width: 1200, height: 900 })
    assert.deepEqual(await commandDisplay(), { wide: 'block', narrow: 'none' })
  })
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
      backgroundColor: 'rgba(0, 0, 0, 0)',
      borderColor: 'rgba(0, 0, 0, 0)',
      color: 'rgb(19, 21, 24)',
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
      borderTopColor: 'rgb(214, 211, 200)',
      color: 'rgb(110, 114, 122)',
      display: 'grid',
      fontFamily: '"Instrument Sans", system-ui, sans-serif',
      trademarkBorderTopColor: 'rgb(214, 211, 200)',
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

    await page.goto(`${origin}/demo/ixbrl-viewer/ixbrlviewer.html`, { waitUntil: 'networkidle0' })
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
