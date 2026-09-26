#!/usr/bin/env python3
"""Extra remote-job sources: Himalayas, RemoteOK, Remotive, Jobicy, Arbeitnow,
We Work Remotely RSS, Hacker News "Who is hiring", and fossjobs.net.

Writes raw-leads-extra.json (same row schema as scan.py so rank.py can merge).
"""
import html as htmlmod
import json
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))


def _p(name):
    return os.path.join(HERE, name)


UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
OUT = _p("raw-leads-extra.json")

TECH = re.compile(
    r"engineer|developer|programmer|software|frontend|front-end|backend|back-end|"
    r"full[\s-]?stack|python|javascript|typescript|node|react|golang|\bgo\b|rust|"
    r"data|devops|sre|platform|infrastructure|security|privacy|linux|cloud|docker|"
    r"kubernetes|api|qa|test|automation|machine learning|\bai\b|\bml\b|nlp|web|mobile|"
    r"android|flutter|support|technical|open[\s-]?source|solutions", re.I)
JUNIOR = re.compile(r"intern|junior|entry[- ]level|graduate|trainee|associate|"
                    r"apprentice|part[\s-]?time|contract|freelance|contributor", re.I)
INDIA_OK = re.compile(r"worldwide|anywhere|global|india|asia|apac|ist\b|remote", re.I)


def curl(url, timeout=30):
    try:
        return subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", UA, url],
                              capture_output=True, text=True).stdout
    except Exception as exc:
        print("  curl fail", url, exc, flush=True)
        return ""


def clean(txt, limit=0):
    t = re.sub(r"<[^>]+>", " ", txt or "")
    t = re.sub(r"\s+", " ", htmlmod.unescape(t)).strip()
    return t[:limit] if limit else t


def row(**kw):
    base = {"source": "", "title": "", "company": "", "location": "", "stipend": "",
            "duration": "", "posted": "", "url": "", "job_type": "Remote",
            "remote": True, "tags": []}
    base.update(kw)
    return base


def scan_himalayas(pages=40):
    out, cursor = {}, None
    for i in range(pages):
        url = "https://himalayas.app/jobs/api?limit=100"
        if cursor:
            url += "&cursor=" + cursor
        body = curl(url)
        try:
            data = json.loads(body)
        except Exception:
            print("  himalayas parse fail page", i, flush=True)
            break
        jobs = data.get("jobs", [])
        if not jobs:
            break
        for j in jobs:
            title = j.get("title", "")
            sen = " ".join(str(x) for x in (j.get("seniority") or []))
            etype = str(j.get("employmentType") or "")
            locs = " ".join(str(x) for x in (j.get("locationRestrictions") or []))
            tzs = " ".join(str(x) for x in (j.get("timezoneRestrictions") or []))
            loc = locs or "Worldwide"
            blob = f"{title} {sen} {etype} {loc} {tzs} {j.get('excerpt', '')[:300]}"
            if not TECH.search(title):
                continue
            if not (JUNIOR.search(f"{title} {sen} {etype}") or
                    re.search(r"entry|contract|part[\s-]?time|intern", blob, re.I)):
                continue
            if locs and not INDIA_OK.search(f"{loc} {tzs}"):
                continue
            link = j.get("applicationLink") or j.get("guid") or ""
            if link:
                out[link] = row(source="himalayas", title=title, company=j.get("companyName", ""),
                                location=loc, url=link, job_type=etype or "Remote",
                                posted=time.strftime("%Y-%m-%d", time.gmtime(int(j.get("pubDate") or 0))),
                                stipend=(f"{j.get('minSalary') or ''}-{j.get('maxSalary') or ''} "
                                         f"{j.get('currency') or ''}").strip("- "),
                                tags=[x for x in (sen.split() + [etype]) if x][:4])
        cursor = data.get("nextCursor")
        print(f"  himalayas page {i+1}: {len(jobs)} scanned, {len(out)} kept", flush=True)
        if not cursor:
            break
    return list(out.values())


