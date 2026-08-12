# arelle.org

The [Hugo](https://gohugo.io/) source for the Arelle website, published to GitHub Pages.

## Prerequisites

- Hugo (extended). CI pins the version in `.github/workflows/build-website.yml`.
- Node.js 26 or newer.
- Chrome or Chromium for the served-artifact acceptance checks. Set
  `CHROME_PATH` if it is not installed in a standard location.

## Local development

Install dependencies and start the development server:

```shell
npm ci
hugo server
```

`npm ci` is required before any build: the stylesheet is assembled from
`node_modules/` by Hugo's asset pipeline rather than from a vendored or CDN copy.

To produce the normal Hugo output without the generated Viewer demo:

```shell
hugo --minify
```

The result lands in `public/`.

## Viewer demo taxonomy package

The Viewer demo is generated offline from the narrowly scoped taxonomy package
defined by `demo/taxonomy-package.json`. From the repository root, reproduce
the package with:

```shell
python scripts/build_viewer_demo_taxonomy_package.py \
  docs/arelle.org/demo/taxonomy-package.json \
  arelle-viewer-demo.zip
```

The builder verifies each upstream archive, copies the FASB US GAAP and SRT
packages, adds only the SEC files listed in the definition, replaces the
upstream metadata with Arelle-specific package metadata, and verifies the final
artifact digest. A maintainer with access to the `arelle-public` bucket can
publish the resulting file at
`ci/packages/arelle-viewer-demo.zip`.

Ordinary Hugo development does not build or download this package.

## Generating the Viewer demo

The production build generates the Workiva FY2025 Form 10-K Viewer after Hugo
finishes. To reproduce that composite build locally from this directory:

```shell
python -m venv /tmp/arelle-site
source /tmp/arelle-site/bin/activate
VIEWER_REQUIREMENT="$(grep -m1 '^ixbrl-viewer==' ../../requirements-plugins.txt)"
python -m pip install -e ../.. "$VIEWER_REQUIREMENT"
git clone --branch master --depth 1 https://github.com/Arelle/EDGAR.git /tmp/arelle-edgar
hugo --minify --baseURL https://arelle.org/
python ../../scripts/generate_viewer_demo.py . /tmp/arelle-edgar --base-url https://arelle.org/
python -m http.server --directory public 8000
```

Open `http://localhost:8000/demo/ixbrl-viewer/viewer.htm`. The Viewer must be
served over HTTP; it does not run from a `file:` URL. The generator downloads
and verifies the published demo taxonomy package, uses a fresh cache with
network access disabled during Arelle processing, and rejects log messages,
invalid SEC transformations, or an implausibly small concept set.

The generated `public/demo/` output remains ignored and is rebuilt rather than
committed or cached.

That composite output is also the production acceptance seam. With the virtual
environment still active, run every local gate against the same artifact:

```shell
npm test
npm run check:legacy-urls
htmltest -c .htmltest.yml
npx lhci autorun
```

The Node suite checks both built markup and browser behavior. Its browser tests
start a local server automatically and verify theme selection, persistence,
navigation states, reduced motion, and the Viewer's shared saved choice.

## Adding a blog post

Blog posts live in `content/blog/YYYY/` and are named `YYYY-MM-DD-slug.md`. The
year directories are the archive's year selector: each holds an `_index.md`
whose `title` is the year, and the most recent one is what `/blog/` itself
shows. Starting a new year means adding its directory and `_index.md`.

Front matter:

```yaml
---
title: June 2026 Update
date: 2026-06-26T16:49:00
summary: Optional authored summary for the archive and post deck.
---
```

The permalink comes from `date`, not the filename — `[permalinks]` in
`hugo.toml` maps blog pages to `/blog/:year/:month/:day/:slug/`, where the slug
is the filename with its date prefix stripped. Keep the filename's date and the
`date` field in agreement so posts sort and resolve the way they read.

Posts migrated from the old WordPress site also carry an `aliases` entry
pointing at their `/arelle/YYYY/MM/DD/slug/` URL. New posts have no old URL to
preserve and need no `aliases`.

Omit `summary` to let Hugo derive an archive summary from the post. Set it when
the post needs a concise authored summary; the same text appears as the post's
deck.

Replace the previous latest post's URL in `lighthouserc.yml` with the new post
so it is covered by the performance and accessibility budgets.

## Checks

`.github/workflows/build-website.yml` runs the checks below on every pull
request that touches `docs/arelle.org/`. Before running an individual check,
produce the complete artifact with the composite build under
[Generating the Viewer demo](#generating-the-viewer-demo). Each command below
then checks that same output.

### Legacy URLs

Every URL the old WordPress site served must still land somewhere in the build.
This is the check that matters most — three of the paths are linked from SEC
filings and cannot break:

```shell
npm run check:legacy-urls
```

The in-scope URLs live in `legacy-urls/legacy-urls.json`, captured from the live
WordPress site before it was retired. It cannot be recaptured, so treat it as
fixed: if the check fails, the site is wrong, not the fixture. Most entries pass
on an `aliases` redirect stub; the four `verbatim` assets must match their
`static/` copies byte for byte, because an XML parser and a browser download
will not follow a meta refresh. The `expected404` entries must stay unserved.

`legacy-urls/check.test.mjs` covers the checker itself as part of `npm test`.
That command also checks the complete production artifact in Node and Chrome,
and builds isolated custom-domain and project-site outputs to verify that
social-preview metadata contains the correct absolute URLs.

### htmltest

Checks links, mailto addresses, the favicon, and the doctype against the build
output. Install [htmltest](https://github.com/wjdp/htmltest), then from this
directory:

```shell
htmltest -c .htmltest.yml
```

Broken *external* links are logged but do not fail the run — see the comments in
`.htmltest.yml` for why.

### Lighthouse CI

Asserts category scores and transfer-size and request-count budgets — total,
per resource type, and third-party — against the minified output. The Node
tests separately enforce that the inline theme controller is the only
normal-site script and remains below 1.125 KiB:

```shell
npx lhci autorun
```

The production build's `--minify` is not optional here — the budgets are
calibrated against minified output. Do not point Lighthouse CI at
`hugo server`; its output is neither minified nor fingerprinted, so the numbers
will not match CI's.

#### Production budget baseline

The current B2 budgets were measured on 2026-08-11 from the composite
production artifact: `hugo --minify --baseURL https://arelle.org/`, followed by
the generated Viewer build described above. Lighthouse audited the minified
static output (the generated `public/demo/` Viewer is intentionally excluded)
three times for each of the nine routes in `lighthouserc.yml`, for 27 runs
total. Lighthouse 12.6.1 reported performance 0.99 or 1.0, accessibility 1.0,
best practices 1.0, SEO 1.0, and zero third-party requests on every run.
Assertions use pessimistic aggregation, so every repeated run must satisfy the
category and resource ceilings.

The maximum observed values and the enforced ceilings are:

| Resource | Stable maximum | Enforced ceiling |
| --- | ---: | ---: |
| Total transfer | 160,031 B | 180 KiB |
| Total requests | 10 | 11 |
| Document transfer / requests | 62,232 B / 1 | 72 KiB / 2 |
| Stylesheet transfer / requests | 15,595 B / 1 | 18 KiB / 2 |
| Image transfer / requests | 80,763 B / 7 | 90 KiB / 8 |
| Font transfer / requests | 10,933 B / 1 | 12 KiB / 2 |
| Media transfer / requests | 0 B / 0 | 1 KiB / 1 |
| Other transfer / requests | 1,441 B / 1 | 2 KiB / 2 |
| Third-party transfer / requests | 0 B / 0 | 0 B / 0 |
| Inline theme controller | 1,020 B | 1.125 KiB |

The B2 homepage itself measured 151,977 B across 6 requests; the legacy EDGAR
installation page supplied the site-wide maximum of 160,031 B across 10
requests.

The ceilings are rounded just above the observed maxima so normal content
maintenance has modest room without turning the B2 page-weight gate into an
arbitrary allowance. A zero media baseline and the zero third-party gate are
intentional: neither is a shipped dependency. Re-run the composite build and
`npx lhci autorun` when site assets or layouts change; do not recalibrate from
an unminified development server.

## Publishing

`.github/workflows/publish-website.yml` builds and deploys the site to GitHub
Pages. It will deploy on release once `release.yml` calls it, and supports
`workflow_dispatch` for content corrections in between. It owns no checks of its
own: the release caller gates it on the build workflow above.

## Download links

The download page links static S3 and Alibaba OSS stable aliases, which the
existing release workflow keeps pointed at the current release. Local and CI
site builds treat them as plain URLs and never resolve them through an API, so
no token or network access is needed to build the site.
