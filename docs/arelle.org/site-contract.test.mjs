import assert from 'node:assert/strict'
import { readFile, readdir, stat } from 'node:fs/promises'
import { test } from 'node:test'

const output = new URL('./public/', import.meta.url)

async function page(path) {
  return readFile(new URL(path, output), 'utf8')
}

function element(html, tag, className) {
  const match = html.match(new RegExp(`<${tag}[^>]*class=(?:"${className}"|${className})(?:\\s|>)[\\s\\S]*?</${tag}>`))
  assert.ok(match, `expected ${tag}.${className}`)
  return match[0]
}

function links(html) {
  return [...html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/g)].map((match) => ({
    attributes: match[1],
    href: match[1].match(/\bhref=(?:"([^"]+)"|([^\s>]+))/)?.slice(1).find(Boolean),
    text: match[2].replace(/<[^>]+>/g, '').trim(),
  }))
}

function scripts(html) {
  return [...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)]
}

test('primary navigation exposes direct destinations in the settled order', async () => {
  const html = await page('index.html')
  const primary = element(html, 'nav', 'primary-navigation')
  assert.deepEqual(
    links(primary).map(({ href, text }) => [text, href]),
    [
      ['Arelle', '/'],
      ['Download', '/download/'],
      ['Docs', 'https://arelle.readthedocs.io/'],
      ['Updates', '/blog/'],
      ['GitHub', 'https://github.com/Arelle/Arelle'],
    ],
  )
  assert.doesNotMatch(primary, /external|<img/i)
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
  assert.match(redirect, /url=\/about\//)
  await assert.rejects(stat(new URL('participate/index.html', output)), { code: 'ENOENT' })
})

test('footer contains community, legal, and verbatim trademark content', async () => {
  const html = await page('index.html')
  const footer = element(html, 'footer', 'site-footer')
  assert.deepEqual(
    links(element(footer, 'nav', 'footer-navigation')).map(({ href, text }) => [text, href]),
    [
      ['About', '/about/'],
      ['Google Group', 'https://groups.google.com/d/forum/arelle-users'],
      ['Contributing', 'https://arelle.readthedocs.io/en/latest/contributor_guides/contributing.html'],
      ['Monthly standup', 'mailto:support@arelle.org'],
    ],
  )
  assert.match(footer, /(?:©|&copy;) \d{4} Workiva Inc\./)
  assert.match(footer, /https:\/\/www\.workiva\.com\/privacy-policy/)
  assert.match(
    footer,
    /XBRL™ is a trademark of XBRL International, Inc\. All rights reserved\. The XBRL™ standards are open and freely licensed by way of the XBRL International License Agreement\. Our use of these trademarks is permitted by XBRL International in accordance with the XBRL International Trademark Policy\./,
  )
})

test('theme control is action-labelled and its only controller stays under 1 KB', async () => {
  const html = await page('index.html')
  const pageScripts = scripts(html)
  assert.equal(pageScripts.length, 1)
  const [, attributes, controller] = pageScripts[0]
  assert.match(attributes, /\bdata-theme-controller\b/)
  assert.ok(Buffer.byteLength(controller) <= 1024)
  assert.match(controller, /ixbrl-viewer-theme/)

  const button = html.match(/<button[^>]*data-theme-toggle[^>]*>[\s\S]*?<\/button>/)?.[0]
  assert.ok(button)
  assert.match(button, /\baria-label="Switch to dark"/)
  assert.match(button, /\btitle="Switch to dark"/)
  assert.equal(button.replace(/<svg[\s\S]*?<\/svg>/g, '').replace(/<[^>]+>/g, '').trim(), '')

  const files = await readdir(output, { recursive: true })
  for (const file of files.filter((file) => file.endsWith('.html') && !file.startsWith('demo/'))) {
    const fileScripts = scripts(await page(file))
    assert.ok(fileScripts.length <= 1, `${file} contains an additional script`)
    for (const [tag, pageAttributes] of fileScripts) {
      assert.match(pageAttributes, /\bdata-theme-controller\b/, `${file} contains a non-theme script: ${tag}`)
    }
  }
})
