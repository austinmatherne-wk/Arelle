#!/usr/bin/env node
// Fails if any URL the old WordPress site served has no target in the Hugo
// build output. The fixture beside this script was captured while WordPress was
// still up; it cannot be recaptured, so it is the whole definition of in scope.
import { stat, readFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const FIXTURE = join(dirname(fileURLToPath(import.meta.url)), 'legacy-urls.json')

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
// stubs and real pages, which is why resolvable URLs accept whichever exists:
// the three SEC-linked EDGAR paths are pinned with `url:` front matter and are
// real pages, not stubs.
async function readServed(root, url) {
  const path = join(root, url)
  return (await readIfFile(path)) ?? (await readIfFile(join(path, 'index.html')))
}

export async function checkLegacyUrls({ fixture, buildDir, sourceDir }) {
  const failures = []

  for (const url of fixture.resolvable) {
    if (!(await readServed(buildDir, url))) failures.push(`missing: ${url}`)
  }

  // Copied verbatim out of static/, and a redirect stub will not do: the XSD is
  // fetched by an XML parser and the CLA documents are linked as downloads,
  // neither of which follows a meta refresh. Comparing bytes against the staged
  // source proves the real thing was served rather than something at that path.
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

  // The old site 404'd these, so serving them now would be a regression: a
  // resurrected download redirector or author archive is a dead end for anyone
  // who follows it and a duplicate for search engines.
  for (const url of fixture.expected404) {
    if (await readServed(buildDir, url)) failures.push(`unexpectedly served: ${url}`)
  }

  return failures
}

// Skipped when the test suite imports this module for its exports.
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [buildDir = 'public'] = process.argv.slice(2)
  const fixture = JSON.parse(await readFile(FIXTURE, 'utf8'))
  const failures = await checkLegacyUrls({ fixture, buildDir, sourceDir: 'static' })

  if (failures.length) {
    console.error(`${failures.length} legacy URL(s) failed the check:`)
    for (const failure of failures) console.error(`  ${failure}`)
    process.exit(1)
  }

  const count = fixture.resolvable.length + fixture.verbatim.length
  console.log(`${count} legacy URLs resolve; ${fixture.expected404.length} stay unserved.`)
}
