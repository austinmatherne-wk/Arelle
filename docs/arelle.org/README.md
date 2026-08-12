# arelle.org

The Hugo source for the Arelle website. The foundation keeps shared layout,
typography, theme behavior, and navigation in one buildable site.

## Prerequisites

- Hugo extended.
- Node.js and npm.

## Build

From this directory, install the pinned frontend dependencies and assemble the
minified site:

```shell
npm ci
hugo --minify
```

The generated `public/` directory and Hugo resource cache are ignored. Start a
local development server with:

```shell
hugo server
```

## Project updates

Updates live in `content/blog/YYYY/`, with one `_index.md` year section per
archive year. The archive at `/blog/` shows the latest year, while each year
page shows that year's complete set of updates. The date in each post's
front matter determines its permalink:

```yaml
---
title: July 2026 Update
date: 2026-07-31T12:00:00
summary: Optional authored summary for the archive and post deck.
---
```

Posts migrated from WordPress retain an `aliases` entry for their historical
`/arelle/YYYY/MM/DD/slug/` URL. New updates do not need an alias. The canonical
RSS feed is `/blog/index.xml`; `/index.xml` and `/arelle/feed/index.xml` carry
the same complete archive for existing subscribers.

## Legacy URLs

The fixed corpus in `legacy-urls/legacy-urls.json` covers every migrated
WordPress route, including all project-update URLs, `/arelle/blog/`, and
`/arelle/feed/`. Resolvable entries must land on a page or redirect stub,
verbatim historical assets must match their staged `static/` copies byte for
byte, and the paths the old site left unserved must remain 404s.

```shell
hugo --minify
npm run check:legacy-urls
```

`legacy-urls/check.test.mjs` covers the checker, and
`project-updates.test.mjs` covers the rendered yearly archive, aliases, and
feeds. Run both with:

```shell
npm test
```
