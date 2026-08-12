# arelle.org

The Hugo source for the Arelle website. The foundation keeps shared layout,
typography, theme behavior, and navigation in one buildable site.

## Prerequisites

- Hugo extended.
- Node.js and npm.
- Chrome or Chromium for the served-artifact acceptance checks. Set
  `CHROME_PATH` if it is not installed in a standard location.
- The [`htmltest`](https://github.com/wjdp/htmltest) CLI for link, favicon, and
  doctype checks.

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
(cd docs/arelle.org && hugo --minify --baseURL https://arelle.org/)
python scripts/generate_viewer_demo.py docs/arelle.org /tmp/arelle-edgar --base-url https://arelle.org/
```

Generation rejects unexpected log messages, invalid transformations, and
implausibly incomplete Viewer output. The generated demo is written under
`public/demo/ixbrl-viewer/` and is served over HTTP rather than `file:`.
The EDGAR transform checkout is pinned to the revision shown above.
After generation, run its focused rendered-artifact check from this directory:

```shell
node --test viewer-demo.test.mjs
```

## Production verification

The production acceptance seam is one composite artifact: minified Hugo
output followed by the generated offline Viewer. Build it from the repository
root with the pinned Viewer inputs, then run every gate against the same
`public/` directory:

```shell
(cd docs/arelle.org && hugo --minify --baseURL https://arelle.org/)
python scripts/generate_viewer_demo.py docs/arelle.org /tmp/arelle-edgar --base-url https://arelle.org/
(cd docs/arelle.org && \
  npm test && \
  npm run check:legacy-urls && \
  htmltest -c .htmltest.yml && \
  npx lhci autorun)
```

`npm test` covers the rendered routes, committed examples, social metadata,
Viewer artifact, and browser behavior. `htmltest` keeps links, favicons, and
doctypes valid while logging—but not failing on—unavailable external
destinations. Lighthouse audits the minified Hugo output only; the generated
Viewer is covered by its dedicated artifact and browser contracts.

### Measured production budget baseline

The current baseline was measured on 2026-08-12 from
`hugo --minify --baseURL https://arelle.org/`, followed by the Viewer
generation above. Lighthouse 12.6.1 audited the nine routes in
`lighthouserc.yml` three times each, for 27 runs total. Every run reported
performance 0.99 or 1.0, accessibility 1.0, best practices 1.0, SEO 1.0, and
zero third-party requests. Repeated assertions use pessimistic aggregation, so
the weakest score and largest resource value must pass.

| Resource | Stable maximum | Enforced ceiling |
| --- | ---: | ---: |
| Total transfer | 160,091 B | 180 KiB |
| Total requests | 10 | 11 |
| Document transfer / requests | 62,290 B / 1 | 72 KiB / 2 |
| Stylesheet transfer / requests | 15,597 B / 1 | 18 KiB / 2 |
| Image transfer / requests | 80,763 B / 7 | 90 KiB / 8 |
| Font transfer / requests | 10,933 B / 1 | 12 KiB / 2 |
| Media transfer / requests | 0 B / 0 | 1 KiB / 1 |
| Other transfer / requests | 1,441 B / 1 | 2 KiB / 2 |
| Third-party transfer / requests | 0 B / 0 | 0 B / 0 |
| Inline theme controller | 1,020 B | 1.125 KiB |

The homepage measured 152,102 B across six requests; the legacy EDGAR
installation page supplied the site-wide maximum of 160,091 B across ten
requests. The ceilings are rounded just above those maxima to allow normal
content maintenance without making the page-weight gate arbitrary. The zero
media and third-party budgets are intentional: neither is a shipped
dependency. Re-run the composite build and `npx lhci autorun` when assets or
layouts change; do not recalibrate from `hugo server` or other unminified
output.

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
npm run check:legacy-urls
```

`legacy-urls/check.test.mjs` covers the checker, and
`project-updates.test.mjs` covers the rendered yearly archive, aliases, and
feeds. The complete test command also checks the minified served artifact in
Node and Chrome and builds isolated custom-domain and project-site outputs to
verify that social-preview metadata contains the correct absolute URLs:

```shell
npm test
```
