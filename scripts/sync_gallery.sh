#!/usr/bin/env bash
# Rebuild the gallery from Instagram.
#
# Uses gallery-dl with your logged-in Brave session, which pulls the ORIGINAL
# media rather than grid thumbnails. Videos are represented by a frame taken
# with ffmpeg (the brightest of several samples, since a reel's first frame is
# often a black fade-in).
#
#   ./scripts/sync_gallery.sh
#
# Never asks for a password and never logs in — it reuses the session Brave
# already has. Then it writes:
#   public/ig/cover/*.jpg   480px, for the wall
#   public/ig/full/*.jpg    900px, loaded only when the viewer opens
#   src/data/gallery.ts     the manifest
set -euo pipefail

PROFILE="${IG_PROFILE:-pritkmr}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

command -v gallery-dl >/dev/null || { echo "gallery-dl not found"; exit 1; }
command -v ffmpeg     >/dev/null || { echo "ffmpeg not found"; exit 1; }

RAW="$(mktemp -d)"
trap 'rm -rf "$RAW"' EXIT

echo "==> fetching @${PROFILE} from your Brave session"
gallery-dl --cookies-from-browser brave --write-metadata "https://instagram.com/${PROFILE}" -d "$RAW"

echo "==> building the manifest"
RAW="$RAW" python3 scripts/build_gallery.py

echo "==> done — run 'bun run build' and check /gallery"
