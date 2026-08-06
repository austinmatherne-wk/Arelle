---
# Compatibility-only page: the WordPress feed lived at this URL. GitHub Pages
# serves a slash-terminated path via index.html, so the feed itself cannot live
# here — the HTML output is a redirect to /blog/ and the RSS output alongside it
# (/arelle/feed/index.xml) carries the posts. Canonical feed: /blog/index.xml.
title: Feed
url: /arelle/feed/
# Named rather than section-scoped: layouts/legacy/single.* would also claim the
# frozen SEC-linked pages under legacy/edgar/.
layout: feed
outputs:
  - HTML
  - RSS
build:
  list: never
sitemap:
  disable: true
---