def scan_remoteok():
    out = {}
    try:
        data = json.loads(curl("https://remoteok.com/api", timeout=45))
    except Exception:
        print("  remoteok parse fail", flush=True)
        return []
    for j in data:
        if not isinstance(j, dict) or "position" not in j:
            continue
        title = j.get("position", "")
        tags = j.get("tags") or []
        blob = f"{title} {' '.join(tags)}"
        if not TECH.search(blob):
            continue
        link = j.get("url") or j.get("apply_url") or ""
        if not link:
            continue
        etype = "Remote"
        if re.search(r"part[\s-]?time", blob, re.I):
            etype = "Part-time"
        out[link] = row(source="remoteok", title=title, company=j.get("company", ""),
                        location=j.get("location") or "Worldwide",
                        posted=str(j.get("date", ""))[:10], url=link, job_type=etype,
                        stipend=(f"${j.get('salary_min')}-{j.get('salary_max')}"
                                 if j.get("salary_min") else ""),
                        tags=tags[:6])
    print(f"  remoteok kept {len(out)}", flush=True)
    return list(out.values())


def scan_remotive():
    out = {}
    searches = ["intern", "junior", "entry level", "python", "typescript", "react",
                "node", "golang", "open source", "privacy", "india", "part time"]
    for term in searches:
        url = ("https://remotive.com/api/remote-jobs?limit=100&search="
               + term.replace(" ", "%20"))
        try:
            jobs = json.loads(curl(url)).get("jobs", [])
        except Exception:
            continue
        for j in jobs:
            title = j.get("title", "")
            loc = j.get("candidate_required_location", "") or "Worldwide"
            if not TECH.search(title):
                continue
            if not (JUNIOR.search(f"{title} {j.get('job_type', '')}") or INDIA_OK.search(loc)):
                continue
            link = j.get("url", "")
            if not link:
                continue
            jt = j.get("job_type", "") or "Remote"
            kind = "Part-time" if re.search(r"part|contract|freelance", jt, re.I) else (
                "Internship" if re.search(r"intern", jt, re.I) else "Remote")
            out[link] = row(source="remotive", title=title, company=j.get("company_name", ""),
                            location=loc, posted=str(j.get("publication_date", ""))[:10],
                            url=link, job_type=kind, stipend=j.get("salary", ""),
                            tags=[term] + (j.get("tags") or [])[:4])
        print(f"  remotive[{term}] -> {len(out)} total", flush=True)
        time.sleep(0.5)
    return list(out.values())


def scan_jobicy():
    out = {}
    urls = []
    for page in range(1, 5):
        urls.append(f"https://jobicy.com/api/v2/remote-jobs?count=50&industry=engineering&page={page}")
    urls.append("https://jobicy.com/api/v2/remote-jobs?count=50")
    for url in urls:
        try:
            jobs = json.loads(curl(url)).get("jobs", [])
        except Exception:
            continue
        if not jobs:
            continue
        for j in jobs:
            title = j.get("jobTitle", "")
            if not TECH.search(title):
                continue
            geo = j.get("jobGeo", "") or "Anywhere"
            lvl = j.get("jobLevel", "") or ""
            if not (JUNIOR.search(f"{title} {lvl} {j.get('jobType')}") or INDIA_OK.search(geo)):
                continue
            link = j.get("url", "")
            if not link:
                continue
            jt = " ".join(j.get("jobType") or [])
            kind = "Part-time" if re.search(r"part|contract|freelance", jt, re.I) else "Remote"
            out[link] = row(source="jobicy", title=title, company=j.get("companyName", ""),
                            location=geo, posted=str(j.get("pubDate", ""))[:10], url=link,
                            job_type=kind, tags=[lvl] + (j.get("jobIndustry") or [])[:3])
        print(f"  jobicy [{url.split('?')[-1][:34]}] -> {len(out)} total", flush=True)
        time.sleep(0.5)
    return list(out.values())


def scan_arbeitnow():
    out = {}
    for page in range(1, 4):
        try:
            data = json.loads(curl(f"https://www.arbeitnow.com/api/job-board-api?page={page}"))
        except Exception:
            break
        for j in data.get("data", []):
            if not j.get("remote"):
                continue
            title = j.get("title", "")
            if not TECH.search(title):
                continue
            link = j.get("url", "")
            if not link:
                continue
            jt = " ".join(j.get("job_types") or [])
            kind = "Part-time" if re.search(r"part|contract|freelance", jt, re.I) else "Remote"
            out[link] = row(source="arbeitnow", title=title, company=j.get("company_name", ""),
                            location=j.get("location", "") or "Remote", posted="", url=link,
                            job_type=kind, tags=(j.get("tags") or [])[:5])
        print(f"  arbeitnow page {page} -> {len(out)} total", flush=True)
        time.sleep(0.5)
    return list(out.values())


