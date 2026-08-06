---
layout: ../../components/MarkdownPost.astro
title: "How Predirect became my most-starred project"
description: "A one-install Manifest V3 extension that rewrites 30+ tracked sites to privacy-friendly frontends."
author:
  name: "Prit Kumar"
  url: "https://github.com/pritkr"
image:
  url: "/assets/predirectpreview.avif"
  alt: "Predirect extension preview"
tags: ["privacy", "browsers", "open-source"]
pubDate: '2026-07-26'
---

Predirect started as an itch. Every time I opened YouTube, X, or Reddit in a normal browser, I was being profiled — cookies, trackers, fingerprinting — before I'd even scrolled. The usual answer is "just use a private frontend", but then you're juggling five different tools and remembering five different URLs.

So I built an extension that does it for you: one Manifest V3 extension that rewrites 30+ tracked sites to privacy-friendly frontends. Install once, and YouTube becomes Invidious, X becomes a lightweight client, Reddit becomes a readable alternative — automatically.

The fun part was the redirect map. Every site has its own URL quirks, and a naive `replace("youtube.com", "invidious.example")` breaks half the URLs. The map needed to handle watch IDs, shorts, embeds, and paths without breaking the actual content.

It took a few weekends and a lot of "why is this URL still leaking my IP" debugging. The result sits at **270 stars on GitHub** and works on Chrome, Firefox, and Edge.

Two lessons I keep relearning:

1. **The best privacy tool is the one you don't notice.** If a user has to think about their privacy, you've already lost.
2. **Small, boring, focused tools win.** Not a "suite". One redirect map, done properly.

If you use it, star it — and open an issue when a site breaks. That's how it gets better.
