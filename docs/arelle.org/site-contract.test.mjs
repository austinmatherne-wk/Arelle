import assert from 'node:assert/strict'
import { readFile, stat } from 'node:fs/promises'
import { test } from 'node:test'

const output = new URL('./public/', import.meta.url)
const externalMarker = /<span class=(?:"external-link-marker"|external-link-marker) aria-hidden=(?:"true"|true)>↗<\/span>/

async function page(path) {
  return readFile(new URL(path, output), 'utf8')
}

function element(html, tag, className) {
  const match = html.match(new RegExp(`<${tag}[^>]*class=(?:"${className}"|${className})(?:\\s|>)[\\s\\S]*?</${tag}>`))
  assert.ok(match, `expected ${tag}.${className}`)
  return match[0]
}

function attribute(tag, name) {
  return tag.match(new RegExp(`\\b${name}=(?:"([^"]+)"|([^\\s>]+))`))?.slice(1).find(Boolean)
}

function visibleText(html) {
  return html
    .replace(/<span[^>]*aria-hidden=(?:"true"|true)[^>]*>[\s\S]*?<\/span>/g, '')
    .replace(/<img\b([^>]*)>/g, (_, attributes) => attribute(attributes, 'alt') ?? '')
    .replace(/<[^>]+>/g, '')
    .trim()
}

function links(html) {
  return [...html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/g)].map((match) => ({
    attributes: match[1],
    content: match[2],
    href: attribute(match[1], 'href'),
    text: visibleText(match[2]),
  }))
}

function images(html) {
  return [...html.matchAll(/<img\b([^>]*)>/g)].map((match) => ({
    alt: attribute(match[1], 'alt'),
    src: attribute(match[1], 'src'),
  }))
}

function inlineBytes(src, mediaType) {
  const prefix = `data:${mediaType};base64,`
  assert.ok(src.startsWith(prefix), `expected an inline ${mediaType}, got ${src.slice(0, 40)}`)
  return Buffer.from(src.slice(prefix.length), 'base64')
}

function assertPng(bytes, label) {
  assert.equal(bytes.subarray(0, 8).toString('hex'), '89504e470d0a1a0a', `${label} is not a PNG`)
}

function assertWebp(bytes, label) {
  assert.equal(bytes.subarray(0, 4).toString(), 'RIFF', `${label} is not a WebP`)
  assert.equal(bytes.subarray(8, 12).toString(), 'WEBP', `${label} is not a WebP`)
}

function canonical(html) {
  const tag = html.match(/<link\b[^>]*rel=(?:"canonical"|canonical)[^>]*>/)?.[0]
  assert.ok(tag, 'expected a canonical link')
  return attribute(tag, 'href')
}

function refresh(html) {
  const tag = html.match(/<meta\b[^>]*http-equiv=(?:"refresh"|refresh)[^>]*>/)?.[0]
  assert.ok(tag, 'expected a refresh redirect')
  return attribute(tag, 'content')
}

test('primary navigation exposes the final supporting destinations', async () => {
  const primary = element(await page('index.html'), 'nav', 'primary-navigation')
  const primaryLinks = links(primary)
  assert.deepEqual(
    primaryLinks.map(({ href, text }) => [text, href]),
    [
      ['Arelle', '/'],
      ['Download', '/download/'],
      ['Updates', '/blog/'],
      ['Docs', 'https://arelle.readthedocs.io/'],
      ['GitHub', 'https://github.com/Arelle/Arelle'],
    ],
  )
  assert.deepEqual(
    primaryLinks.filter(({ content }) => externalMarker.test(content)).map(({ text }) => text),
    ['Docs', 'GitHub'],
  )
})

test('footer keeps community, legal, and trademark links in the shared shell', async () => {
  const footer = element(await page('index.html'), 'footer', 'site-footer')
  assert.deepEqual(
    links(element(footer, 'nav', 'footer-navigation')).map(({ href, text }) => [text, href]),
    [
      ['About', '/about/'],
      ['Community', 'https://groups.google.com/d/forum/arelle-users'],
      ['Contribute', 'https://arelle.readthedocs.io/en/latest/contributor_guides/contributing.html'],
      ['Contact', 'mailto:support@arelle.org'],
    ],
  )
  assert.match(footer, /(?:©|&copy;) \d{4} Workiva Inc\./)
  assert.match(footer, /https:\/\/www\.workiva\.com\/privacy-policy/)
  assert.match(
    footer,
    /XBRL™ is a trademark of XBRL International, Inc\. All rights reserved\. The XBRL™ standards are open and freely licensed by way of the XBRL International License Agreement\. Our use of these trademarks is permitted by XBRL International in accordance with the XBRL International Trademark Policy\./,
  )
})

