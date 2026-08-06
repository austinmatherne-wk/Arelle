# arelle.org

The [Hugo](https://gohugo.io/) source for the Arelle website, published to GitHub Pages.

## Prerequisites

- Hugo (extended). CI pins the version in `.github/workflows/build-website.yml`.
- Node.js 26 or newer.

## Local development

Install dependencies and start the development server:

```shell
npm ci
hugo server
```

`npm ci` is required before any build: the stylesheet is assembled from
`node_modules/` by Hugo's asset pipeline rather than from a vendored or CDN copy.

To produce the same output CI builds and publishes:

```shell
hugo --minify
```

The result lands in `public/`.

## Adding a blog post

Blog posts live in `content/blog/` and are named `YYYY-MM-DD-slug.md`. Front
matter:

```yaml
---
title: June 2026 Update
date: 2026-06-26T16:49:00
---
```

The permalink comes from `date`, not the filename — `[permalinks]` in
`hugo.toml` maps blog pages to `/blog/:year/:month/:day/:slug/`, where the slug
is the filename with its date prefix stripped. Keep the filename's date and the
`date` field in agreement so posts sort and resolve the way they read.

Posts migrated from the old WordPress site also carry an `aliases` entry
pointing at their `/arelle/YYYY/MM/DD/slug/` URL. New posts have no old URL to
preserve and need no `aliases`.

Add the new post's URL to the target list in `lighthouserc.yml` if it should be
covered by the performance and accessibility budgets.

## Checks

`.github/workflows/build-website.yml` runs the checks below on every pull
request that touches `docs/arelle.org/`. Run them locally the same way before
opening one.

### htmltest

Checks links, mailto addresses, the favicon, and the doctype against the build
output. Install [htmltest](https://github.com/wjdp/htmltest), then from this
directory:

```shell
hugo --minify
htmltest -c .htmltest.yml
```

Broken *external* links are logged but do not fail the run — see the comments in
`.htmltest.yml` for why.

### Lighthouse CI

Asserts category scores and page-weight, request-count, and zero-JavaScript
budgets against the minified output:

```shell
hugo --minify
npx lhci autorun
```

`--minify` is not optional here — the budgets are calibrated against minified
output. Do not point Lighthouse CI at `hugo server`; its output is neither
minified nor fingerprinted, so the numbers will not match CI's.

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
