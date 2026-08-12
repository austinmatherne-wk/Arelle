#!/usr/bin/env node
// Checks the static pages, compatibility aliases, historical assets, and
// intentionally unserved paths owned by the static-page migration boundary.
import { stat, readFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const FIXTURE = join(dirname(fileURLToPath(import.meta.url)), 'static-pages.json')

async function readIfFile(path) {
  try {
    const info = await stat(path)
    if (!info.isFile()) return null
  } catch {
    return null
  }
  return readFile(path)
}

// A URL maps either to the file at that path or, for directory-style URLs, to
// the index.html inside it. Hugo emits the latter for both meta-refresh alias
// stubs and real pages.
async function readServed(root, url) {
  const path = join(root, url)
  return (await readIfFile(path)) ?? (await readIfFile(join(path, 'index.html')))
}

export async function checkStaticPageBoundary({ fixture, buildDir, sourceDir }) {
  const failures = []

  for (const url of fixture.resolvable) {
    if (!(await readServed(buildDir, url))) failures.push(`missing: ${url}`)
  }

  // Redirect stubs cannot replace these historical assets: the XSD is fetched
  // by an XML parser and the CLA documents are linked as downloads. Comparing
  // bytes against the staged source proves the real asset was served.
  for (const url of fixture.verbatim) {
    const built = await readServed(buildDir, url)
    if (!built) {
      failures.push(`missing: ${url}`)
      continue
    }
    const source = await readIfFile(join(sourceDir, url))
    if (!source) failures.push(`no staged source to compare against: ${url}`)
    else if (!source.equals(built)) failures.push(`differs from staged source: ${url}`)
  }

  // These paths were intentionally unserved by the retired static site. Serving
  // one now would create a compatibility regression and a duplicate route.
  for (const url of fixture.expected404) {
    if (await readServed(buildDir, url)) failures.push(`unexpectedly served: ${url}`)
  }

  return failures
}

// Skipped when the test suite imports this module for its exports.
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [buildDir = 'public'] = process.argv.slice(2)
  const fixture = JSON.parse(await readFile(FIXTURE, 'utf8'))
  const failures = await checkStaticPageBoundary({ fixture, buildDir, sourceDir: 'static' })

  if (failures.length) {
    console.error(`${failures.length} static page or asset check(s) failed:`)
    for (const failure of failures) console.error(`  ${failure}`)
    process.exit(1)
  }

  console.log(
    `${fixture.resolvable.length} static pages/aliases resolve; ` +
    `${fixture.verbatim.length} historical assets match; ` +
    `${fixture.expected404.length} expected-404 paths stay unserved.`,
  )
}
