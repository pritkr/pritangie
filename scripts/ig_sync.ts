#!/usr/bin/env bun
/*
  ig:sync — pull your own Instagram post images into the site.

  WHY THIS EXISTS
  ---------------
  Instagram retired every public read path, and the one scrapers use now
  returns "SecFetch Policy violation" — a deliberate anti-automation control.
  So the posts are downloaded once, by hand, from your own account, and
  committed to the repo. After that the site is fully self-hosted: no embed, no
  third-party script, no cookies, and the grid can't break when Instagram
  changes something.

  This script automates the tedious part of that: unpacking Instagram's own
  data export and turning it into web-ready images plus a manifest to paste.

  USAGE
  -----
  1. Instagram → Settings → Privacy → "Download your information" → request a
     download with "All data" (or at least posts/media), then unzip it.
  2. Run:

       bun run ig:sync path/to/instagram-export.zip     # or a folder

  3. It writes images to public/ig/ and prints a manifest for
     src/data/instagram.ts.

  Captions and post links are NOT in the export, so the printed manifest leaves
  those blank for you to fill in — pasting a link takes a few seconds each.

  Nothing here logs into Instagram, and your password is never involved.
*/

import { existsSync, mkdirSync, copyFileSync, writeFileSync, readdirSync, statSync, rmSync } from "node:fs";
import { basename, extname, join, resolve } from "node:path";
import { execFileSync } from "node:child_process";

const MAX_POSTS = 6;
const IMAGE_EXT = new Set([".jpg", ".jpeg", ".png", ".webp", ".avif"]);

const arg = process.argv[2];
if (!arg) {
  console.error(
    "usage: bun run ig:sync <path-to-instagram-export.zip|folder>",
  );
  process.exit(1);
}

const src = resolve(arg);
if (!existsSync(src)) {
  console.error(`not found: ${src}`);
  process.exit(1);
}

let mediaDir = src;

// A .zip (or the folder it was unzipped into) needs a little digging: the
// media lives under your_posts/media inside the export.
if (extname(src) === ".zip") {
  const tmp = join("/tmp", `ig-export-${Date.now()}`);
  console.log(`unpacking ${basename(src)} …`);
  try {
    execFileSync("unzip", ["-q", src, "-d", tmp], { stdio: "inherit" });
  } catch {
    console.error("could not unzip. Unzip it yourself and pass the folder:");
    console.error("  bun run ig:sync path/to/unzipped-export/your_posts/media");
    process.exit(1);
  }
  const walk = (dir: string, depth = 0): string | null => {
    if (depth > 6 || !existsSync(dir)) return null;
    for (const entry of readdirSync(dir)) {
      const full = join(dir, entry);
      if (statSync(full).isDirectory()) {
        if (entry === "media") return full;
        const hit = walk(full, depth + 1);
        if (hit) return hit;
      }
    }
    return null;
  };
  mediaDir = walk(tmp) ?? tmp;
  console.log(`media: ${mediaDir}`);
}

const files: string[] = [];
const collect = (dir: string, depth = 0) => {
  if (depth > 6) return;
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) collect(full, depth + 1);
    else if (IMAGE_EXT.has(extname(full).toLowerCase())) files.push(full);
  }
};
collect(mediaDir);

if (!files.length) {
  console.error(`no images found under ${mediaDir}`);
  process.exit(1);
}

/*
  Instagram names exported media `<epochMillis>_<uuid>.jpg`, so a reverse
  lexicographic sort is a reliable newest-first ordering without trusting
  mtimes (which a fresh unzip flattens).
*/
files.sort((a, b) => basename(b).localeCompare(basename(a), undefined, { numeric: true }));
const picked = files.slice(0, MAX_POSTS);

const outDir = resolve("public/ig");
mkdirSync(outDir, { recursive: true });

console.log(`\n${picked.length} of ${files.length} image(s) -> ${outDir}\n`);
const manifest: string[] = [];
picked.forEach((file, i) => {
  const name = `post-${String(i + 1).padStart(2, "0")}${extname(file).toLowerCase()}`;
  copyFileSync(file, join(outDir, name));
  manifest.push(`  {
    image: "/ig/${name}",
    permalink: "https://www.instagram.com/p/PASTE_SHORTCODE/",
    caption: "PASTE CAPTION",
  },`);
  console.log(`  ${name}  <- ${basename(file)}`);
});

const block = `export const instagramPosts: IgPost[] = [
${manifest.join("\n")}
];`;

const dataFile = resolve("src/data/instagram.ts");
const current = existsSync(dataFile) ? await Bun.file(dataFile).text() : "";
const filled = current.includes("PASTE_SHORTCODE");
if (!filled) {
  writeFileSync(
    dataFile,
    current.replace(
      /export const instagramPosts: IgPost\[\] = \[[\s\S]*?\];/,
      block,
    ),
  );
  console.log(`\nwrote ${dataFile}`);
} else {
  console.log(`\n${dataFile} already has entries — left it alone.`);
}

console.log(
  `\nNext: replace PASTE_SHORTCODE / PASTE CAPTION in src/data/instagram.ts\n` +
    `Copy a post link from the Instagram app or web, e.g.\n` +
    `  https://www.instagram.com/p/AbCdEfGhIjK/`,
);