def scan_weworkremotely():
    out = {}
    feeds = ["https://weworkremotely.com/categories/remote-programming-jobs.rss",
             "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
             "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss"]
    for feed in feeds:
        try:
            root = ET.fromstring(curl(feed))
        except Exception:
            print("  wwr parse fail", feed, flush=True)
            continue
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = clean(item.findtext("description") or "", 400)
            region = item.findtext("region") or ""
            if not link or not TECH.search(title):
                continue
            if not (JUNIOR.search(f"{title} {desc}") or INDIA_OK.search(region + desc)):
                continue
            out[link] = row(source="weworkremotely", title=title,
                            company=title.split(":")[0][:40], location=region or "Remote",
                            posted=(item.findtext("pubDate") or "")[:16], url=link,
                            job_type="Part-time" if re.search(r"part[\s-]?time", desc, re.I) else "Remote",
                            tags=["wwr"])
        print(f"  wwr [{feed.split('/')[-1]}] -> {len(out)} total", flush=True)
    return list(out.values())


def scan_hn_hiring():
    out = {}
    body = curl("https://hn.algolia.com/api/v1/search_by_date?tags=story"
                "&query=%22Ask%20HN%3A%20Who%20is%20hiring%22&hitsPerPage=6")
    try:
        hits = json.loads(body).get("hits", [])
    except Exception:
        return []
    if not hits:
        return []
    sid = hits[0].get("objectID")
    print(f"  HN story: {hits[0].get('title')} ({sid})", flush=True)
    try:
        tree = json.loads(curl(f"https://hn.algolia.com/api/v1/items/{sid}", timeout=45))
    except Exception:
        return []

    def walk(node):
        txt = clean(node.get("text") or "")
        if txt and TECH.search(txt) and JUNIOR.search(txt):
            link = f"https://news.ycombinator.com/item?id={node.get('id')}"
            out[link] = row(source="hn_hiring", title="HN comment: " + txt[:110],
                            company="Hacker News hiring thread", location="see comment",
                            url=link, job_type="Remote/Contract",
                            tags=re.findall(r"\b(intern|junior|entry[\s-]level|part[\s-]?time|contract)\b",
                                            txt, re.I)[:4])
        for ch in node.get("children") or []:
            walk(ch)

    for ch in tree.get("children") or []:
        walk(ch)
    print(f"  hn_hiring kept {len(out)}", flush=True)
    return list(out.values())


def scan_fossjobs():
    out = {}
    for feed in ("https://www.fossjobs.net/rss/all/", "https://www.fossjobs.net/rss/all/?page=2"):
        try:
            root = ET.fromstring(curl(feed, timeout=35))
        except Exception:
            print("  fossjobs parse fail", feed, flush=True)
            continue
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = clean(item.findtext("description") or "", 400)
            if not link or not title:
                continue
            out[link] = row(source="fossjobs", title=title, company="",
                            location="Remote", posted=(item.findtext("pubDate") or "")[:16],
                            url=link, job_type="FOSS",
                            tags=["foss"] + re.findall(r"\b(python|javascript|typescript|go|rust|react|node|linux|devops|security|android)\b", desc, re.I)[:4])
        print(f"  fossjobs [{feed.split('?')[-1]}] -> {len(out)} total", flush=True)
    return list(out.values())


def main():
    rows = []
    for name, fn in [("himalayas", scan_himalayas), ("remoteok", scan_remoteok),
                     ("remotive", scan_remotive), ("jobicy", scan_jobicy),
                     ("arbeitnow", scan_arbeitnow), ("weworkremotely", scan_weworkremotely),
                     ("hn_hiring", scan_hn_hiring), ("fossjobs", scan_fossjobs)]:
        print(f"== {name} ==", flush=True)
        try:
            rows += fn()
        except Exception as exc:
            print("  FAILED", name, exc, flush=True)
    with open(OUT, "w") as fh:
        json.dump(rows, fh, indent=1)
    counts = {}
    for r in rows:
        counts[r["source"]] = counts.get(r["source"], 0) + 1
    print(f"WROTE {OUT}: {len(rows)} rows {counts}", flush=True)


if __name__ == "__main__":
    main()
