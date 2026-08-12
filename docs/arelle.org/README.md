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

## Viewer demo

The production Viewer demo uses the narrowly scoped taxonomy package described
by `demo/taxonomy-package.json`. Rebuild that package from its pinned upstream
archives from the repository root:

```shell
python scripts/build_viewer_demo_taxonomy_package.py \
  docs/arelle.org/demo/taxonomy-package.json \
  arelle-viewer-demo.zip
```

The builder verifies every upstream archive and the final artifact digest. The
generator downloads the published artifact, verifies its identity, and then
runs Arelle with network access disabled:

```shell
python -m pip install -e . "ixbrl-viewer==1.5.1"
git clone https://github.com/Arelle/EDGAR.git /tmp/arelle-edgar
git -C /tmp/arelle-edgar checkout 72033f579e89ab47e882437b5d4ceed9c7656ed5
(cd docs/arelle.org && hugo --minify)
python scripts/generate_viewer_demo.py docs/arelle.org /tmp/arelle-edgar --base-url /
```

Generation rejects unexpected log messages, invalid transformations, and
implausibly incomplete Viewer output. The generated demo is written under
`public/demo/ixbrl-viewer/` and is served over HTTP rather than `file:`.
The EDGAR transform checkout is pinned to the revision shown above.
After generation, run its focused rendered-artifact check from this directory:

```shell
node --test viewer-demo.test.mjs
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
feeds. The complete test command also builds isolated custom-domain and
project-site outputs to verify that social-preview metadata contains the
correct absolute URLs:

```shell
npm test
```
