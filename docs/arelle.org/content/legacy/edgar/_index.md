---
# Repository-facing notes only. This file is never rendered as a page; the body
# below is documentation for whoever opens this directory.
title: Legacy EDGAR pages
build:
  render: never
  list: never
---

These three pages exist for one reason: the U.S. Securities and Exchange Commission links them from its own documentation. They are compatibility surfaces, not part of arelle.org's information architecture.

Each page is pinned to the exact URL WordPress served it at, via `url:` front matter:

| File | Pinned URL | Aliases |
| --- | --- | --- |
| `applications.md` | `/arelle/pub/applications/` | none |
| `edgar-renderer-installation.md` | `/arelle/pub/edgar-renderer-installation/` | `/edgar-renderer-installation/`, `/pub/edgar-renderer-installation/`, `/documentation/edgar-renderer-installation/` |
| `edgar-renderer-technical-operation.md` | `/arelle/documentation/edgar-renderer-technical-operation/` | `/arelle/pub/edgar-renderer-installation/edgar-renderer-technical-operation/`, `/documentation/edgar-renderer-installation/edgar-renderer-technical-operation/` |

Nothing else on the site uses `/arelle/` as a canonical path, so the prefix itself marks these pages as frozen.

Constraints that must hold:

- They must stay out of the site menu, out of every list and section page, and out of `sitemap.xml`. Each page carries `build.list: never` and `sitemap.disable: true`; the two `_index.md` files stop Hugo from rendering `/legacy/` and `/legacy/edgar/` section pages. No page on the site links to them.
- New technical documentation does **not** belong here. It belongs on Read the Docs, which already has a Popular Plugins section covering the EDGAR plugin. These files are an exception kept for URL compatibility, not a precedent.
- Changing or removing any of these URLs requires first confirming that the SEC no longer depends on them. Nothing in this repository can tell you that.

The pages are frozen in URL, not in content: stale links inside them (the retired `edgar_renderer_3_3_0_814.zip`, the WordPress download tables) have been repointed at live equivalents.
