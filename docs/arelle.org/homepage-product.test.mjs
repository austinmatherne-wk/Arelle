import assert from 'node:assert/strict'
import { access, readFile } from 'node:fs/promises'
import { createServer } from 'node:http'
import { extname, join, normalize } from 'node:path'
import { after, before, test } from 'node:test'
import { fileURLToPath } from 'node:url'

import puppeteer from 'puppeteer-core'

const output = fileURLToPath(new URL('./public/', import.meta.url))
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
  ['.avif', 'image/avif'],
  ['.css', 'text/css'],
  ['.html', 'text/html'],
  ['.ico', 'image/x-icon'],
  ['.js', 'text/javascript'],
  ['.png', 'image/png'],
  ['.svg', 'image/svg+xml'],
  ['.webp', 'image/webp'],
  ['.woff2', 'font/woff2'],
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
  throw new Error('Chrome was not found; set CHROME_PATH to run homepage product checks')
}

async function artifact(request, response) {
  const requestedPath = decodeURIComponent(new URL(request.url, 'http://localhost').pathname)
  const relativePath = requestedPath.endsWith('/') ? `${requestedPath}index.html` : requestedPath
  const filePath = join(output, normalize(relativePath).replace(/^(\.\.(\/|\\|$))+/, ''))

  try {
    const body = await readFile(filePath)
    response.writeHead(200, {
      'content-type': contentTypes.get(extname(filePath)) ?? 'application/octet-stream',
    })
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

async function withPage(scheme, callback) {
  const { context, page } = await pageFor(scheme)
  try {
    return await callback(page)
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

test('homepage tabs progressively enhance mouse and keyboard input', async () => {
  await withPage('light', async (page) => {
    await page.setViewport({ width: 320, height: 900 })
    await page.goto(origin, { waitUntil: 'networkidle0' })

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

    assert.deepEqual(
      await state(),
      {
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
      },
    )

    const originalUrl = page.url()
    await page.click('#tab-cli')
    assert.equal(page.url(), originalUrl)
    assert.equal((await state()).tabs.find((tab) => tab.focused).id, 'tab-cli')
    assert.equal((await state()).panels.find((panel) => panel.id === 'panel-cli').hidden, false)

    for (const [key, expected] of [
      ['ArrowRight', 'tab-python'],
      ['ArrowRight', 'tab-docker'],
      ['ArrowRight', 'tab-plugin'],
      ['ArrowRight', 'tab-gui'],
      ['ArrowLeft', 'tab-plugin'],
      ['Home', 'tab-gui'],
      ['End', 'tab-plugin'],
    ]) {
      await page.keyboard.press(key)
      assert.equal((await state()).tabs.find((tab) => tab.focused).id, expected)
      assert.equal(
        (await state()).panels.find((panel) => panel.id === expected.replace('tab-', 'panel-')).hidden,
        false,
      )
    }

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
  })
})

test('homepage panels remain in document order without JavaScript', async () => {
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
      products.map((product) => ({
        id: `panel-${product}`,
        display: 'block',
        hidden: false,
      })),
    )
    assert.equal(
      await page.$eval('[role="tablist"]', (tablist) => getComputedStyle(tablist).display),
      'none',
    )
  } finally {
    await context.close()
  }
})

test('homepage tab relationships and GUI captures follow the effective theme', async () => {
  for (const scheme of ['light', 'dark']) {
    await withPage(scheme, async (page) => {
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

      const captureDisplay = () => page.evaluate(() => ({
        light: getComputedStyle(document.querySelector('.shot-light')).display,
        dark: getComputedStyle(document.querySelector('.shot-dark')).display,
      }))
      assert.deepEqual(
        await captureDisplay(),
        scheme === 'dark' ? { light: 'none', dark: 'block' } : { light: 'block', dark: 'none' },
      )

      await page.click('[data-theme-toggle]')
      assert.deepEqual(
        await captureDisplay(),
        scheme === 'dark' ? { light: 'block', dark: 'none' } : { light: 'none', dark: 'block' },
      )
    })
  }
})

test('homepage remains usable at 320 pixels without page overflow', async () => {
  await withPage('light', async (page) => {
    await page.setViewport({ width: 320, height: 900 })
    await page.goto(origin, { waitUntil: 'networkidle0' })

    const layout = await page.evaluate(() => {
      const viewportWidth = document.documentElement.clientWidth
      const tablist = document.querySelector('[role="tablist"]')
      const setup = document.querySelector('.product-setup')
      const fitsViewport = (element) => {
        const { left, right } = element.getBoundingClientRect()
        return left >= -1 && right <= viewportWidth + 1
      }
      return {
        pageOverflow: document.documentElement.scrollWidth > viewportWidth,
        tabsFit: fitsViewport(tablist),
        tabsScroll: tablist.scrollWidth > tablist.clientWidth,
        setupStacked: getComputedStyle(setup).flexDirection === 'column',
      }
    })

    assert.deepEqual(layout, {
      pageOverflow: false,
      tabsFit: true,
      tabsScroll: true,
      setupStacked: true,
    })

    for (const product of products) {
      await page.click(`#tab-${product}`)
      const selectedPanel = await page.evaluate(() => {
        const viewportWidth = document.documentElement.clientWidth
        const tablist = document.querySelector('[role="tablist"]')
        const selectedTab = tablist.querySelector('[aria-selected="true"]').getBoundingClientRect()
        const tablistBounds = tablist.getBoundingClientRect()
        const panel = document.querySelector('[role="tabpanel"]:not([hidden])')
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
