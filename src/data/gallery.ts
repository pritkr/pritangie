/*
  The gallery: every photo from @pritkmr, self-hosted.

  Fetched with:
    gallery-dl --cookies-from-browser brave https://instagram.com/pritkmr
  which reuses the logged-in Brave session and pulls the originals rather than
  grid thumbnails. Videos are represented by a frame extracted with ffmpeg.

  Images live in `public/ig/` and are served from this domain — nothing is
  embedded from Instagram, so no third-party script or cookies, and the footer's
  "no trackers · no cookies" claim stays true.

  Two sizes per image: `cover` (480px, ~43KB) for the wall and `full` (900px)
  fetched only when the viewer opens. The wall therefore costs the 88 covers as
  you scroll, not the 14MB full set — a previous build loaded 77 fulls straight
  into the grid because only each post's first image had a cover.

  `w`/`h` are the original pixel dimensions, used to reserve space and to keep
  the aspect ratio before an image loads.

  To refresh: re-run gallery-dl, then rebuild this file. Posts are newest first.
*/

export type GalleryImage = {
  /** Small version, used by the wall. */
  cover: string;
  /** Full size, fetched only when the viewer opens. */
  full: string;
  w: number;
  h: number;
};

export type GalleryPost = {
  /** ISO date, from the post metadata. */
  date: string;
  likes: number;
  /** The real post on Instagram. */
  permalink: string;
  /** Caption. Doubles as alt text. */
  caption: string;
  /** How many of this post's items were video (shown as a badge). */
  videoCount: number;
  images: GalleryImage[];
};

