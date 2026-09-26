#!/usr/bin/env python3
"""Round 3: Prit-specific niche queries + startup boards (YC, Wellfound).
Merges into raw-leads.json / raw-leads-extra.json without re-fetching round 1-2."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scan  # noqa: E402  (shared fetch/parse helpers)


def _p(n):
    return os.path.join(HERE, n)


# --- 1. LinkedIn: his actual niche (privacy / extensions / FOSS / his stack) ---
NICHE_LINKEDIN = [
    # internships, India, remote
    ("Browser Extension", "India", "I", "2"),
    ("Chrome Extension", "India", "I", "2"),
    ("Privacy Engineer", "India", "I", "2"),
    ("Open Source Engineer", "India", "I", "2"),
    ("Web Scraping", "India", "I", "2"),
    ("Django Developer Intern", "India", "I", "2"),
    ("FastAPI", "India", "I", "2"),
    ("GraphQL Intern", "India", "I", "2"),
    ("Vue Developer Intern", "India", "I", "2"),
    ("React Native Intern", "India", "I", "2"),
    ("WordPress Developer Intern", "India", "I", "2"),
    ("Developer Advocate Intern", "India", "I", "2"),
    ("Technical Documentation", "India", "I", "2"),
    ("QA Automation Intern", "India", "I", "2"),
    ("Technical Support Engineer", "India", "I", "2"),
    ("Astro", "India", "I", "2"),
    ("Supabase", "India", "I", "2"),
    ("Frappe", "India", "I", "2"),
    ("ERPNext", "India", "I", "2"),
    ("OCR", "India", "I", "2"),
    ("Web3 Intern", "India", "I", "2"),
    # part-time, India, remote
    ("Browser Extension", "India", "P", "2"),
    ("React Native", "India", "P", "2"),
    ("Django", "India", "P", "2"),
    ("WordPress", "India", "P", "2"),
    ("Automation", "India", "P", "2"),
    ("Data Scraping", "India", "P", "2"),
    # worldwide remote internships
    ("Browser Extension", "", "I", "2"),
    ("Privacy", "", "I", "2"),
    ("Open Source Developer", "", "I", "2"),
    ("Python Developer", "", "I", "2"),
    ("Web Scraping", "", "I", "2"),
    ("Technical Writer", "", "I", "2"),
]

# --- 2. Internshala: keyword WFH pages (verified live, cards in brackets) ---
NICHE_INTERNSHALA = [
    ("Python", "https://internshala.com/internships/work-from-home-python-internships/"),
    ("Python p2", "https://internshala.com/internships/work-from-home-python-internships/page-2/"),
    ("React", "https://internshala.com/internships/work-from-home-react-internships/"),
    ("React p2", "https://internshala.com/internships/work-from-home-react-internships/page-2/"),
    ("Data Science kw", "https://internshala.com/internships/work-from-home-data-science-internships/"),
    ("Machine Learning kw", "https://internshala.com/internships/work-from-home-machine-learning-internships/"),
    ("Java", "https://internshala.com/internships/work-from-home-java-internships/"),
    ("Java p2", "https://internshala.com/internships/work-from-home-java-internships/page-2/"),
    ("DevOps kw", "https://internshala.com/internships/work-from-home-devops-internships/"),
    ("Golang", "https://internshala.com/internships/work-from-home-golang-internships/"),
    ("UI/UX kw", "https://internshala.com/internships/work-from-home-ui-ux-internships/"),
    ("Flutter kw", "https://internshala.com/internships/work-from-home-flutter-internships/"),
    ("Django kw", "https://internshala.com/internships/work-from-home-django-internships/"),
    ("Android kw", "https://internshala.com/internships/work-from-home-android-internships/"),
    ("PHP kw", "https://internshala.com/internships/work-from-home-php-internships/"),
    ("Search python", "https://internshala.com/internships/?search_term=python"),
    ("Search react", "https://internshala.com/internships/?search_term=react"),
    ("Search open source", "https://internshala.com/internships/?search_term=open%20source"),
    ("Search privacy", "https://internshala.com/internships/?search_term=privacy"),
    ("Search part time", "https://internshala.com/internships/?search_term=part%20time"),
    ("Search node", "https://internshala.com/internships/?search_term=node"),
    ("Search typescript", "https://internshala.com/internships/?search_term=typescript"),
]


def merge(path, new_rows):
    old = json.load(open(path)) if os.path.exists(path) else []
    seen = {}
    for r in old:
        seen[r.get("url")] = r
    added = 0
    for r in new_rows:
        u = r.get("url")
        if not u or u in seen:
            continue
        seen[u] = r
        added += 1
    out = list(seen.values())
    json.dump(out, open(path, "w"), indent=1)
    return len(old), len(out), added


def main():
    scan.LINKEDIN_COMBOS = NICHE_LINKEDIN
    print(f"== niche linkedin ({len(NICHE_LINKEDIN)} combos) ==", flush=True)
    li = scan.scan_linkedin()
    scan.INTERNSHALA_PAGES = NICHE_INTERNSHALA
    print(f"== niche internshala ({len(NICHE_INTERNSHALA)} pages) ==", flush=True)
    ins = scan.scan_internshala()
    a, b, c = merge(_p("raw-leads.json"), li + ins)
    print(f"raw-leads.json: {a} -> {b} (+{c} new)")

    # --- 3. startup boards (YC Work at a Startup + Wellfound, both SSR) ---
    from sources import curl, clean, row  # noqa: E402
    extra = []
    yc = curl("https://www.ycombinator.com/jobs", timeout=40)
    links = sorted(set(re.findall(r'href="(/companies/[^"]+/jobs/[^"]+)"', yc)))
    for href in links:
        slug = href.rsplit("/", 1)[-1]
        title = slug.split("-", 1)[-1] if "-" in slug else slug
        title = title.replace("-", " ").strip().title()
        company = href.split("/")[2].replace("-", " ").title()
        extra.append(row(source="yc_work", title=title, company=company,
                         location="YC startup (see posting)",
                         url="https://www.ycombinator.com" + href,
                         job_type="Startup", tags=["yc"]))
    print(f"YC WAT: {len(links)} job links", flush=True)

    wf = curl("https://wellfound.com/jobs", timeout=40)
    for m in re.finditer(r'"title":"([^"]{5,70})","[^"]*?"', wf):
        pass
    # wellfound SSR: extract /jobs/<id>-<slug> hrefs + nearby titles
    wf_links = sorted(set(re.findall(r'href="(/jobs/[a-z0-9-]+-\d+)"', wf)))
    titles = re.findall(r'"title":"([^"]{5,70})"', wf)
    for i, href in enumerate(wf_links):
        t = titles[i] if i < len(titles) else href.replace("-", " ").split("/")[-1]
        extra.append(row(source="wellfound", title=t, company="",
                         location="Remote/Startup (see posting)",
                         url="https://wellfound.com" + href,
                         job_type="Startup", tags=["wellfound"]))
    print(f"Wellfound: {len(wf_links)} links, {len(titles)} titles", flush=True)

    a, b, c = merge(_p("raw-leads-extra.json"), extra)
    print(f"raw-leads-extra.json: {a} -> {b} (+{c} new)")


if __name__ == "__main__":
    main()
