#!/usr/bin/env python3
"""Round 4: sources never touched before this run.

  * Internshala part-time keyword categories + work-from-home fresher-jobs
  * Unstop opportunity=jobs (tech-filtered client-side)
  * python.org/jobs RSS (Python-community postings)
  * Remote AI-contractor boards: Mercor (Ashby), Scale AI (GH), Turing (GH),
    Labelbox (GH), Toloka (GH) - all hire remote part-time/contract, India OK

Merges into raw-leads.json / raw-leads-extra.json like scan3.py.
"""
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scan  # noqa: E402  (shared fetch/parse helpers)
from sources import curl, clean, row  # noqa: E402


def _p(n):
    return os.path.join(HERE, n)


PART_TIME_PAGES = [
    ("PT Python", "https://internshala.com/internships/part-time-python-development-internships/"),
    ("PT Data Science", "https://internshala.com/internships/part-time-data-science-internships/"),
    ("PT React", "https://internshala.com/internships/part-time-react-development-internships/"),
    ("PT Machine Learning", "https://internshala.com/internships/part-time-machine-learning-internships/"),
    ("PT Backend", "https://internshala.com/internships/part-time-backend-development-internships/"),
    ("PT Front End", "https://internshala.com/internships/part-time-front-end-development-internships/"),
    ("PT Web Dev p2", "https://internshala.com/internships/part-time-web-development-internships/page-2/"),
    ("Fresher WFH all", "https://internshala.com/fresher-jobs/work-from-home-jobs/"),
    ("Fresher WFH SW", "https://internshala.com/fresher-jobs/work-from-home-software-development-jobs/"),
    ("Fresher WFH Data", "https://internshala.com/fresher-jobs/work-from-home-data-science-jobs/"),
    ("WFH Fresher pool", "https://internshala.com/internships/work-from-home-fresher-internships/"),
]


def scan_internshala_pt():
    scan.INTERNSHALA_PAGES = PART_TIME_PAGES
    return scan.scan_internshala()


TECH = re.compile(
    r"python|javascript|typescript|node|react|full[\s-]?stack|back[\s-]?end|"
    r"front[\s-]?end|software|developer|programmer|data|machine learning|\bml\b|"
    r"devops|linux|security|qa|api|open[\s-]?source|technical writer|automation", re.I)


def scan_unstop_jobs(pages=6):
    out = {}
    for page in range(1, pages + 1):
        url = ("https://unstop.com/api/public/opportunity/search-result?"
               f"opportunity=jobs&per_page=30&page={page}&sortBy=recent")
        body = curl(url, [("Accept", "application/json")])
        try:
            data = json.loads(body).get("data", {}).get("data", [])
        except Exception:
            print("  unstop-jobs page", page, "parse fail", flush=True)
            continue
        for item in data:
            title = scan.clean(item.get("title", ""))
            org = item.get("organisation") if isinstance(item.get("organisation"), dict) else {}
            skills = [s.get("skill_name", "") for s in (item.get("required_skills") or []) if isinstance(s, dict)]
            if not TECH.search(f"{title} {' '.join(skills)}"):
                continue
            link = item.get("seo_url") or item.get("short_url") or ""
            if not link:
                continue
            out[link] = row(source="unstop", title=title, company=scan.clean(org.get("name", "")),
                            location="Online/Remote" if item.get("region") == "online" else str(item.get("region") or ""),
                            stipend="paid" if str(item.get("isPaid")) == "True" else "",
                            posted=str(item.get("approved_date") or item.get("updated_at") or "")[:10],
                            url=link, job_type="Internship" if "intern" in title.lower() else "Job",
                            remote=item.get("region") == "online",
                            tags=[s for s in skills if s][:6])
        print(f"  unstop-jobs page {page} -> {len(out)} kept", flush=True)
        time.sleep(1)
    return list(out.values())


NAMES = {"mercor": "Mercor", "scaleai": "Scale AI", "turing": "Turing",
         "labelbox": "Labelbox", "toloka": "Toloka"}


