#!/usr/bin/env python3
"""Generate genuinely NEW postings: deep LinkedIn pagination (pages 4-20, never
scanned before), Internshala category pages 3-5, and deeper Unstop paging.
Writes raw-leads.json (URL-deduped merge)."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scan  # noqa: E402


def _p(n):
    return os.path.join(HERE, n)


def merge(path, new_rows):
    old = json.load(open(path)) if os.path.exists(path) else []
    seen = {r.get("url"): r for r in old}
    added = 0
    for r in new_rows:
        u = r.get("url")
        if u and u not in seen:
            seen[u] = r
            added += 1
    out = list(seen.values())
    json.dump(out, open(path, "w"), indent=1)
    return len(old), len(out), added


def deep_linkedin():
    # same high-yield queries, but pages 4-20 (start=75..975) never fetched before
    queries = [("Software Engineer Intern", "India", "I", "2"),
               ("Full Stack Developer Intern", "India", "I", "2"),
               ("Backend Developer Intern", "India", "I", "2"),
               ("Python Developer Intern", "India", "I", "2"),
               ("DevOps Engineer Intern", "India", "I", "2"),
               ("Software Developer", "India", "P", "2"),
               ("Data Engineer Intern", "India", "I", "2")]
    pages = (75, 100, 125, 150, 175, 200, 225, 250, 275, 300)
    out = {}
    from bs4 import BeautifulSoup
    import subprocess
    UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
    for kw, loc, jt, wt in queries:
        for start in pages:
            url = (f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
                   f"keywords={kw.replace(' ', '%20')}&location={loc}&f_JT={jt}&f_WT={wt}"
                   f"&sortBy=DD&start={start}")
            try:
                body = subprocess.run(["curl", "-sL", "--max-time", "20", "-A", UA, url],
                                      capture_output=True, text=True, timeout=26).stdout
            except Exception:
                continue
            if "<li" not in body:
                continue
            for card in BeautifulSoup(body, "lxml").select("li"):
                a = card.select_one("a.base-card__full-link")
                t = card.select_one(".base-search-card__title")
                if not (a and t):
                    continue
                link = (a.get("href") or "").split("?")[0]
                if not link or link in out:
                    continue
                comp = card.select_one(".base-search-card__subtitle")
                locel = card.select_one(".job-search-card__location")
                date = card.select_one("time")
                out[link] = {
                    "source": "linkedin", "title": scan.clean(t.get_text()),
                    "company": scan.clean(comp.get_text()) if comp else "",
                    "location": scan.clean(locel.get_text()) if locel else "",
                    "stipend": "", "duration": "",
                    "posted": (date.get("datetime") if date else "") or "",
                    "url": link,
                    "job_type": "Internship" if jt == "I" else "Part-time",
                    "remote": True, "tags": [kw],
                }
            time.sleep(0.35)
        print(f"  linkedin[{kw}] deep pages -> {len(out)} rows", flush=True)
    return list(out.values())


def deep_internshala():
    bases = [
        ("WebDev", "https://internshala.com/internships/work-from-home-web-development-internships/"),
        ("SoftwareDev", "https://internshala.com/internships/work-from-home-software-development-internships/"),
        ("Python", "https://internshala.com/internships/work-from-home-python-internships/"),
        ("React", "https://internshala.com/internships/work-from-home-react-internships/"),
        ("DataScience", "https://internshala.com/internships/work-from-home-data-science-internships/"),
        ("Backend", "https://internshala.com/internships/work-from-home-backend-development-internships/"),
        ("Frontend", "https://internshala.com/internships/work-from-home-front-end-development-internships/"),
        ("ML", "https://internshala.com/internships/work-from-home-machine-learning-internships/"),
        ("DevOps", "https://internshala.com/internships/work-from-home-devops-internships/"),
        ("Django", "https://internshala.com/internships/work-from-home-django-internships/"),
        ("Flutter", "https://internshala.com/internships/work-from-home-flutter-internships/"),
        ("Cyber", "https://internshala.com/internships/work-from-home-cyber-security-internships/"),
        ("Java", "https://internshala.com/internships/work-from-home-java-internships/"),
        ("Android", "https://internshala.com/internships/work-from-home-android-internships/"),
        ("Golang", "https://internshala.com/internships/work-from-home-golang-internships/"),
    ]
    pages = [(f"{lbl} p{n}", f"{u}page-{n}/") for lbl, u in bases for n in (3, 4, 5)]
    scan.INTERNSHALA_PAGES = pages
    return scan.scan_internshala()


def deep_unstop(pages=20):
    out = {}
    import subprocess
    UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
    TECH = ("python|javascript|typescript|node|react|software|developer|programmer|data|"
            "machine learning|\\bai\\b|devops|cloud|linux|security|qa|api|open source|"
            "automation|technical")
    import re
    TECH = re.compile(TECH, re.I)
    from sources import row
    for page in range(16, pages + 1):
        url = ("https://unstop.com/api/public/opportunity/search-result?"
               f"opportunity=internships&per_page=30&page={page}&sortBy=recent")
        try:
            body = subprocess.run(["curl", "-s", "--compressed", "--max-time", "40", "-A", UA, url],
                                  capture_output=True).stdout.decode("utf-8", "replace")
            items = json.loads(body)["data"]["data"]
        except Exception:
            continue
        n = 0
        for it in items:
            title = str(it.get("title") or "").strip()
            org = it.get("organisation") if isinstance(it.get("organisation"), dict) else {}
            skills = [s.get("skill_name", "") for s in (it.get("required_skills") or []) if isinstance(s, dict)]
            if not TECH.search(f"{title} {' '.join(skills)}"):
                continue
            link = it.get("seo_url") or it.get("short_url") or ""
            if not link.startswith("http"):
                continue
            reg = str(it.get("region") or "")
            out[link] = row(source="unstop", title=title, company=str(org.get("name") or ""),
                            location=("Online/Remote" if reg == "online" else reg),
                            stipend=("paid" if str(it.get("isPaid")) == "True" else ""),
                            posted=str(it.get("approved_date") or it.get("updated_at") or "")[:10],
                            url=link,
                            job_type="Internship" if "intern" in title.lower() else "Job",
                            remote=(reg == "online"),
                            tags=[s for s in skills if s][:6])
            n += 1
        if n:
            print(f"  unstop page {page}: {n} tech kept (total {len(out)})", flush=True)
        time.sleep(1)
    return list(out.values())


def main():
    print("== deep linkedin (pages 4-20) ==", flush=True)
    a = deep_linkedin()
    print("== deep internshala (pages 3-5) ==", flush=True)
    b = deep_internshala()
    print("== deep unstop (pages 16-20) ==", flush=True)
    c = deep_unstop()
    old, new, added = merge(_p("raw-leads.json"), a + b + c)
    print(f"raw-leads.json: {old} -> {new} (+{added} genuinely new)", flush=True)


if __name__ == "__main__":
    main()
