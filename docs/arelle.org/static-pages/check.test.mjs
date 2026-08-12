import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtemp, mkdir, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { checkStaticPageBoundary } from './check.mjs'

const EMPTY = { resolvable: [], verbatim: [], expected404: [] }

// Lays out a build/source tree from a { path: contents } map and runs the check.
async function check(fixture, files) {
  const root = await mkdtemp(join(tmpdir(), 'static-pages-'))
  for (const [path, contents] of Object.entries(files)) {
    await mkdir(dirname(join(root, path)), { recursive: true })
    await writeFile(join(root, path), contents)
  }
  return checkStaticPageBoundary({
    fixture: { ...EMPTY, ...fixture },
    buildDir: join(root, 'public'),
    sourceDir: join(root, 'static'),
  })
}

test('a static alias passes on a redirect stub', async () => {
  const failures = await check({ resolvable: ['/arelle/documentation/'] }, {
    'public/arelle/documentation/index.html': '<meta http-equiv=refresh content="0; url=/documentation/">',
  })
  assert.deepEqual(failures, [])
})

test('a static compatibility URL passes on a real page', async () => {
  const failures = await check({ resolvable: ['/arelle/pub/applications/'] }, {
    'public/arelle/pub/applications/index.html': '<html>Applications</html>',
  })
  assert.deepEqual(failures, [])
})

test('a static page URL with no file fails and is named', async () => {
  const failures = await check({ resolvable: ['/arelle/pub/', '/arelle/participate/'] }, {
    'public/arelle/participate/index.html': 'page',
  })
  assert.deepEqual(failures, ['missing: /arelle/pub/'])
})

test('a historical asset passes when its bytes match the staged source', async () => {
  const failures = await check({ verbatim: ['/2014/doc-2014-01-31.xsd'] }, {
    'public/2014/doc-2014-01-31.xsd': '<xs:schema/>',
    'static/2014/doc-2014-01-31.xsd': '<xs:schema/>',
  })
  assert.deepEqual(failures, [])
})

test('a historical asset fails when a redirect stub stands in for it', async () => {
  const failures = await check({ verbatim: ['/2014/doc-2014-01-31.xsd'] }, {
    'public/2014/doc-2014-01-31.xsd': '<meta http-equiv=refresh content="0; url=/schema.xsd">',
    'static/2014/doc-2014-01-31.xsd': '<xs:schema/>',
  })
  assert.deepEqual(failures, ['differs from staged source: /2014/doc-2014-01-31.xsd'])
})

test('a historical asset fails when it is absent from the build', async () => {
  const failures = await check({ verbatim: ['/arelle/logo-platform.png'] }, {
    'static/arelle/logo-platform.png': 'png',
  })
  assert.deepEqual(failures, ['missing: /arelle/logo-platform.png'])
})

test('a historical asset with no staged source to compare against fails', async () => {
  const failures = await check({ verbatim: ['/arelle/logo-platform.png'] }, {
    'public/arelle/logo-platform.png': 'png',
  })
  assert.deepEqual(failures, ['no staged source to compare against: /arelle/logo-platform.png'])
})

test('an expected-404 path passes when nothing is served there', async () => {
  const failures = await check({ expected404: ['/arelle/download/12/'] }, {
    'public/arelle/index.html': 'home',
  })
  assert.deepEqual(failures, [])
})

test('an expected-404 directory URL fails once something is served there', async () => {
  const failures = await check({ expected404: ['/arelle/category/status/'] }, {
    'public/arelle/category/status/index.html': 'stub',
  })
  assert.deepEqual(failures, ['unexpectedly served: /arelle/category/status/'])
})

test('an expected-404 file URL fails once something is served there', async () => {
  const failures = await check({ expected404: ['/arelle/wp-sitemap.xml'] }, {
    'public/arelle/wp-sitemap.xml': '<sitemap/>',
  })
  assert.deepEqual(failures, ['unexpectedly served: /arelle/wp-sitemap.xml'])
})