def scan_python_jobs():
    out = {}
    body = curl("https://www.python.org/jobs/feed/rss", timeout=30)
    try:
        root = ET.fromstring(body)
    except Exception:
        print("  python.org/jobs RSS parse fail", flush=True)
        return []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = clean(item.findtext("description") or "", 400)
        if not link or not title:
            continue
        is_remote = bool(re.search(r"remote", desc, re.I))
        out[link] = row(source="pythonorg", title=title, company="",
                        location="Remote" if is_remote else "see posting",
                        posted=(item.findtext("pubDate") or "")[:16], url=link,
                        job_type="Remote" if is_remote else "Job",
                        tags=["python"] + re.findall(r"\b(remote|django|flask|fastapi|data|devops|junior|contract|part[\s-]?time)\b", desc, re.I)[:4])
    print(f"  python.org/jobs kept {len(out)}", flush=True)
    return list(out.values())


def scan_contractor_boards():
    out = {}
    targets = [("mercor", "ashby"), ("scaleai", "gh"), ("turing", "gh"),
               ("labelbox", "gh"), ("toloka", "gh")]
    for slug, kind in targets:
        url = (f"https://api.ashbyhq.com/posting-api/job-board/{slug}" if kind == "ashby"
               else f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=false")
        try:
            data = json.loads(curl(url))
            jobs = data.get("jobs", [])
        except Exception:
            print(f"  {kind}:{slug} fail", flush=True)
            continue
        n = 0
        for j in jobs:
            if kind == "ashby":
                t = j.get("title", "")
                loc = (j.get("location") or "") + " " + (j.get("locationId") or "")
                loc = loc.strip()
                link = j.get("jobUrl", "")
                post = j.get("publishedAt", "")
            else:
                t = j.get("title", "")
                offs = j.get("offices") or []
                deps = j.get("departments") or []
                loc = "; ".join(o.get("name", "") for o in offs if isinstance(o, dict))
                link = j.get("absolute_url", "") or ("https://boards.greenhouse.io/" + slug)
                post = ""
                blob = f"{t} {loc} " + " ".join(d.get("name", "") for d in deps if isinstance(d, dict))
            if kind == "ashby":
                blob = f"{t} {loc}"
            if not re.search(r"engineer|developer|data|python|javascript|reviewer|evaluator|trainer|annotator|rating|writer|coder|analyst|contractor|expert|specialist|contributor|operations|support|platform|cloud|ml\b|ai\b", blob, re.I):
                continue
            if not re.search(r"remote|anywhere|global|india|apac|worldwide|distributed", loc, re.I):
                continue
            if link in out:
                continue
            kt = "Contract" if re.search(r"contract|freelance|part|hourly|gig|expert|contributor", blob, re.I) else "Remote"
            out[link] = row(source="contractor", title=t, company=NAMES.get(slug, slug),
                            location=loc or "Remote", url=link, job_type=kt,
                            stipend="", posted=str(post)[:10], tags=["contract", slug])
            n += 1
        print(f"  {kind}:{slug} -> {n} kept (of {len(jobs)})", flush=True)
    return list(out.values())


def merge(path, new_rows):
    old = json.load(open(path)) if os.path.exists(path) else []
    seen = {r.get("url"): r for r in old}
    added = sum(1 for r in new_rows if r.get("url") and r.get("url") not in seen
                and not seen.setdefault(r["url"], r))
    out = list(seen.values())
    json.dump(out, open(path, "w"), indent=1)
    return len(old), len(out), added


def main():
    print("== unstop jobs ==", flush=True)
    a2 = scan_unstop_jobs()
    a, b, c = merge(_p("raw-leads.json"), a2)
    print(f"raw-leads.json: {a} -> {b} (+{c} new)")
    print("== python.org/jobs ==", flush=True)
    e1 = scan_python_jobs()
    print("== contractor boards ==", flush=True)
    e2 = scan_contractor_boards()
    a, b, c = merge(_p("raw-leads-extra.json"), e1 + e2)
    print(f"raw-leads-extra.json: {a} -> {b} (+{c} new)")


if __name__ == "__main__":
    main()