test('Download offers focused desktop and integrator installation paths', async () => {
  const html = await page('download/index.html')
  const table = html.match(/<table\b[^>]*>[\s\S]*?<\/table>/)?.[0]
  assert.ok(table, 'expected a semantic builds table')
  assert.deepEqual(
    [...table.matchAll(/<th\b[^>]*>([\s\S]*?)<\/th>/g)].map((match) => visibleText(match[1])),
    ['Build', 'Mirrors'],
  )

  const builds = [
    ['Windows 64-bit installer', 'arelle-win.exe'],
    ['Windows 64-bit zip', 'arelle-win.zip'],
    ['macOS for Apple silicon', 'arelle-macos-arm64.dmg'],
    ['macOS for Intel', 'arelle-macos-x64.dmg'],
    ['Ubuntu Linux', 'arelle-ubuntu.tgz'],
  ]
  const mirrors = [
    ['US', 'https://arelle-us.s3-us-west-1.amazonaws.com/'],
    ['Europe', 'https://arelle-eu.s3.eu-central-1.amazonaws.com/'],
    ['Mainland China', 'https://arelle-cn.oss-cn-shenzhen.aliyuncs.com/'],
  ]
  const body = table.match(/<tbody\b[^>]*>([\s\S]*?)<\/tbody>/)?.[1]
  assert.ok(body, 'expected the builds inside a table body')
  const rows = [...body.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/g)].map((match) => match[1])
  assert.equal(rows.length, builds.length)
  builds.forEach(([build, artifact], index) => {
    const cells = [...rows[index].matchAll(/<td\b[^>]*>([\s\S]*?)<\/td>/g)]
    assert.equal(cells.length, 2)
    assert.equal(visibleText(cells[0][1]), build)
    assert.deepEqual(
      links(cells[1][1]).map(({ href, text }) => [text, href]),
      mirrors.map(([mirror, base]) => [mirror, `${base}${artifact}`]),
    )
  })
  assert.match(html, /Choose the mirror closest to you\. Each mirror serves the same current release\./)

  const commands = [
    ...html.matchAll(/<code\b[^>]*class=(?:"language-shell"|language-shell)[^>]*>([\s\S]*?)<\/code>/g),
  ].map((match) =>
    visibleText(match[1])
      .replace(/(?:&#34;|&quot;)/g, '"')
      .replace(/\s+/g, ' '),
  )
  assert.deepEqual(commands, [
    'pip install arelle-release',
    'docker run --rm -v "$PWD:/data" arelleproject/arelle:latest \\ python arelleCmdLine.py --file /data/filing.zip --validate',
    'docker run --name arelle-webserver -p 8080:8080 \\ arelleproject/arelle:latest /opt/start.sh',
  ])

  const hrefs = links(html).map(({ href }) => href)
  assert.ok(hrefs.includes('https://arelle.readthedocs.io/en/latest/install.html'))
  assert.ok(hrefs.includes('https://arelle.readthedocs.io/en/latest/install.html#docker'))
  assert.ok(hrefs.includes('https://github.com/Arelle/Arelle/releases'))
  assert.doesNotMatch(html, /archive-index|EDGAR Renderer|ContributorLicenseFor/i)
})

test('About uses the settled copy and only the historical Participate alias', async () => {
  const html = await page('about/index.html')
  for (const heading of ['About Arelle', 'Mission', 'Stewardship', 'Get involved']) {
    assert.match(html, new RegExp(`>${heading}</h[12]>`))
  }
  assert.match(html, /Created in 2010/)
  assert.match(html, /Apache License 2\.0/)
  assert.match(html, /Workiva holds the\s+project(?:'|&#39;|&rsquo;)s copyright/)
  assert.doesNotMatch(html, /over 50 regulators|fund(?:ed|ing)|governance/i)

  const redirect = await page('arelle/participate/index.html')
  assert.equal(refresh(redirect), `0; url=${canonical(html)}`)
  await assert.rejects(stat(new URL('participate/index.html', output)), { code: 'ENOENT' })
})

test('Documentation is a pinned redirect to Read the Docs', async () => {
  const html = await page('documentation/index.html')
  assert.equal(refresh(html), '0; url=https://arelle.readthedocs.io/')
  assert.equal(canonical(html), 'https://arelle.readthedocs.io/')
  assert.deepEqual(
    links(html).map(({ href, text }) => [text, href]),
    [['Read the Docs', 'https://arelle.readthedocs.io/']],
  )
})

test('404 page reports the missing page through the shared site shell', async () => {
  const html = await page('404.html')
  assert.match(html, /<h1[^>]*>Page not found\.<\/h1>/)
  assert.equal(
    visibleText(element(html, 'p', 'not-found-error')),
    '[arelle.4.0.4.notFound] The requested page could not be found.',
  )
  assert.equal(visibleText(element(html, 'p', 'not-found-summary')), 'Validation completed with 1 error.')
  assert.match(html, /<header class=(?:"site-header"|site-header)>/)
  assert.match(html, /<footer class=(?:"site-footer"|site-footer)>/)

  const main = html.match(/<main\b[^>]*>([\s\S]*?)<\/main>/)?.[1]
  assert.ok(main, 'expected 404 content inside the main landmark')
  assert.equal(links(main).length, 0)
  assert.doesNotMatch(main, /requested-url|location\.|document\.URL|<img\b|<svg\b/i)
})

test('legacy EDGAR pages keep routes and production image delivery', async () => {
  const legacyRoutes = [
    'arelle/pub/applications/',
    'arelle/pub/edgar-renderer-installation/',
    'arelle/documentation/edgar-renderer-technical-operation/',
  ]
  for (const route of legacyRoutes) {
    const html = await page(`${route}index.html`)
    assert.match(html, /<header class=(?:"site-header"|site-header)>/)
    assert.match(html, /<footer class=(?:"site-footer"|site-footer)>/)
    const primaryTargets = links(element(html, 'nav', 'primary-navigation')).map(({ href }) => href)
    assert.ok(!primaryTargets.includes(`/${route}`), `${route} should remain outside primary navigation`)
  }

  const sitemap = await page('sitemap.xml')
  for (const route of legacyRoutes) {
    assert.ok(!sitemap.includes(route), `${route} should stay out of the sitemap`)
  }

  const installationImages = images(await page('arelle/pub/edgar-renderer-installation/index.html'))
  const expectedImages = new Map([
    ['start Edgar Renderer Windows', 'inline-webp'],
    ['start Edgar Renderer Mac', 'inline-webp'],
    ['check menu selection for disclosure system validation', 'inline-webp'],
    ['manage plugins', 'requested-webp'],
    ['select Edgar Renderer', 'requested-webp'],
    ['allow to restart', 'requested-webp'],
    ['select NTLM proxy plugin', 'requested-webp'],
    ['select disclosure system', 'requested-webp'],
    ['select EDGAR Filer Manual validation mode', 'requested-webp'],
    ['inline ix viewer', 'requested-webp'],
    ['open file toolbar button', 'inline-png'],
    ['validate toolbar button', 'inline-png'],
  ])
  assert.equal(installationImages.length, expectedImages.size)

  for (const { alt, src } of installationImages) {
    assert.ok(alt, 'every legacy image should retain alt text')
    assert.ok(src, `${alt} should have a source`)
    const delivery = expectedImages.get(alt)
    assert.ok(delivery, `unexpected legacy image: ${alt}`)
    if (delivery === 'inline-png') {
      assertPng(inlineBytes(src, 'image/png'), alt)
    } else if (delivery === 'inline-webp') {
      assertWebp(inlineBytes(src, 'image/webp'), alt)
    } else {
      assert.match(src, /^\/images\/[^/]+\.webp$/)
      const bytes = await readFile(new URL(src.slice(1), output))
      assertWebp(bytes, src)
    }
  }
})
