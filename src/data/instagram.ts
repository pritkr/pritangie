/*
  Your Instagram posts, shown on /elsewhere.

  These are your own posts, downloaded once by hand and committed — the images
  live in `public/ig/` and are served from this site. Nothing is embedded from
  Instagram at runtime, so there is no third-party iframe, no cookies, and the
  site's "no trackers · no cookies" claim stays true.

  WHY NOT PULL THEM AUTOMATICALLY
  ------------------------------
  Instagram retired every public read path for this. Verified directly against
  the profile: the endpoint scrapers use returns "SecFetch Policy violation"
  (a deliberate anti-automation control, not an oversight), the profile page is
  a ~636KB client-side shell with no post data in it, and the oEmbed endpoint
  demands an OAuth token. A real token needs a Meta app plus a Professional
  account and possibly App Review. The one-time download is the honest option,
  and it also means the grid cannot silently break when Instagram changes
  something.

  EASIEST WAY
  -----------
    bun run ig:sync path/to/instagram-export.zip

  Instagram → Settings → Privacy → "Download your information" → unzip →
  run the command. It writes the images to public/ig/ newest-first and prints
  a manifest to paste here. It never logs into Instagram and never touches your
  password. Or just save the images into public/ig/ yourself.

  An empty list simply renders no grid, so the page never shows a gap or an
  explanation of a missing feature.
*/

export type IgPost = {
  /** Path under /public, e.g. "/ig/post-01.jpg". */
  image: string;
  /** The real post URL, so the tile links back to Instagram. */
  permalink: string;
  /** Caption, reused as the image's alt text. */
  caption?: string;
};

/** Newest first. */
export const instagramPosts: IgPost[] = [
  // {
  //   image: "/ig/post-01.jpg",
  //   permalink: "https://www.instagram.com/p/XXXXXXXXXXX/",
  //   caption: "Wrote a small tool that does a thing I kept doing by hand.",
  // },
];
