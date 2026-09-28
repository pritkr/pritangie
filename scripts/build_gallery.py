#!/usr/bin/env python3
"""Turn a gallery-dl export into public/ig/ + src/data/gallery.ts.

Run through scripts/sync_gallery.sh, or directly with RAW=<export-dir>:
    RAW=/path/to/gallery-dl python3 scripts/build_gallery.py

Kept separate from the shell wrapper so the fiddly part — grouping media items
back into posts, sampling video frames, resizing, and emitting the manifest —
is testable on its own.
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict

RAW = os.environ.get("RAW", "")
PROFILE = os.environ.get("IG_PROFILE", "pritkmr")
SRC = os.path.join(RAW, "gallery-dl", "instagram", PROFILE)

COVER_PX, COVER_Q = 480, 60
FULL_PX, FULL_Q = 900, 70
VIDEO_EXT = {".mp4", ".webm", ".mov", ".m4v"}
# A frame is only usable if it is not (near) black — reels often open on a
# fade-in, so several timestamps are sampled and the brightest wins.
MIN_LUMA = 12

HEADER = '''/*
  The gallery: every photo from @{profile}, self-hosted.

  Fetched with:
    gallery-dl --cookies-from-browser brave https://instagram.com/{profile}
  which reuses the logged-in Brave session and pulls the originals rather than
  grid thumbnails. Videos are represented by a frame extracted with ffmpeg.

  Images live in `public/ig/` and are served from this domain — nothing is
  embedded from Instagram, so no third-party script or cookies, and the footer's
  "no trackers · no cookies" claim stays true.

  Two sizes per image: `cover` ({cover_px}px, ~{cover_kb}KB) for the wall and
  `full` ({full_px}px) for the viewer, fetched only when a post is opened. The
  wall therefore costs the covers as you scroll, not the whole {total_mb}MB set.

  `w`/`h` are the original pixel dimensions, used to reserve space so nothing
  reflows, and to build the justified rows.

  To refresh: ./scripts/sync_gallery.sh
*/

export type GalleryImage = {{
  /** Small version, used by the wall. */
  cover: string;
  /** Full size, fetched only when the viewer opens. */
  full: string;
  w: number;
  h: number;
}};

export type GalleryPost = {{
  /** ISO date, from the post metadata. */
  date: string;
  likes: number;
  /** The real post on Instagram. */
  permalink: string;
  /** Caption. Doubles as alt text. */
  caption: string;
  /** How many of this post's items were video. */
  videoCount: number;
  images: GalleryImage[];
}};

/** Newest first. */
export const galleryPosts: GalleryPost[] = [
'''


def run(*cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def run_bytes(*cmd: str) -> subprocess.CompletedProcess:
    """For commands whose stdout is binary (ffmpeg writing a raw frame)."""
    return subprocess.run(cmd, capture_output=True)


def luma(path: str) -> int:
    """Average brightness, 0-255. A one-pixel gray frame is all that is needed."""
    out = run_bytes("ffmpeg", "-v", "quiet", "-i", path, "-vf", "scale=1:1,format=gray",
                    "-f", "rawvideo", "-").stdout
    return out[0] if out else 0


def to_jpeg(src: str, dst: str, px: int, q: int) -> None:
    """Resize `src` to fit `px` on the long edge and write a JPEG at `dst`."""
    tmp = dst + ".tmp.jpg"
    try:
        if not src.lower().endswith((".jpg", ".jpeg")):
            r = run("sips", "-s", "format", "jpeg", src, "--out", tmp)
            if r.returncode or not os.path.exists(tmp):
                raise RuntimeError(r.stderr.strip() or f"sips could not read {src}")
        else:
            shutil.copyfile(src, tmp)
        r = run("sips", "-Z", str(px), "-s", "formatOptions", str(q), tmp)
        # sips reports an unreadable file as a warning and still exits 0, so the
        # exit code alone is not enough — the temp file has to be there.
        if r.returncode or not os.path.exists(tmp) or os.path.getsize(tmp) < 1024:
            raise RuntimeError(r.stderr.strip() or r.stdout.strip() or f"sips produced nothing from {src}")
        os.replace(tmp, dst)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def video_frame(src: str, dst: str, px: int) -> bool:
    """Pick the brightest sample across the clip, skipping fade-ins."""
    try:
        dur = float(run("ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", src).stdout.strip())
    except ValueError:
        dur = 8.0
    best, best_l = None, -1
    for frac in (0.15, 0.3, 0.45, 0.6, 0.75, 0.85):
        # A per-call temp name: a shared one races between videos and can be
        # read back stale from a previous run.
        with tempfile.TemporaryDirectory() as td:
            tmp = os.path.join(td, "f.jpg")
            run("ffmpeg", "-v", "quiet", "-y", "-ss", str(round(dur * frac, 2)), "-i", src,
                "-frames:v", "1", "-vf", f"scale='min({px},iw)':-2", "-q:v", "2", tmp)
            if not os.path.exists(tmp) or os.path.getsize(tmp) < 3000:
                continue
            value = luma(tmp)
            if value > best_l:
                best, best_l = tmp, value
                # Stash outside the temp dir so it survives the cleanup.
                best = os.path.join(tempfile.mkdtemp(), "best.jpg")
                shutil.copyfile(tmp, best)
    if best and best_l > MIN_LUMA:
        shutil.copyfile(best, dst)
        return True
    return False


def main() -> int:
    if not RAW or not os.path.isdir(SRC):
        print(f"no gallery-dl export at {SRC or '(RAW unset)'}", file=sys.stderr)
        return 1

    posts: OrderedDict[str, dict] = OrderedDict()
    for meta in glob.glob(os.path.join(SRC, "*.json")):
        d = json.load(open(meta))
        pid = str(d["post_id"])
        post = posts.setdefault(pid, {
            "date": d["post_date"][:10],
            "likes": d.get("likes") or 0,
            "permalink": d["post_url"],
            "caption": " ".join((d.get("description") or "").split()),
            "videoCount": 0,
            "items": {},
        })
        post["items"][int(d.get("num", 1))] = d
        if d.get("video_url"):
            post["videoCount"] += 1
        # gallery-dl writes the caption on one item per post, not all of them,
        # so an item with an empty description must not clobber the real one.
        desc = " ".join((d.get("description") or "").split())
        if desc and not post["caption"]:
            post["caption"] = desc

    # media_id -> every downloaded file for it. A post can hold both a photo
    # and a reel, and the export names them "<post_id>_<media_id>.<ext>", so the
    # same id can legitimately appear with two extensions. Keying on media_id
    # alone would let a .mp4 shadow its .jpg.
    files: dict[str, list[str]] = {}
    for path in glob.glob(os.path.join(SRC, "*")):
        name = os.path.basename(path)
        if name.endswith(".json"):
            continue
        parts = name.rsplit(".", 1)[0].split("_")
        files.setdefault(parts[1] if len(parts) > 1 else parts[0], []).append(path)

    shutil.rmtree("public/ig", ignore_errors=True)
    os.makedirs("public/ig/cover")
    os.makedirs("public/ig/full")

    out, skipped = [], 0
    for pi, post in enumerate(sorted(posts.values(), key=lambda p: p["date"], reverse=True), 1):
        images = []
        for num in sorted(post["items"]):
            item = post["items"][num]
            is_video = bool(item.get("video_url"))
            cands = files.get(str(item["media_id"]), [])
            # Match the download to the media type rather than taking whichever
            # the glob happened to yield last.
            src = next(
                (c for c in cands
                 if (os.path.splitext(c)[1].lower() in VIDEO_EXT) == is_video),
                None,
            )
            if not src:
                print(f"  {pi:02d}-{num:02d} skipped: no "
                      f"{'video' if is_video else 'image'} for media {item['media_id']}")
                skipped += 1
                continue
            name = f"{pi:02d}-{num:02d}"
            full = f"public/ig/full/{name}.jpg"
            if is_video:
                if not video_frame(src, full, FULL_PX):
                    print(f"  {name} skipped: every frame of the clip was black")
                    skipped += 1
                    continue
            else:
                to_jpeg(src, full, FULL_PX, FULL_Q)
            to_jpeg(full, f"public/ig/cover/{name}.jpg", COVER_PX, COVER_Q)
            images.append({
                "cover": f"/ig/cover/{name}.jpg",
                "full": f"/ig/full/{name}.jpg",
                "w": item.get("width_original") or 4,
                "h": item.get("height_original") or 3,
            })
        if not images:
            print(f"  post {pi:02d} skipped: no renderable media")
            continue
        out.append({k: post[k] for k in ("date", "likes", "permalink", "caption", "videoCount")}
                   | {"images": images})
        print(f"  {pi:02d} {post['date']} {len(images):2d} imgs {post['likes']:4d} likes  "
              f"{post['caption'][:44]}")

    if not out:
        print("nothing built", file=sys.stderr)
        return 1

    covers = [os.path.getsize(p) for p in glob.glob("public/ig/cover/*.jpg")]
    fulls = [os.path.getsize(p) for p in glob.glob("public/ig/full/*.jpg")]

    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    blocks = []
    for p in out:
        imgs = ",\n".join(
            '        { cover: "%s", full: "%s", w: %s, h: %s }' % (i["cover"], i["full"], i["w"], i["h"])
            for i in p["images"]
        )
        blocks.append(
            "  {\n"
            f'    date: "{p["date"]}",\n'
            f'    likes: {p["likes"]},\n'
            f'    permalink: "{p["permalink"]}",\n'
            f'    caption: "{esc(p["caption"])}",\n'
            f'    videoCount: {p["videoCount"]},\n'
            f"    images: [\n{imgs},\n    ],\n"
            "  },"
        )

    header = HEADER.format(
        profile=PROFILE,
        cover_px=COVER_PX,
        cover_kb=round(sum(covers) / len(covers) / 1024) if covers else 0,
        full_px=FULL_PX,
        total_mb=round(sum(fulls) / 1048576, 1),
    )
    open("src/data/gallery.ts", "w").write(header + "\n".join(blocks) + "\n];\n")
    print(f"\n{len(out)} posts, {sum(len(p['images']) for p in out)} images, {skipped} skipped")
    print(f"covers {sum(covers)//1024}KB / fulls {sum(fulls)//1024}KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
