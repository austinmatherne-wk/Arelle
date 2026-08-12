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
