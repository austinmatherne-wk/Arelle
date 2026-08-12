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

## Static pages and historical assets

The issue-04 boundary covers the migrated static pages, compatibility aliases,
four historical assets, and paths that the retired static site intentionally
left unserved. The fixed boundary fixture lives in
`static-pages/static-pages.json`; it does not include project-update, blog, or
feed routes, which are covered by the later archive migration.

```shell
hugo --minify
npm run check:static-pages
```

`static-pages/check.test.mjs` covers the boundary checker itself; run it with
`npm test`.
