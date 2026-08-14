import { execFile } from 'node:child_process'
import assert from 'node:assert/strict'
import { mkdtemp, readFile, readdir, rm, stat } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { promisify } from 'node:util'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'

const output = new URL('./public/', import.meta.url)
const siteRoot = fileURLToPath(new URL('.', import.meta.url))
const execFileAsync = promisify(execFile)
const viewerRoute = 'demo/ixbrl-viewer/'
const themeControllerByteCap = 1152 // 1.125 KiB
const latestReleaseURL = 'https://github.com/Arelle/Arelle/releases/latest'

async function page(path) {
  return readFile(new URL(path, output), 'utf8')
}

function element(html, tag, className) {
  const match = html.match(new RegExp(`<${tag}[^>]*class=(?:"[^"]*\\b${className}\\b[^"]*"|${className})(?:\\s|>)[\\s\\S]*?</${tag}>`))
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

function decodeHtmlEntities(text) {
  return text
    .replaceAll('&#34;', '"')
    .replaceAll('&quot;', '"')
    .replaceAll('&#39;', "'")
    .replaceAll('&apos;', "'")
    .replaceAll('&gt;', '>')
    .replaceAll('&lt;', '<')
    .replaceAll('&amp;', '&')
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

function scripts(html) {
  return [...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)]
}

async function readTranscript(path) {
  return (await readFile(new URL(path, import.meta.url), 'utf8'))
    .trimEnd()
    .split(/\r?\n/)
}

function transcriptParts(transcript) {
  const commandLines = []
  let outputStart = 0
  while (outputStart < transcript.length) {
    const line = transcript[outputStart++]
    commandLines.push(line)
    if (!line.endsWith('\\')) break
  }
  return {
    command: commandLines.join('\n'),
    output: transcript.slice(outputStart).join('\n'),
  }
}

function productPanels(comparison) {
  const starts = [...comparison.matchAll(
    /<div\b([^>]*\bid=(?:"panel-(?:gui|cli|docker|python|plugin|webserver)"|panel-(?:gui|cli|docker|python|plugin|webserver))[^>]*)>/g,
  )]
  return starts.map((match, index) => {
    const end = starts[index + 1]?.index ?? comparison.search(/<\/div>\s*<\/div>\s*<\/section>/)
    return [match[0], match[1], comparison.slice(match.index + match[0].length, end !== -1 ? end : undefined)]
  })
}

function codeBlocks(html) {
  return [...html.matchAll(/<pre\b[^>]*>([\s\S]*?)<\/pre>/g)]
    .map(([, content]) => decodeHtmlEntities(visibleText(content)))
}

function exampleOutputLabels(html) {
  return [...html.matchAll(
    /<div\b[^>]*class=(?:"[^"]*\bexample-output-heading\b[^"]*"|example-output-heading)[^>]*>([\s\S]*?)<\/div>/g,
  )].map(([, content]) => visibleText(content).toLowerCase())
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

test('primary navigation exposes direct destinations in the settled order', async () => {
  const html = await page('index.html')
  const primary = element(html, 'nav', 'primary-navigation')
  const primaryLinks = links(primary)
  assert.deepEqual(
    primaryLinks.map(({ href, text }) => [text, href]),
    [
      ['Arelle', '/'],
      ['Download', '/download/'],
      ['Updates', '/updates/'],
      ['Docs', 'https://arelle.readthedocs.io/'],
      ['GitHub', 'https://github.com/Arelle/Arelle'],
    ],
  )
  assert.doesNotMatch(primary, /<img/i)

  const destinations = primary.match(/<ul\b[^>]*>[\s\S]*?<\/ul>/)?.[0]
  assert.ok(destinations, 'expected a destination list in primary navigation')
  assert.doesNotMatch(destinations, /data-theme-toggle/)
  assert.match(primary, /data-theme-toggle/)
})

test('current internal navigation destinations identify the page', async () => {
  const home = element(await page('index.html'), 'nav', 'primary-navigation')
  const currentHome = links(home).find(({ text }) => text === 'Arelle')
  assert.match(currentHome.attributes, /\baria-current=(?:"page"|page)/)

  const download = element(await page('download/index.html'), 'nav', 'primary-navigation')
  const currentDownload = links(download).find(({ text }) => text === 'Download')
  assert.match(currentDownload.attributes, /\baria-current=(?:"page"|page)/)

  const about = element(await page('about/index.html'), 'nav', 'footer-navigation')
  const currentAbout = links(about).find(({ text }) => text === 'About')
  assert.match(currentAbout.attributes, /\baria-current=(?:"page"|page)/)
})

test('Download offers focused desktop, container, package, and plugin installation paths', async () => {
  const html = await page('download/index.html')
  assert.match(html, /<h1[^>]*>Arelle Distributions<\/h1>/)

  const table = html.match(/<table\b[^>]*>[\s\S]*?<\/table>/)?.[0]
  assert.ok(table, 'expected a semantic distributions table')
  assert.match(table, /<thead\b/)
  assert.deepEqual(
    [...table.matchAll(/<th\b[^>]*>([\s\S]*?)<\/th>/g)].map((match) => visibleText(match[1])),
    ['Distribution', 'Format', 'Download / Install Command', 'Mirrors / Options'],
  )

  const builds = [
    ['Windows 64-bit Installer', 'arelle-win.exe'],
    ['Windows 64-bit Portable', 'arelle-win.zip'],
    ['macOS Apple Silicon', 'arelle-macos-arm64.dmg'],
    ['macOS Intel x64', 'arelle-macos-x64.dmg'],
    ['Ubuntu / Debian Linux', 'arelle-ubuntu.tgz'],
  ]
  const mirrors = [
    ['US', 'https://arelle-us.s3-us-west-1.amazonaws.com/'],
    ['EU', 'https://arelle-eu.s3.eu-central-1.amazonaws.com/'],
    ['CN', 'https://arelle-cn.oss-cn-shenzhen.aliyuncs.com/'],
  ]

  for (const [name, mirrorAsset] of builds) {
    assert.match(html, new RegExp(name))
    for (const [mirrorLabel, mirrorBase] of mirrors) {
      assert.match(html, new RegExp(`${mirrorBase}${mirrorAsset}`))
    }
  }

  const versionPill = element(html, 'div', 'download-version-pill')
  assert.equal(
    visibleText(versionPill.match(/<strong[^>]*>[\s\S]*?<\/strong>/)?.[0]),
    'Latest',
  )

  assert.match(html, /docker pull arelleproject\/arelle:latest/)
  assert.match(html, /docker pull ghcr\.io\/arelle\/arelle:latest/)
  assert.match(html, /docker pull arelleproject\/arelle:latest-slim/)
  assert.match(html, /docker pull ghcr\.io\/arelle\/arelle:latest-slim/)
  assert.match(html, /pip install arelle-release/)
  assert.match(html, /git clone https:\/\/github\.com\/Arelle\/Arelle\.git/)

  const downloadLinks = links(html)
  const releaseNotes = downloadLinks.find(({ attributes }) => /\bdownload-changelog-link\b/.test(attribute(attributes, 'class') ?? ''))
  assert.equal(releaseNotes?.href, latestReleaseURL)
  assert.match(releaseNotes?.text, /Release Notes/)
  assert.deepEqual(
    downloadLinks
      .filter(({ attributes }) => /\bdownload-direct-link\b/.test(attribute(attributes, 'class') ?? ''))
      .map(({ href, text }) => [text, href]),
    builds.map(([name]) => ['GitHub Release', latestReleaseURL]),
  )

  assert.ok(downloadLinks.some(({ href }) => href === 'https://github.com/Arelle/ixbrl-viewer'))
  assert.ok(downloadLinks.some(({ href }) => href === 'https://github.com/xbrlus/xule'))
  assert.ok(downloadLinks.some(({ href }) => href === 'https://github.com/arelle/edgar'))
  assert.ok(downloadLinks.some(({ href }) => href === 'https://arelle.readthedocs.io/en/latest/install.html'))

  assert.doesNotMatch(
    html,
    /archive-index|EDGAR Renderer|<h2[^>]*>(?:Source|Support|Contribution|License|Copyright and trademark)<\/h2>|ContributorLicenseFor/i,
  )
})

test('Download interpolates a release version into desktop GitHub assets', async (t) => {
  try {
    await execFileAsync('hugo', ['version'], { cwd: siteRoot })
  } catch (error) {
    if (error?.code === 'ENOENT') {
      if (process.env.CI) {
        assert.fail('hugo must be available in CI to verify versioned download links')
      }
      t.skip('hugo is not available; skipping the versioned download compile')
      return
    }
    throw error
  }

  const destination = await mkdtemp(join(tmpdir(), 'arelle-download-contract-'))
  try {
    await execFileAsync(
      'hugo',
      ['--minify', '--destination', destination],
      {
        cwd: siteRoot,
        env: {
          ...process.env,
          HUGO_PARAMS_downloadVersion: '9.9.9',
        },
      },
    )
    const html = await readFile(join(destination, 'download/index.html'), 'utf8')
    const table = html.match(/<table\b[^>]*>[\s\S]*?<\/table>/)?.[0]
    assert.ok(table, 'expected a semantic distributions table')
    assert.deepEqual(
      [...table.matchAll(/<th\b[^>]*>([\s\S]*?)<\/th>/g)].map((match) => visibleText(match[1])),
      ['Distribution', 'Format', 'Download / Install Command', 'Mirrors / Options'],
    )

    const builds = [
      ['Windows 64-bit Installer', 'arelle-win-9.9.9.exe', 'arelle-win.exe'],
      ['Windows 64-bit Portable', 'arelle-win-9.9.9.zip', 'arelle-win.zip'],
      ['macOS Apple Silicon', 'arelle-macos-arm64-9.9.9.dmg', 'arelle-macos-arm64.dmg'],
      ['macOS Intel x64', 'arelle-macos-x64-9.9.9.dmg', 'arelle-macos-x64.dmg'],
      ['Ubuntu / Debian Linux', 'arelle-ubuntu-9.9.9.tgz', 'arelle-ubuntu.tgz'],
    ]
    const mirrors = [
      ['US', 'https://arelle-us.s3-us-west-1.amazonaws.com/'],
      ['EU', 'https://arelle-eu.s3.eu-central-1.amazonaws.com/'],
      ['CN', 'https://arelle-cn.oss-cn-shenzhen.aliyuncs.com/'],
    ]

    for (const [name, ghAsset, mirrorAsset] of builds) {
      assert.match(html, new RegExp(name))
      assert.match(html, new RegExp(`https://github\\.com/Arelle/Arelle/releases/download/9\\.9\\.9/${ghAsset}`))
      for (const [mirrorLabel, mirrorBase] of mirrors) {
        assert.match(html, new RegExp(`${mirrorBase}${mirrorAsset}`))
      }
    }

    const versionPill = element(html, 'div', 'download-version-pill')
    assert.equal(
      visibleText(versionPill.match(/<strong[^>]*>[\s\S]*?<\/strong>/)?.[0]),
      'v9.9.9',
    )
    const downloadLinks = links(html)
    const releaseNotes = downloadLinks.find(({ attributes }) => /\bdownload-changelog-link\b/.test(attribute(attributes, 'class') ?? ''))
    assert.equal(releaseNotes?.href, 'https://github.com/Arelle/Arelle/releases/tag/9.9.9')
    assert.match(releaseNotes?.text, /Release Notes/)
    assert.deepEqual(
      downloadLinks
        .filter(({ attributes }) => /\bdownload-direct-link\b/.test(attribute(attributes, 'class') ?? ''))
        .map(({ href, text }) => [text, href]),
      builds.map(([, ghAsset]) => [
        'GitHub Release',
        `https://github.com/Arelle/Arelle/releases/download/9.9.9/${ghAsset}`,
      ]),
    )
  } finally {
    await rm(destination, { recursive: true, force: true })
  }
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

test('legacy EDGAR pages keep the shared shell outside active navigation', async () => {
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
})

test('404 page reports the missing page through the shared site shell', async () => {
  const html = await page('404.html')
  assert.match(html, /<h1[^>]*>Page not found<\/h1>/)
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

  const pageScripts = scripts(html)
  assert.equal(pageScripts.length, 1)
  const [, attributes] = pageScripts[0]
  assert.match(attributes, /\bdata-theme-controller\b/)
  assert.doesNotMatch(main, /requested-url|location\.|document\.URL|<img\b|<svg\b/i)
})

test('legacy EDGAR images use the production formats and request split', async () => {
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

test('Project updates exposes complete yearly archives and connected posts', async () => {
  const archive = await page('updates/index.html')
  assert.match(archive, /<h1[^>]*>Project updates<\/h1>/)

  const yearNavigation = element(archive, 'nav', 'update-year-navigation')
  assert.deepEqual(
    links(yearNavigation).map(({ href, text }) => [text, href]),
    [
      ['2026', '/updates/2026/'],
      ['2025', '/updates/2025/'],
      ['2024', '/updates/2024/'],
    ],
  )
  assert.match(links(yearNavigation)[0].attributes, /\baria-current=(?:"page"|page)/)
  assert.equal(
    [...archive.matchAll(/<article\b[^>]*class=(?:"update-entry"|update-entry)[^>]*>/g)].length,
    6,
    'the archive defaults to the complete latest year',
  )

  const expectedYears = new Map([
    ['updates/2026/index.html', { year: '2026', entries: 6 }],
    ['updates/2025/index.html', { year: '2025', entries: 12 }],
    ['updates/2024/index.html', { year: '2024', entries: 11 }],
  ])
  for (const [path, expected] of expectedYears) {
    const html = await page(path)
    assert.match(html, new RegExp(`<section class=(?:"update-year"|update-year) aria-label=(?:"${expected.year}"|${expected.year})>`))
    assert.match(html, new RegExp(`<title>Project updates: ${expected.year} · Arelle</title>`))
    assert.match(html, /<meta name=(?:"description"|description) content="Updates from the Arelle team\.">/)
    const entries = [...html.matchAll(/<article\b[^>]*class=(?:"update-entry"|update-entry)[^>]*>([\s\S]*?)<\/article>/g)]
    assert.equal(entries.length, expected.entries, `${path} should contain one complete year`)
    for (const [, entry] of entries) {
      const time = entry.match(/<time\b[^>]*>/)?.[0]
      assert.ok(time, 'expected a machine-readable date')
      assert.match(attribute(time, 'datetime'), new RegExp(`^${expected.year}-\\d{2}-\\d{2}$`))
      assert.match(entry, /<h3\b[^>]*><a\b[^>]*>[^<]+<\/a><\/h3>/)
      assert.match(entry, /<p\b[^>]*class=(?:"update-summary"|update-summary)[^>]*>\S/)
    }
  }
  assert.match(archive, /July(?:'|&#39;|&rsquo;)s releases improved validation and conformance coverage/)

  assert.match(archive, /<link rel=(?:"alternate"|alternate) type=(?:"application\/rss\+xml"|application\/rss\+xml) href=(?:"[^"]*\/updates\/index\.xml"|[^ >]*\/updates\/index\.xml)/)
  assert.doesNotMatch(await page('index.html'), /<link rel=alternate type=application\/rss\+xml/)

  const feed = await page('updates/index.xml')
  const feedTitles = [...feed.matchAll(/<item>[\s\S]*?<title>([\s\S]*?)<\/title>/g)].map((match) => match[1])
  assert.equal(
    feedTitles.length,
    [...expectedYears.values()].reduce((total, { entries }) => total + entries, 0),
    'the feed carries every update, not only those of the default year',
  )
  assert.equal(feedTitles[0], 'July 2026 Update')

  const latest = await page('updates/2026/07/31/july-2026-update/index.html')
  const currentUpdates = links(element(latest, 'nav', 'primary-navigation')).find(({ text }) => text === 'Updates')
  assert.match(currentUpdates.attributes, /\baria-current=(?:"page"|page)/)
  assert.match(latest, /<a[^>]*class=(?:"update-archive-label"|update-archive-label)[^>]*>Arelle updates<\/a>/)
  assert.match(latest, /<h1[^>]*>July 2026 Update<\/h1>/)
  assert.match(
    element(latest, 'p', 'update-deck'),
    /July(?:'|&#39;|&rsquo;)s releases improved validation and conformance coverage, and arelle\.org has a new design\./,
  )
  assert.doesNotMatch(latest, /<link rel=alternate type=application\/rss\+xml/)
  assert.match(latest, /<h2[^>]*>Validation and conformance<\/h2>/)
  assert.match(latest, /<h2[^>]*>A new home for Arelle<\/h2>/)
  assert.doesNotMatch(latest, /ReadTheDocs (?:has been|was) redesigned|Viewer is mobile-friendly|every supported specification is certified/i)

  const feedNotice = links(latest).find(({ text }) => text === 'canonical Project updates RSS feed')
  assert.equal(feedNotice?.href, '/updates/index.xml')
  assert.match(latest, /<code>\/arelle\/feed\/<\/code>[^.]*is no longer a feed/)

  const postNavigation = element(
    await page('updates/2026/03/27/march-2026/index.html'),
    'nav',
    'update-post-navigation',
  )
  assert.deepEqual(
    links(postNavigation).map(({ href, text }) => [text, href]),
    [
      ['Previous February 2026 Update', '/updates/2026/02/27/february-2026-update/'],
      ['Next April 2026 Update', '/updates/2026/04/24/april-2026-update/'],
    ],
  )

  assert.deepEqual(
    links(element(latest, 'nav', 'update-post-navigation')).map(({ href, text }) => [text, href]),
    [
      ['Previous June 2026 Update', '/updates/2026/06/26/june-2026-update/'],
    ],
  )
  const oldest = await page('updates/2024/01/26/january-2024-update/index.html')
  assert.deepEqual(
    links(element(oldest, 'nav', 'update-post-navigation')).map(({ href, text }) => [text, href]),
    [
      ['Next February 2024 Update', '/updates/2024/02/27/february-2024-update/'],
    ],
  )
})

test('footer contains community, legal, and verbatim trademark content', async () => {
  const html = await page('index.html')
  const footer = element(html, 'footer', 'site-footer')
  assert.deepEqual(
    links(element(footer, 'nav', 'footer-navigation')).map(({ href, text }) => [text, href]),
    [
      ['About', '/about/'],
      ['Community', 'https://groups.google.com/g/arelle-users'],
      ['Contribute', 'https://arelle.readthedocs.io/en/latest/contributor_guides/contributing.html'],
      ['Contact', 'mailto:support@arelle.org'],
    ],
  )
  assert.match(footer, /(?:©|&copy;) \d{4} Workiva Inc\./)
  assert.match(footer, /https:\/\/www\.workiva\.com\/legal\/workiva-privacy-policy/)
  assert.match(
    footer,
    /XBRL™ is a trademark of XBRL International, Inc\. All rights reserved\. The XBRL™ standards are open and freely licensed by way of the XBRL International License Agreement\. Our use of these trademarks is permitted by XBRL International in accordance with the XBRL International Trademark Policy\./,
  )
})

test('shared visual foundation serves only the approved font faces from the site', async () => {
  const html = await page('index.html')
  const css = html.match(/<style\b[^>]*data-fonts[^>]*>([\s\S]*?)<\/style>/)?.[1]
  assert.ok(css, 'expected inline self-hosted font declarations')
  const faces = [...css.matchAll(/@font-face\s*\{([^}]+)\}/g)].map(([, declarations]) => {
    const value = (property) => declarations
      .match(new RegExp(`${property}\\s*:\\s*([^;]+)`))?.[1]
      .trim()
      .replaceAll('"', '')
    return {
      family: value('font-family').toLowerCase(),
      source: declarations.match(/src\s*:\s*url\((?:"([^"]+)"|([^)]+))\)/)?.slice(1).find(Boolean),
      style: value('font-style'),
      weight: value('font-weight'),
    }
  })

  assert.deepEqual(faces.map(({ source, ...face }) => face), [
    { family: 'instrument sans', style: 'normal', weight: '400 700' },
    { family: 'dm mono', style: 'normal', weight: '400' },
    { family: 'martian mono', style: 'normal', weight: '600' },
  ])
  for (const { family, source } of faces) {
    if (family !== 'martian mono') {
      assert.match(source, /^data:font\/woff2;base64,/)
      const bytes = Buffer.from(source.slice('data:font/woff2;base64,'.length), 'base64')
      assert.equal(bytes.subarray(0, 4).toString(), 'wOF2', `inlined ${family} is not WOFF2`)
      continue
    }
    assert.match(source, /^\/(?:css|fonts)\/[^/]+\.woff2$/)
    const bytes = await readFile(new URL(source.slice(1), output))
    assert.equal(bytes.subarray(0, 4).toString(), 'wOF2', `${source} is not WOFF2`)
  }
  assert.doesNotMatch(css, /url\(["']?https?:/)
  assert.doesNotMatch(await page('css/main.css'), /url\(["']?https?:/)
})

test('theme control is action-labelled and its only controller stays under 1.125 KiB', async () => {
  const html = await page('index.html')
  const pageScripts = scripts(html)
  assert.equal(pageScripts.length, 1)
  const [, attributes, controller] = pageScripts[0]
  assert.match(attributes, /\bdata-theme-controller\b/)
  assert.ok(Buffer.byteLength(controller) <= themeControllerByteCap)
  assert.match(controller, /ixbrl-viewer-theme/)

  const button = html.match(/<button[^>]*data-theme-toggle[^>]*>[\s\S]*?<\/button>/)?.[0]
  assert.ok(button)
  assert.match(button, /\baria-label="Switch to dark"/)
  assert.match(button, /\btitle="Switch to dark"/)
  assert.equal(visibleText(button.replace(/<svg[\s\S]*?<\/svg>/g, '')), '')

  const files = await readdir(output, { recursive: true })
  for (const file of files.filter((file) => file.endsWith('.html') && !file.startsWith('demo/'))) {
    const fileScripts = scripts(await page(file))
    assert.ok(fileScripts.length <= 1, `${file} contains an additional script`)
    for (const [tag, pageAttributes] of fileScripts) {
      assert.match(pageAttributes, /\bdata-theme-controller\b/, `${file} contains a non-theme script: ${tag}`)
    }
  }
})

test('homepage opening presents the product, actions, and three distinct proofs', async () => {
  const html = await page('index.html')
  const opening = element(html, 'section', 'homepage-opening')
  assert.equal(
    visibleText(opening.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/)?.[1]).replace(/\n\s+/g, '\n'),
    'Validate XBRL\nUnderstand the data',
  )
  assert.match(opening, />Free and open-source XBRL platform</)
  assert.match(opening, /Ensure compliance with global reporting standards, explore disclosures interactively, and feed verified structured financial data directly into your applications, data pipelines, and AI workflows\./)

  assert.deepEqual(
    links(element(opening, 'div', 'homepage-actions')).map(({ href, text }) => [text, href]),
    [
      ['Explore a real interactive iXBRL filing', '/demo/ixbrl-viewer/ixbrlviewer.html'],
    ],
  )

  const proof = opening.match(/<dl\b[^>]*>([\s\S]*?)<\/dl>/)?.[1]
  assert.ok(proof, 'expected the project facts in a description list')
  assert.equal([...proof.matchAll(/<div\b[^>]*>/g)].length, 3)
  assert.match(proof, /<dt[^>]*>50\+<\/dt>/)
  assert.match(proof, /Regulators, banks and technology companies rely on Arelle for data quality and comparison\./)
  assert.match(proof, new RegExp(`<dt[^>]*>${new Date().getFullYear() - 2010} yrs<\\/dt>`))
  assert.match(proof, /Maintained in the open since 2010 under Apache 2\.0\./)
  assert.deepEqual(
    links(proof).map(({ href, text }) => [text, href]),
    [[
      'XBRL Certified Software',
      'https://software.xbrl.org/processor/arelle-arelle',
    ]],
  )
})

test('homepage progressively enhances the Desktop, Command line, Docker, Python API, Plugin, and Web server comparison', async () => {
  const html = await page('index.html')
  const comparison = element(html, 'section', 'homepage-capabilities')
  assert.match(comparison, />One engine, six interfaces</)
  assert.match(comparison, /<h2[^>]*>Built to fit your workflow<\/h2>/)

  const tablist = comparison.match(
    /<div\b[^>]*role=(?:"tablist"|tablist)[^>]*>[\s\S]*?<\/div>/,
  )?.[0]
  assert.ok(tablist, 'expected a tablist')
  const tabs = [...tablist.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g)]
  assert.equal(tabs.length, 6)
  assert.deepEqual(tabs.map(([, attributes, content]) => [attribute(attributes, 'id'), visibleText(content)]), [
    ['tab-gui', 'Desktop app'],
    ['tab-cli', 'Command line'],
    ['tab-docker', 'Docker'],
    ['tab-python', 'Python API'],
    ['tab-plugin', 'Plugin system'],
    ['tab-webserver', 'Web server'],
  ])
  assert.match(tabs[0][1], /\brole=(?:"tab"|tab)/)
  assert.match(tabs[0][1], /\baria-selected=(?:"true"|true)/)
  assert.match(tabs[0][1], /\btabindex=(?:"0"|0)/)
  assert.match(tabs[1][1], /\baria-selected=(?:"false"|false)/)
  assert.match(tabs[1][1], /\btabindex=(?:"-1"|-1)/)
  assert.match(tabs[2][1], /\brole=(?:"tab"|tab)/)
  assert.match(tabs[2][1], /\baria-selected=(?:"false"|false)/)
  assert.match(tabs[2][1], /\btabindex=(?:"-1"|-1)/)
  assert.match(tabs[3][1], /\brole=(?:"tab"|tab)/)
  assert.match(tabs[3][1], /\baria-selected=(?:"false"|false)/)
  assert.match(tabs[3][1], /\btabindex=(?:"-1"|-1)/)
  assert.match(tabs[4][1], /\brole=(?:"tab"|tab)/)
  assert.match(tabs[4][1], /\baria-selected=(?:"false"|false)/)
  assert.match(tabs[4][1], /\btabindex=(?:"-1"|-1)/)
  assert.match(tabs[5][1], /\brole=(?:"tab"|tab)/)
  assert.match(tabs[5][1], /\baria-selected=(?:"false"|false)/)
  assert.match(tabs[5][1], /\btabindex=(?:"-1"|-1)/)

  const panels = productPanels(comparison)
  assert.equal(panels.length, 6)
  assert.deepEqual(
    panels.map(([, attributes]) => [attribute(attributes, 'id'), attribute(attributes, 'aria-labelledby')]),
    [
      ['panel-gui', 'tab-gui'],
      ['panel-cli', 'tab-cli'],
      ['panel-docker', 'tab-docker'],
      ['panel-python', 'tab-python'],
      ['panel-plugin', 'tab-plugin'],
      ['panel-webserver', 'tab-webserver'],
    ],
  )
  assert.match(panels[0][1], /\brole=(?:"tabpanel"|tabpanel)/)
  assert.doesNotMatch(panels[1][1], /\bhidden(?:=|>)/)
  assert.doesNotMatch(panels[2][1], /\bhidden(?:=|>)/)
  assert.doesNotMatch(panels[3][1], /\bhidden(?:=|>)/)
  assert.doesNotMatch(panels[4][1], /\bhidden(?:=|>)/)
  assert.doesNotMatch(panels[5][1], /\bhidden(?:=|>)/)
  assert.equal(links(comparison).some(({ href }) => href === '#'), false)
  assert.match(panels[0][2], /Supported on Windows, macOS and Linux\./)
  assert.deepEqual(
    links(panels[0][2]).map(({ href, text }) => [text, href]),
    [['Download Arelle', '/download/']],
  )
  assert.match(panels[1][2], /Windows, macOS or Linux binaries/)
  assert.match(panels[1][2], /run Arelle from the Python source/)
  assert.deepEqual(
    links(panels[1][2]).map(({ href, text }) => [text, href]),
    [['Read the command line documentation', 'https://arelle.readthedocs.io/en/latest/command_line.html']],
  )
  assert.match(panels[3][2], /pip[\s\S]*?install[\s\S]*?arelle-release/)
  assert.deepEqual(
    links(panels[3][2]).map(({ href, text }) => [text, href]),
    [['Read the Python API documentation', 'https://arelle.readthedocs.io/en/latest/python_api/python_api.html']],
  )

  const transcript = await readTranscript('./examples/cli.txt')
  const cliTranscript = transcriptParts(transcript)
  const wideCommand = cliTranscript.command.replace(/\\\r?\n\s*/g, '')
  const cliPanel = panels[1][2]
  const consoleBlocks = codeBlocks(cliPanel)
  assert.deepEqual(consoleBlocks, [wideCommand, cliTranscript.command, cliTranscript.output])
  assert.match(cliPanel, /class=(?:"[^"]*\bconsole-command-wide\b[^"]*"|console-command-wide)/)
  assert.match(cliPanel, /class=(?:"[^"]*\bconsole-command-narrow\b[^"]*"|console-command-narrow)/)
  assert.match(cliPanel, /<span[^>]*class=(?:"console-example"|console-example)[^>]*>example<\/span>/)
  assert.match(
    cliPanel,
    /Gross profit in this example filing does not foot, and Arelle says so — naming the concept, the context, and the lines of the document to look at\./,
  )
  assert.match(cliPanel, /XML/)
  assert.match(cliPanel, /JSON/)
  assert.doesNotMatch(cliPanel, /cursor/i)
  assert.equal(consoleBlocks[2].endsWith('$'), false)
  assert.doesNotMatch(consoleBlocks[2], /\$/)

  const pythonSource = (await readFile(new URL('./examples/revenue.py', import.meta.url), 'utf8')).trim()
  const pythonTranscript = await readTranscript('./examples/python-api.txt')
  const pythonPanel = panels[3][2]
  const pythonBlocks = codeBlocks(pythonPanel)
  assert.deepEqual(pythonBlocks, [pythonSource, pythonTranscript[0], pythonTranscript.slice(1).join('\n')])
  assert.deepEqual(exampleOutputLabels(pythonPanel), ['command', 'output'])
  assert.match(pythonPanel, /python[\s\S]*?revenue\.py/)
  assert.match(
    pythonPanel,
    /loaded report is an object model that exposes facts and taxonomy relationships/i,
  )

  const webserverTranscript = await readTranscript('./examples/webserver.txt')
  const webserverPanel = panels[5][2]
  assert.match(webserverPanel, /arelleCmdLine[\s\S]*?--webserver[\s\S]*?localhost:8080/)
  assert.deepEqual(
    links(webserverPanel).map(({ href, text }) => [text, href]),
    [['Read the webserver security policy', 'https://arelle.readthedocs.io/en/latest/webserver_security.html']],
  )
  const webserverBlocks = codeBlocks(webserverPanel)
  assert.deepEqual(webserverBlocks, [webserverTranscript[0], webserverTranscript.slice(1).join('\n')])
  assert.match(webserverPanel, /trusted callers/i)
  assert.match(webserverPanel, /authentication/i)

  const dockerPanel = panels[2][2]
  const dockerCommand = (await readFile(new URL('./examples/docker.txt', import.meta.url), 'utf8')).trim()
  assert.match(dockerPanel, /docker[\s\S]*?pull[\s\S]*?arelleproject\/arelle/)
  assert.deepEqual(
    links(dockerPanel).map(({ href, text }) => [text, href]),
    [['Open Docker Hub', 'https://hub.docker.com/r/arelleproject/arelle']],
  )
  const dockerBlocks = codeBlocks(dockerPanel)
  assert.equal(dockerBlocks[0], dockerCommand)
  assert.equal(dockerBlocks[1], cliTranscript.output)
  const cliArguments = wideCommand
    .replace('$ arelleCmdLine ', '')
    .replace('demo-20251231.xbrl', '/data/demo-20251231.xbrl')
  assert.equal(
    dockerCommand.replace(/\\\r?\n\s*/g, ''),
    `$ docker run --rm -v "$PWD:/data" arelleproject/arelle:latest python arelleCmdLine.py ${cliArguments}`,
  )
  assert.match(dockerPanel, /Docker Hub/)
  assert.match(dockerPanel, /GitHub Container Registry/)
  assert.match(dockerPanel, /HTTP web service/)
  assert.doesNotMatch(dockerPanel, /independently (?:executed|tested|verified) in Docker/i)

  const pluginRules = await readFile(new URL('./examples/house_rules/house_rules.py', import.meta.url), 'utf8')
  const pluginSource = pluginRules.match(/# include start\r?\n([\s\S]*?)\r?\n# include end/)?.[1].trim()
  assert.ok(pluginSource, 'expected a marked plugin rule region')
  const pluginTranscript = await readTranscript('./examples/plugin.txt')
  const pluginTranscriptParts = transcriptParts(pluginTranscript)
  const pluginPanel = panels[4][2]
  assert.match(pluginPanel, /Extend Arelle(?:'|&#39;)s capabilities with custom validation rules/i)
  assert.deepEqual(
    links(pluginPanel).map(({ href, text }) => [text, href]),
    [[
      'Read the plugin development guide',
      'https://arelle.readthedocs.io/en/latest/plugins/development/getting_started.html',
    ]],
  )
  assert.deepEqual(
    codeBlocks(pluginPanel),
    [pluginSource, pluginTranscriptParts.command, pluginTranscriptParts.output],
  )
  assert.deepEqual(exampleOutputLabels(pluginPanel), ['command', 'output'])
  assert.match(pluginPanel, /@validation/)
  assert.match(pluginPanel, /ValidationHook[\s\S]*?XBRL_FINALLY/)
  assert.match(pluginPanel, /disclosureSystems/)
  assert.match(pluginPanel, /Validation[\s\S]*?error/)
  assert.match(
    pluginPanel,
    /Plugins throughout Arelle use the same hook system to add validation, loading, UI, export, and other behavior\./,
  )
  assert.equal(
    visibleText(pluginPanel.match(/<figcaption\b[^>]*>([\s\S]*?)<\/figcaption>/)?.[1]),
    'Plugins throughout Arelle use the same hook system to add validation, loading, UI, export, and other behavior.',
  )
  assert.doesNotMatch(pluginPanel, /SEC|ESMA|HMRC|identical implementations/i)
})

test('homepage GUI captures retain source dimensions and responsive derivatives', async () => {
  const html = await page('index.html')
  const comparison = element(html, 'section', 'homepage-capabilities')
  const panel = productPanels(comparison)[0]?.[2]
  assert.ok(panel, 'expected the Desktop app panel')
  const sourceAssets = [
    ['gui-light.png', '2264', '1580', /desktop app.*fact table/i],
    ['gui-dark.png', '2264', '1580', /desktop app.*dark mode/i],
  ]
  const renderedImages = [...panel.matchAll(/<img\b([^>]*)>/g)]
  assert.equal(renderedImages.length, sourceAssets.length)
  renderedImages.forEach(([tag, attributes], index) => {
    const [source, width, height, alt] = sourceAssets[index]
    assert.match(tag, /\bclass=(?:"[^"]*shot-(?:light|dark)[^"]*"|[^\s>]*shot-(?:light|dark))/)
    assert.equal(attribute(attributes, 'alt').match(alt)?.[0] !== undefined, true)
    assert.equal(attribute(attributes, 'width'), width)
    assert.equal(attribute(attributes, 'height'), height)
    assert.match(attribute(attributes, 'src'), /\.webp$/)
    assert.doesNotMatch(tag, /\.png(?:["' >]|$)/)
    assert.ok(source, 'source asset is named for the expected theme')
  })
  assert.match(panel, /<source\b[^>]*type=(?:"image\/avif"|image\/avif)[^>]*srcset="[^"]+\.avif/)
  assert.match(panel, /<source\b[^>]*type=(?:"image\/webp"|image\/webp)[^>]*srcset="[^"]+\.webp/)
  assert.doesNotMatch(panel, /\.png(?:["' >]|$)/)

  for (const image of renderedImages) {
    const src = attribute(image[1], 'src')
    const bytes = await readFile(new URL(src.slice(1), output))
    assertWebp(bytes, src)
  }
  for (const asset of sourceAssets) {
    await stat(new URL(`assets/images/${asset[0]}`, import.meta.url))
  }
})

test('homepage renders the maintained conformance roster across specifications and filing rules', async () => {
  const html = await page('index.html')
  const support = element(html, 'section', 'homepage-support')
  assert.match(support, /<p[^>]*class=(?:"homepage-eyebrow"|homepage-eyebrow)[^>]*>Conformance<\/p>/)
  assert.match(support, /<h2[^>]*>Specification and filing[- ]rule support<\/h2>/)
  assert.match(
    support,
    /<p[^>]*class=(?:"homepage-section-intro"|homepage-section-intro)[^>]*>Maintained as specifications and filing rules evolve\.<\/p>/,
  )
  assert.doesNotMatch(support, /certif/i)
  assert.doesNotMatch(support, /<a\b/i)
  assert.doesNotMatch(support, /perspective|rotate|taxonomy graph|support-card/i)

  assert.match(support, /<div[^>]*class=(?:"[^"]*\bsupport-split-grid\b[^"]*"|support-split-grid)(?:\s|>)/)
  assert.match(support, /<div[^>]*class="[^"]*specs-card[^"]*"/)
  assert.match(support, /<div[^>]*class="[^"]*rules-card[^"]*"/)
  assert.match(support, /<h3\b[^>]*>Specifications &(?:amp;)? Registries<\/h3>/)
  assert.match(support, /Comprehensive validation and processor coverage for core taxonomies, distribution formats, and shared registries\./)
  assert.match(support, /<h3\b[^>]*>Filing Rules &(?:amp;)? Programs<\/h3>/)
  assert.match(support, /Enforces local filing rules and disclosure system manuals across major financial regulators and tax authorities worldwide/)

  const expected = new Map([
    [
      'Core',
      {
        summary: 'The foundation for defining XBRL taxonomies and reports.',
        items: [
          'XBRL 2.1',
          'XBRL Dimensions 1.0',
          'Calculations 1.1',
          'Extensible Enumerations 1.0',
          'Extensible Enumerations 2.0',
          'Formula 1.0',
          'Table Linkbase 1.0',
          'Generic Links 1.0',
          'Generic References 1.0',
          'Generic Labels 1.0',
          'Generic Prefered Labels 1.0',
        ],
      },
    ],
    [
      'Formats',
      {
        summary: 'Formats for publishing and exchanging structured data.',
        items: [
          'Inline XBRL 1.0',
          'Inline XBRL 1.1',
          'xBRL-CSV 1.0',
          'xBRL-JSON 1.0',
          'Taxonomy Packages 1.0',
          'Report Packages 1.0',
        ],
      },
    ],
    [
      'Registries',
      {
        summary: 'Shared registries that keep reports and taxonomies portable.',
        items: [
          'Data Type Registry 1.0',
          'Functions Registry 1.0',
          'Link Role Registry 1.0',
          'Link Role Registry 2.0',
          'Units Registry 1.0',
          'Inline XBRL - Transformation Registry 1.0',
          'Inline XBRL - Transformation Registry 2.0',
          'Inline XBRL - Transformation Registry 3.0',
          'Inline XBRL - Transformation Registry 4.0',
          'Inline XBRL - Transformation Registry 5.0',
        ],
      },
    ],
    [
      'Filing Rules',
      {
        summary: "Enforces local filing rules and disclosure system manuals across major financial regulators and tax authorities worldwide, validating complex regulatory constraints that exist only as unstructured prose in filing manuals including the EDGAR Filer Manual and ESEF Reporting Manual.",
        items: [
          'ESMA ESEF',
          'SEC EDGAR',
          'US FERC',
          'Japan EDINET',
          'South Africa CIPC',
          'Denmark DBA',
          'Netherlands SBR',
          'Netherlands KvK',
          'UK HMRC',
          'Ireland ROS',
        ],
      },
    ],
  ])

  for (const [title, { summary }] of expected) {
    if (title !== 'Filing Rules') {
      assert.match(support, new RegExp(`<h4[^>]*class=(?:"split-section-title"|split-section-title)[^>]*>${title}</h4>`))
      assert.match(support, new RegExp(summary.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))
    }
  }

  const allItems = [...support.matchAll(/<li\b[^>]*>([\s\S]*?)<\/li>/g)].map((match) => visibleText(match[1]))
  const expectedAllItems = [...expected.values()].flatMap(({ items }) => items)
  assert.deepEqual(allItems, expectedAllItems)

  const checks = [...support.matchAll(/<span\b([^>]*)>✓<\/span>/g)]
  assert.equal(checks.length, expectedAllItems.length, 'every supported item is marked with a checkmark')
  for (const check of checks) {
    assert.match(check[1], /\baria-hidden=(?:"true"|true)/)
  }
})

test('generated Viewer demo is complete, healthy, and configured for the site', async () => {
  const filingDependencies = [
    'exhibit1019-formofemployme.htm',
    'exhibit1022-herrenofferlet.htm',
    'exhibit1023-peekofferletter.htm',
    'exhibit211subsidiaries1231.htm',
    'exhibit231consentofauditor.htm',
    'exhibit311-section302xceoc.htm',
    'exhibit312-section302xcfoc.htm',
    'exhibit321-section906xceoc.htm',
    'exhibit322-section906xcfoc.htm',
    'exhibit404-descriptionofse.htm',
    'wk-20251231.htm',
    'wk-20251231.xsd',
    'wk-20251231_cal.xml',
    'wk-20251231_def.xml',
    'wk-20251231_g1.jpg',
    'wk-20251231_lab.xml',
    'wk-20251231_pre.xml',
  ]
  const files = await readdir(new URL(viewerRoute, output))
  assert.deepEqual(
    files.toSorted(),
    [...filingDependencies, 'ixbrlviewer.config.json', 'ixbrlviewer.html', 'ixbrlviewer.js'].toSorted(),
  )
  await assert.rejects(stat(new URL('demo/index.html', output)), { code: 'ENOENT' })

  const config = JSON.parse(await page(`${viewerRoute}ixbrlviewer.config.json`))
  assert.deepEqual(config, { skin: { faviconUrl: '../../favicon.ico' } })

  const filing = await page(`${viewerRoute}wk-20251231.htm`)
  assert.equal(filing.match(/format="ixt-sec:/g)?.length, 48)
  assert.doesNotMatch(filing, /application\/x\.ixbrl-viewer\+json/)

  const html = await page(`${viewerRoute}ixbrlviewer.html`)
  assert.match(html, /\bixv-stub-viewer\b/)
  assert.doesNotMatch(html, /format="ixt-sec:/)
  const viewerDataSource = html.match(
    /<script[^>]*type=(?:"application\/x\.ixbrl-viewer\+json"|application\/x\.ixbrl-viewer\+json)[^>]*>([\s\S]*?)<\/script>/,
  )?.[1]
  assert.ok(viewerDataSource, 'expected generated Viewer data')
  const viewerData = JSON.parse(viewerDataSource)
  assert.deepEqual(viewerData.features, {
    highlight_facts_on_startup: true,
    home_link_label: 'arelle.org',
    home_link_url: canonical(await page('index.html')),
    review: false,
  })
  const conceptCount = viewerData.sourceReports
    .flatMap((sourceReport) => sourceReport.targetReports)
    .reduce((count, targetReport) => count + Object.keys(targetReport.concepts).length, 0)
  assert.ok(conceptCount >= 800, `expected at least 800 concepts, received ${conceptCount}`)
  assert.doesNotMatch(viewerDataSource, /INVALID_IX_VALUE|ixTransformValueError/)
})
