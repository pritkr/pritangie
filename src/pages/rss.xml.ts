import rss from "@astrojs/rss";
import type { APIContext } from "astro";

type Post = {
  url: string;
  frontmatter: {
    title: string;
    pubDate: string;
    image?: { url: string; alt?: string };
    description?: string;
    subtitle?: string;
    author?: { name: string; url: string };
    tags?: string[];
  };
};

const posts = Object.values(import.meta.glob("./posts/*.md", { eager: true })) as Post[];

export async function GET(context: APIContext) {
  const sorted = [...posts].sort(
    (a, b) => new Date(b.frontmatter.pubDate).getTime() - new Date(a.frontmatter.pubDate).getTime(),
  );
  return rss({
    title: "Prit's Den",
    description: "Open-source, privacy tech, and FOSS community building — Prit Kumar.",
    site: context.site ?? "https://prit.eu.org",
    items: sorted.map((p) => ({
      title: p.frontmatter.title,
      pubDate: new Date(p.frontmatter.pubDate),
      link: p.url,
      description: p.frontmatter.description,
    })),
  });
}