/** Newest first. */
export const galleryPosts: GalleryPost[] = [
  {
    date: "2026-09-24",
    likes: 185,
    permalink: "https://www.instagram.com/p/Ddqcrf3kSvz53W73W2kXu0cwKmhJPw1hiWFH7s0/",
    caption: "Lost the hackathon, not the hustle. The code speaks for itself. 💻🔥 https://jansahay.pages.dev #JansahayRocks",
    videoCount: 0,
    images: [
        { cover: "/ig/cover/01-01.jpg", full: "/ig/full/01-01.jpg", w: 1440, h: 1920 },
        { cover: "/ig/cover/01-02.jpg", full: "/ig/full/01-02.jpg", w: 1440, h: 1920 },
        { cover: "/ig/cover/01-03.jpg", full: "/ig/full/01-03.jpg", w: 1440, h: 1920 },
        { cover: "/ig/cover/01-04.jpg", full: "/ig/full/01-04.jpg", w: 1440, h: 1920 },
        { cover: "/ig/cover/01-05.jpg", full: "/ig/full/01-05.jpg", w: 1440, h: 1920 },
        { cover: "/ig/cover/01-06.jpg", full: "/ig/full/01-06.jpg", w: 1440, h: 1920 },
        { cover: "/ig/cover/01-07.jpg", full: "/ig/full/01-07.jpg", w: 1440, h: 1920 },
        { cover: "/ig/cover/01-08.jpg", full: "/ig/full/01-08.jpg", w: 1440, h: 1921 },
    ],
  },
  {
    date: "2026-08-03",
    likes: 99,
    permalink: "https://www.instagram.com/reel/Dblev7OhwhjHzgzAwayYWLw5YJIk4m-fLA1gh80/",
    caption: "One Solution... 💪🏻🧿",
    videoCount: 1,
    images: [
        { cover: "/ig/cover/02-01.jpg", full: "/ig/full/02-01.jpg", w: 1080, h: 1920 },
    ],
  },
  {
    date: "2025-10-20",
    likes: 172,
    permalink: "https://www.instagram.com/p/DQCh0swkj-GciEwLwvWwssLv0QAdDC6euGbCI80/",
    caption: "Other side of the story made great by great people and Bangalore's chaos 🎞💙",
    videoCount: 3,
    images: [
        { cover: "/ig/cover/03-01.jpg", full: "/ig/full/03-01.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-02.jpg", full: "/ig/full/03-02.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-03.jpg", full: "/ig/full/03-03.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-04.jpg", full: "/ig/full/03-04.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-05.jpg", full: "/ig/full/03-05.jpg", w: 720, h: 900 },
        { cover: "/ig/cover/03-06.jpg", full: "/ig/full/03-06.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-07.jpg", full: "/ig/full/03-07.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-08.jpg", full: "/ig/full/03-08.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-09.jpg", full: "/ig/full/03-09.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-10.jpg", full: "/ig/full/03-10.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-11.jpg", full: "/ig/full/03-11.jpg", w: 720, h: 900 },
        { cover: "/ig/cover/03-12.jpg", full: "/ig/full/03-12.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-13.jpg", full: "/ig/full/03-13.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-14.jpg", full: "/ig/full/03-14.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-15.jpg", full: "/ig/full/03-15.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-16.jpg", full: "/ig/full/03-16.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-17.jpg", full: "/ig/full/03-17.jpg", w: 360, h: 448 },
        { cover: "/ig/cover/03-18.jpg", full: "/ig/full/03-18.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-19.jpg", full: "/ig/full/03-19.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/03-20.jpg", full: "/ig/full/03-20.jpg", w: 1080, h: 1350 },
    ],
  },
  {
    date: "2025-10-20",
    likes: 173,
    permalink: "https://www.instagram.com/p/DQA-89okejXIleAOsp0GhFYB4Ay-GwjonHiBMs0/",
    caption: "Random clicks from unforgettable nights ✨🌙😌",
    videoCount: 0,
    images: [
        { cover: "/ig/cover/04-01.jpg", full: "/ig/full/04-01.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/04-02.jpg", full: "/ig/full/04-02.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/04-03.jpg", full: "/ig/full/04-03.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/04-04.jpg", full: "/ig/full/04-04.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/04-05.jpg", full: "/ig/full/04-05.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/04-06.jpg", full: "/ig/full/04-06.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/04-07.jpg", full: "/ig/full/04-07.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/04-08.jpg", full: "/ig/full/04-08.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/04-09.jpg", full: "/ig/full/04-09.jpg", w: 1080, h: 1350 },
    ],
  },
  {
    date: "2025-08-12",
    likes: 180,
    permalink: "https://www.instagram.com/p/DNRAcO5SkXmYMnkNxAVDJJC2-vIBMO61TaMlpA0/",
    caption: "Ten frames, one soul, countless stories #PhotoDump #SoloVibes #CapturedMoments",
    videoCount: 0,
    images: [
        { cover: "/ig/cover/05-01.jpg", full: "/ig/full/05-01.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/05-02.jpg", full: "/ig/full/05-02.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/05-03.jpg", full: "/ig/full/05-03.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/05-04.jpg", full: "/ig/full/05-04.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/05-05.jpg", full: "/ig/full/05-05.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/05-06.jpg", full: "/ig/full/05-06.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/05-07.jpg", full: "/ig/full/05-07.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/05-08.jpg", full: "/ig/full/05-08.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/05-09.jpg", full: "/ig/full/05-09.jpg", w: 1080, h: 1350 },
        { cover: "/ig/cover/05-10.jpg", full: "/ig/full/05-10.jpg", w: 1080, h: 1350 },
    ],
  },
  {
    date: "2025-07-29",
    likes: 187,
    permalink: "https://www.instagram.com/p/DMr5oggROSCWX77P7MyS36U4aFDG-1Teh6-i8U0/",
    caption: "From hills to holy vibes — memories that hit different 🌿📸🛕",
    videoCount: 1,
    images: [
        { cover: "/ig/cover/06-01.jpg", full: "/ig/full/06-01.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/06-02.jpg", full: "/ig/full/06-02.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/06-03.jpg", full: "/ig/full/06-03.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/06-04.jpg", full: "/ig/full/06-04.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/06-05.jpg", full: "/ig/full/06-05.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/06-06.jpg", full: "/ig/full/06-06.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/06-07.jpg", full: "/ig/full/06-07.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/06-08.jpg", full: "/ig/full/06-08.jpg", w: 360, h: 360 },
    ],
  },
  {
    date: "2025-07-08",
    likes: 594,
    permalink: "https://www.instagram.com/p/DL22ZfehyRknG9mkblYBnYLkkLITw591fh4i3g0/",
    caption: "Started with confusions,wrapped up with smiles! 🙃✨ #TechnicalSupportWale",
    videoCount: 0,
    images: [
        { cover: "/ig/cover/07-01.jpg", full: "/ig/full/07-01.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/07-02.jpg", full: "/ig/full/07-02.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/07-03.jpg", full: "/ig/full/07-03.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/07-04.jpg", full: "/ig/full/07-04.jpg", w: 1440, h: 1440 },
        { cover: "/ig/cover/07-05.jpg", full: "/ig/full/07-05.jpg", w: 1440, h: 1440 },
    ],
  },
  {
    date: "2025-07-08",
    likes: 603,
    permalink: "https://www.instagram.com/p/DL2bNSlBWgddgBqmk_ItNIXNLdGbnz4sfkBJv00/",
    caption: "Pratibha Milan 2k25 💫✨",
    videoCount: 0,
    images: [
        { cover: "/ig/cover/08-01.jpg", full: "/ig/full/08-01.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/08-02.jpg", full: "/ig/full/08-02.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/08-03.jpg", full: "/ig/full/08-03.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/08-04.jpg", full: "/ig/full/08-04.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/08-05.jpg", full: "/ig/full/08-05.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/08-06.jpg", full: "/ig/full/08-06.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/08-07.jpg", full: "/ig/full/08-07.jpg", w: 1440, h: 1800 },
    ],
  },
  {
    date: "2025-03-23",
    likes: 169,
    permalink: "https://www.instagram.com/p/DHjEba5y1L2MbH5HEVFhm9dIsUDDUwr3LaHOmk0/",
    caption: "Squad goals unlocked! 🫥💪 #SquadGoals #EventVibes #MakingMemories #GoodTimes #SmilesForDays #CampusLife #FunTimes",
    videoCount: 0,
    images: [
        { cover: "/ig/cover/09-01.jpg", full: "/ig/full/09-01.jpg", w: 1440, h: 1080 },
        { cover: "/ig/cover/09-02.jpg", full: "/ig/full/09-02.jpg", w: 1440, h: 1082 },
        { cover: "/ig/cover/09-03.jpg", full: "/ig/full/09-03.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/09-04.jpg", full: "/ig/full/09-04.jpg", w: 1440, h: 1080 },
        { cover: "/ig/cover/09-05.jpg", full: "/ig/full/09-05.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/09-06.jpg", full: "/ig/full/09-06.jpg", w: 1440, h: 1080 },
        { cover: "/ig/cover/09-07.jpg", full: "/ig/full/09-07.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/09-08.jpg", full: "/ig/full/09-08.jpg", w: 1440, h: 1082 },
        { cover: "/ig/cover/09-09.jpg", full: "/ig/full/09-09.jpg", w: 1440, h: 1082 },
        { cover: "/ig/cover/09-10.jpg", full: "/ig/full/09-10.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/09-11.jpg", full: "/ig/full/09-11.jpg", w: 1440, h: 1800 },
    ],
  },
  {
    date: "2025-03-22",
    likes: 92,
    permalink: "https://www.instagram.com/p/DHhNCNUTsJA9l0YySiT7jctXlRbMjYIjgX9F7U0/",
    caption: "⚡🖤..!!",
    videoCount: 0,
    images: [
        { cover: "/ig/cover/10-01.jpg", full: "/ig/full/10-01.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/10-02.jpg", full: "/ig/full/10-02.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/10-03.jpg", full: "/ig/full/10-03.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/10-04.jpg", full: "/ig/full/10-04.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/10-05.jpg", full: "/ig/full/10-05.jpg", w: 1440, h: 1800 },
        { cover: "/ig/cover/10-06.jpg", full: "/ig/full/10-06.jpg", w: 1440, h: 1080 },
    ],
  },
  {
    date: "2025-01-10",
    likes: 93,
    permalink: "https://www.instagram.com/p/DEp3ZBHSakZzlxPxU2hvadEckEJF9lo_frYnKw0/",
    caption: "✨",
    videoCount: 0,
    images: [
        { cover: "/ig/cover/11-01.jpg", full: "/ig/full/11-01.jpg", w: 1080, h: 1080 },
        { cover: "/ig/cover/11-02.jpg", full: "/ig/full/11-02.jpg", w: 1080, h: 1080 },
        { cover: "/ig/cover/11-03.jpg", full: "/ig/full/11-03.jpg", w: 1080, h: 1080 },
    ],
  },
];
