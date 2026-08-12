import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { test } from 'node:test'

const output = new URL('./public/', import.meta.url)

async function page(path) {
  return readFile(new URL(path, output), 'utf8')
}

function links(html) {
  return [...html.matchAll(/<a\b[^>]*href=(?:"([^"]+)"|([^\s>]+))[^>]*>([\s\S]*?)<\/a>/g)].map(
    ([, quoted, unquoted, content]) => ({
      href: quoted ?? unquoted,
      text: content.replace(/<[^>]+>/g, '').trim(),
    }),
  )
}

function feedTitles(xml) {
  return [...xml.matchAll(/<item>[\s\S]*?<title>([\s\S]*?)<\/title>/g)].map(([, title]) => title)
}

test('the project-update archive exposes complete yearly sections', async () => {
  const archive = await page('blog/index.html')
  assert.match(archive, /<h1[^>]*>Project updates<\/h1>/)

  const yearNavigation = archive.match(/<nav[^>]*class=(?:"update-year-navigation"|update-year-navigation)[^>]*>[\s\S]*?<\/nav>/)?.[0]
  assert.ok(yearNavigation, 'expected year navigation')
  assert.deepEqual(
    links(yearNavigation).map(({ href, text }) => [text, href]),
    [
      ['2026', '/blog/2026/'],
      ['2025', '/blog/2025/'],
      ['2024', '/blog/2024/'],
    ],
  )

  const expectedYears = new Map([
    ['blog/2026/index.html', ['2026', 6]],
    ['blog/2025/index.html', ['2025', 12]],
    ['blog/2024/index.html', ['2024', 11]],
  ])
  for (const [path, [year, count]] of expectedYears) {
    const html = await page(path)
    assert.match(html, new RegExp(`<h2[^>]*>${year}</h2>`))
    assert.equal(
      [...html.matchAll(/<article\b[^>]*class=(?:"update-entry"|update-entry)[^>]*>/g)].length,
      count,
      `${path} should contain every update from ${year}`,
    )
  }

  assert.match(archive, /July 2026 Update/)
  assert.match(archive, /<a[^>]*href=(?:"\/blog\/index\.xml"|\/blog\/index\.xml)>RSS<\/a>/)
})

test('all project-update feeds carry the same complete archive', async () => {
  const expectedTitles = [
    'July 2026 Update',
    'June 2026 Update',
    'April 2026 Update',
    'March 2026 Update',
    'February 2026 Update',
    'January 2026 Update',
    'December 2025 Update',
    'November 2025 Update',
    'October 2025 Update',
    'September 2025 Update',
    'August 2025 Update',
    'July 2025 Update',
    'June 2025 Update',
    'May 2025 Update',
    'April 2025 Update',
    'March 2025 Update',
    'February 2025 Update',
    'January 2025 Update',
    'December 2024 Update',
    'November 2024 Update',
    'October 2024 Update',
    'September 2024 Update',
    'August 2024 Update',
    'July 2024 Update',
    'June 2024 Update',
    'April - May 2024 Update',
    'March 2024 Update',
    'February 2024 Update',
    'January 2024 Update',
  ]

  const feeds = await Promise.all([
    page('index.xml'),
    page('blog/index.xml'),
    page('arelle/feed/index.xml'),
  ])
  for (const feed of feeds) assert.deepEqual(feedTitles(feed), expectedTitles)
})

test('historical update and feed URLs remain navigable', async () => {
  const oldPost = await page('arelle/2024/01/26/january-2024-update/index.html')
  assert.match(oldPost, /url=\/blog\/2024\/01\/26\/january-2024-update\//)

  const oldBlog = await page('arelle/blog/index.html')
  assert.match(oldBlog, /url=\/blog\//)

  const oldFeed = await page('arelle/feed/index.html')
  assert.match(oldFeed, /url=\/blog\//)

  const currentPost = await page('blog/2026/07/31/july-2026-update/index.html')
  assert.match(currentPost, /<h1[^>]*>July 2026 Update<\/h1>/)
  assert.match(currentPost, /class=(?:"update-archive-label"|update-archive-label)[^>]*>Arelle blog<\/a>/)
  assert.match(currentPost, /class=(?:"update-post-navigation"|update-post-navigation)/)
})
