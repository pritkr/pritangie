/*
  Your Instagram posts, shown on /elsewhere.

  Images live in `public/ig/` and are served from this site — no Instagram
  embed, no third-party script, no cookies, so the footer's "no trackers · no
  cookies" claim stays true.

  Pulled from your own logged-in session and committed. Instagram has no public
  read API left (the endpoints scrapers rely on now answer "SecFetch Policy
  violation" or HTTP 429), so refreshing this list is a deliberate manual job
  rather than a build step.

  TO ADD A POST
  -------------
  Save the image into `public/ig/`, then add an entry below, newest first.
  `bun run ig:sync path/to/instagram-export.zip` does the unpacking if you have a
  "Download your information" export to hand.

  `caption` doubles as the image's alt text, so write it for someone who cannot
  see the picture.

  Reels are deliberately absent: their cover frame is a black still, and a black
  tile is worse on the page than one fewer post.

  An empty list renders no grid, so the page never shows a gap or an
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
  {
    image: "/ig/post-01.jpg",
    permalink: "https://www.instagram.com/p/Ddqcrf3kSvz53W73W2kXu0cwKmhJPw1hiWFH7s0/",
    caption: "Lost the hackathon, not the hustle. The code speaks for itself. 💻🔥 https://jansahay.pages.dev #JansahayRocks",
  },
  {
    image: "/ig/post-02.jpg",
    permalink: "https://www.instagram.com/p/DQCh0swkj-GciEwLwvWwssLv0QAdDC6euGbCI80/",
    caption: "Other side of the story made great by great people and Bangalore's chaos 🎞💙",
  },
  {
    image: "/ig/post-03.jpg",
    permalink: "https://www.instagram.com/p/DQA-89okejXIleAOsp0GhFYB4Ay-GwjonHiBMs0/",
    caption: "Random clicks from unforgettable nights ✨🌙😌",
  },
  {
    image: "/ig/post-04.jpg",
    permalink: "https://www.instagram.com/p/DNRAcO5SkXmYMnkNxAVDJJC2-vIBMO61TaMlpA0/",
    caption: "Ten frames, one soul, countless stories #PhotoDump #SoloVibes #CapturedMoments",
  },
];
