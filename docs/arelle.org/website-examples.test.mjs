import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { test } from 'node:test'

const output = new URL('./public/', import.meta.url)

async function page(path) {
  return readFile(new URL(path, output), 'utf8')
}

async function transcript(path) {
  return (await readFile(new URL(path, import.meta.url), 'utf8'))
    .trimEnd()
    .split(/\r?\n/)
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

function article(html, id) {
  const match = html.match(new RegExp(`<article\\b[^>]*\\bid=(?:"${id}"|${id})[^>]*>[\\s\\S]*?<\\/article>`))
  assert.ok(match, `expected article #${id}`)
  return match[0]
}

function codeBlocks(html) {
  return [...html.matchAll(/<pre\b[^>]*>\s*<code\b[^>]*>([\s\S]*?)<\/code>\s*<\/pre>/g)]
    .map(([, content]) => decodeHtmlEntities(content).replace(/\r\n?/g, '\n').trimEnd())
}

test('homepage renders the committed CLI, Python, Docker, and plugin artifacts', async () => {
  const html = await page('index.html')
  const cli = await transcript('./examples/cli.txt')
  const python = await transcript('./examples/python-api.txt')
  const docker = await transcript('./examples/docker.txt')
  const plugin = await transcript('./examples/plugin.txt')
  const source = (await readFile(new URL('./examples/revenue.py', import.meta.url), 'utf8')).trim()
  const pluginRules = await readFile(new URL('./examples/house_rules/rules.py', import.meta.url), 'utf8')
  const pluginSource = pluginRules.match(/# include start\r?\n([\s\S]*?)\r?\n# include end/)?.[1].trim()

  assert.ok(pluginSource, 'expected a marked plugin rule region')
  assert.match(html, /<section\b[^>]*class=(?:"website-examples"|website-examples)/)
  assert.match(html, /Verify the same report four ways\./)

  assert.deepEqual(codeBlocks(article(html, 'example-cli')), [cli[0], cli.slice(1).join('\n')])
  assert.deepEqual(
    codeBlocks(article(html, 'example-python')),
    [source, python.slice(1).join('\n')],
  )
  assert.match(article(html, 'example-python'), new RegExp(python[0].replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))
  assert.deepEqual(
    codeBlocks(article(html, 'example-docker')),
    [docker[0], cli.slice(1).join('\n')],
  )
  assert.deepEqual(
    codeBlocks(article(html, 'example-plugin')),
    [pluginSource, plugin[0], plugin.slice(1).join('\n')],
  )
})

test('Docker guidance derives its validation command from the CLI example', async () => {
  const cli = (await transcript('./examples/cli.txt'))[0]
  const docker = (await transcript('./examples/docker.txt'))[0]
  const cliArguments = cli
    .replace('$ arelleCmdLine ', '')
    .replace('demo-20251231.xbrl', '/data/demo-20251231.xbrl')
  assert.equal(
    docker,
    `$ docker run --rm -v "$PWD:/data" arelleproject/arelle:latest python arelleCmdLine.py ${cliArguments}`,
  )
})
