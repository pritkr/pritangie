---
layout: ../../components/MarkdownPost.astro
title: "chaind: when your chat apps talk to your local AI"
description: "A Go daemon that bridges Telegram, Matrix, and WhatsApp to local AI agents over a permission-gated Unix socket."
author:
  name: "Prit Kumar"
  url: "https://github.com/pritkr"
image:
  url: "https://img.youtube.com/vi/zMO8yXD-v0Q/maxresdefault.jpg"
  alt: "chaind demo video thumbnail"
tags: ["go", "ai", "privacy", "fossism"]
pubDate: '2026-07-01'
---

A chatbot should not mean "someone else's server sees all my messages". That's the thought behind **chaind**, a Go daemon I co-built with [fossism](https://github.com/fossism) that bridges Telegram, Matrix, and WhatsApp to local AI agents over a permission-gated Unix socket.

The idea: your messages stay on your machine. An agent daemon listens on a local socket, and only the bridges you explicitly allow can talk to it. No cloud round-trip for your chat history — the socket is the privacy boundary.

What made this fun to build:

- **The Unix socket permission model** — enforcing "who gets to talk to the agent" at the OS level instead of trusting an app-level check.
- **Cross-platform watching** — knowing when a new message arrives on each bridge without polling everything into the ground.
- **The outbox scheduler** — batching and broadcasting replies from the agent back to whichever bridge asked, so a slow model doesn't stall your chat.

We shipped the status command and socket error handling first — boring plumbing, but it's what makes a daemon reliable instead of a demo.

It's AGPL-3.0 licensed and lives at [fossism/chaind-cli](https://github.com/fossism/chaind-cli). If you've ever wanted your Telegram bots to be actually yours — this is the direction.

Co-building it also reminded me why I love FOSS: two people, different time zones, one shared repo, and the best ideas come from arguing about the design in the README.
