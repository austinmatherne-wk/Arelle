import assert from 'node:assert/strict'
import { mkdtemp, readFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { test } from 'node:test'

const siteDirectory = fileURLToPath(new URL('.', import.meta.url))
const previewPath = 'images/social-preview.png'

function attribute(tag, name) {
  const match = tag.match(new RegExp(`\\b${name}=(?:"([^"]*)"|([^\\s>]+))`))
  return match?.slice(1).find((value) => value !== undefined)
}

function tagWithAttribute(html, tagName, name, value) {
  return [...html.matchAll(new RegExp(`<${tagName}\\b[^>]*>`, 'g'))]
    .map((match) => match[0])
    .find((tag) => attribute(tag, name) === value)
}

function metadata(html, property) {
  const tag = tagWithAttribute(html, 'meta', 'property', property)
  assert.ok(tag, `expected ${property} metadata`)
  return attribute(tag, 'content')
}

function canonical(html) {
  const tag = tagWithAttribute(html, 'link', 'rel', 'canonical')
  assert.ok(tag, 'expected canonical metadata')
  return attribute(tag, 'href')
}

function pngDimensions(bytes) {
  assert.equal(bytes.subarray(1, 4).toString(), 'PNG')
  assert.equal(bytes.subarray(12, 16).toString(), 'IHDR')
  return [bytes.readUInt32BE(16), bytes.readUInt32BE(20)]
}

async function builtSite(baseUrl) {
  const destination = await mkdtemp(join(tmpdir(), 'arelle-social-preview-'))
  const build = spawnSync('hugo', ['--minify', '--baseURL', baseUrl, '--destination', destination], {
    cwd: siteDirectory,
    encoding: 'utf8',
  })
  assert.equal(build.status, 0, build.stderr)
  return {
    destination,
    page: (path) => readFile(join(destination, path), 'utf8'),
  }
}

for (const baseUrl of ['https://arelle.org/', 'https://arelle.github.io/Arelle/']) {
  test(`social previews are complete at ${baseUrl}`, async (t) => {
    const site = await builtSite(baseUrl)
    t.after(() => rm(site.destination, { recursive: true, force: true }))

    const pages = [
      {
        path: 'index.html',
        url: baseUrl,
        title: 'Arelle',
        description: 'Validate, explore and extract XBRL data with Arelle, the free and open source XBRL platform.',
      },
      {
        path: 'download/index.html',
        url: `${baseUrl}download/`,
        title: 'Download · Arelle',
        description: 'Download Arelle for Windows, macOS and Linux.',
      },
      {
        path: 'documentation/index.html',
        url: 'https://arelle.readthedocs.io/',
        title: 'Documentation · Arelle',
        description: 'Arelle documentation is hosted on Read the Docs.',
      },
      {
        path: 'blog/2026/06/26/june-2026-update/index.html',
        url: `${baseUrl}blog/2026/06/26/june-2026-update/`,
        title: 'June 2026 Update · Arelle',
        descriptionIncludes: 'We missed our monthly update in May',
      },
      {
        path: '404.html',
        url: `${baseUrl}404.html`,
        title: 'Page not found · Arelle',
        description: 'The requested page could not be found.',
      },
      {
        path: 'arelle/pub/applications/index.html',
        url: `${baseUrl}arelle/pub/applications/`,
        title: 'Applications · Arelle',
        descriptionIncludes: 'Arelle provides an application programming interface',
      },
    ]

    for (const expected of pages) {
      const html = await site.page(expected.path)
      assert.equal(canonical(html), expected.url, `${expected.path} canonical`)
      assert.equal(metadata(html, 'og:title'), expected.title, `${expected.path} title`)
      assert.equal(metadata(html, 'og:url'), expected.url, `${expected.path} URL`)
      assert.equal(metadata(html, 'og:image'), `${baseUrl}${previewPath}`, `${expected.path} image`)
      assert.equal(metadata(html, 'og:image:width'), '1200')
      assert.equal(metadata(html, 'og:image:height'), '630')

      const description = metadata(html, 'og:description')
      if (expected.description) {
        assert.equal(description, expected.description, `${expected.path} description`)
      } else {
        assert.ok(description.includes(expected.descriptionIncludes), `${expected.path} description`)
      }
      assert.doesNotMatch(
        html,
        new RegExp(`<img\\b[^>]*${previewPath}`),
        `${expected.path} must not load the preview image`,
      )
    }

    assert.deepEqual(pngDimensions(await readFile(join(site.destination, previewPath))), [1200, 630])
  })
}
