#!/usr/bin/env python3
"""Deep expansion of global remote sources: ALL WeWorkRemotely categories, full
RemoteOK feed, full Remotive feed, deep cursor paging through Himalayas.

Writes raw-leads-extra.json (merged, URL-deduped)."""
import html as htmlmod
import json
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
OUT = os.path.join(HERE, "raw-leads-extra.json")

TECH = re.compile(
    r"engineer|developer|programmer|software|swe\b|sde\b|architect|analyst|scientist|"
    r"administrator|sysadmin|devops|sre|qa\b|tester|support|technical|\bit\b|web|mobile|"
    r"data|security|cloud|platform|infrastructure|automation|research|writer|linux|"
    r"python|javascript|typescript|node|react|golang|\bgo\b|api|devrel|advocate|"
    r"solutions engineer|implementer|integrator", re.I)
ENTRY = re.compile(r"intern|trainee|apprentice|graduate|entry|junior|associate|fresher|"
                   r"part[\s-]?time|contract|freelance|contributor|mid[- ]?level|\bii\b|\bi\b", re.I)


def curl(url, timeout=30):
    try:
        return subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", UA, url],
                              capture_output=True, text=True).stdout or ""
    except Exception:
        return ""


def clean(t):
    return re.sub(r"\s+", " ", htmlmod.unescape(t or "")).strip()


def row(**kw):
    base = {"source": "", "title": "", "company": "", "location": "", "stipend": "",
            "duration": "", "posted": "", "url": "", "job_type": "Remote",
            "remote": True, "tags": []}
    base.update(kw)
    return base


def scan_wwr():
    cats = ["remote-programming", "remote-devops-sysadmin", "remote-full-stack-programming",
            "remote-data", "remote-data-engineering", "remote-product", "remote-engineering",
            "remote-c-plus-plus", "remote-java", "remote-python", "remote-rust", "remote-golang",
            "remote-php", "remote-ruby", "remote-embedded", "remote-qa", "remote-security",
            "remote-ml", "remote-ai", "remote-devops", "remote-ansible", "remote-terraform",
            "remote-kubernetes", "remote-sales-engineering", "remote-solutions-engineering"]
    out = {}
    for c in dict.fromkeys(cats):
        body = curl(f"https://weworkremotely.com/categories/{c}-jobs.rss", 20)
        if "<item>" not in body:
            continue
        try:
            root = ET.fromstring(body)
        except Exception:
            continue
        n = 0
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = clean(item.findtext("description") or "")[:400]
            region = item.findtext("region") or ""
            if not link or not TECH.search(f"{title} {desc}"):
                continue
            company = title.split(":")[0].strip() if ":" in title else ""
            if len(company) > 42:
                company = ""
            out[link] = row(source="weworkremotely", title=title, company=company,
                            location=region or "Remote",
                            posted=(item.findtext("pubDate") or "")[:16], url=link,
                            job_type="Contract" if re.search(r"contract|freelance|part", desc, re.I) else "Remote",
                            tags=[c.replace("remote-", "")])
            n += 1
        if n:
            print(f"  wwr[{c}] -> {n} (total {len(out)})", flush=True)
    return list(out.values())


def scan_remoteok():
    body = curl("https://remoteok.com/api", 45)
    try:
        data = json.loads(body)
    except Exception:
        return []
    out = {}
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
        loc = j.get("location") or "Worldwide"
        etype = "Contract" if re.search(r"contract|freelance|part", blob, re.I) else "Remote"
        out[link] = row(source="remoteok", title=title, company=j.get("company", ""),
                        location=loc, posted=str(j.get("date", ""))[:10], url=link,
                        job_type=etype,
                        stipend=(f"${j.get('salary_min')}-{j.get('salary_max')}" if j.get("salary_min") else ""),
                        tags=tags[:6])
    print(f"  remoteok kept {len(out)}", flush=True)
    return list(out.values())


def scan_remotive():
    out = {}
    body = curl("https://remotive.com/api/remote-jobs?limit=1000", 40)
    try:
        jobs = json.loads(body).get("jobs", [])
    except Exception:
        return []
    for j in jobs:
        title = j.get("title", "")
        loc = j.get("candidate_required_location", "") or "Worldwide"
        if not TECH.search(title):
            continue
        link = j.get("url", "")
        if not link:
            continue
        jt = j.get("job_type", "") or "Remote"
        kind = "Contract" if re.search(r"part|contract|freelance", jt, re.I) else "Remote"
        out[link] = row(source="remotive", title=title, company=j.get("company_name", ""),
                        location=loc, posted=str(j.get("publication_date", ""))[:10],
                        url=link, job_type=kind, stipend=j.get("salary", ""),
                        tags=(j.get("tags") or [])[:5])
    print(f"  remotive kept {len(out)}", flush=True)
    return list(out.values())


def scan_himalayas(pages=90):
    out, cursor = {}, None
    for i in range(pages):
        url = "https://himalayas.app/jobs/api?limit=100" + (f"&cursor={cursor}" if cursor else "")
        body = curl(url, 25)
        try:
            data = json.loads(body)
        except Exception:
            break
        jobs = data.get("jobs", [])
        if not jobs:
            break
        for j in jobs:
            title = j.get("title", "")
            if not TECH.search(title):
                continue
            sen = " ".join(str(x) for x in (j.get("seniority") or []))
            etype = str(j.get("employmentType") or "")
            if not (ENTRY.search(f"{title} {sen} {etype}") or re.search(r"entry|mid", sen, re.I)):
                continue
            link = j.get("applicationLink") or j.get("guid") or ""
            if not link:
                continue
            loc = " ".join(str(x) for x in (j.get("locationRestrictions") or [])) or "Worldwide"
            out[link] = row(source="himalayas", title=title, company=j.get("companyName", ""),
                            location=loc, url=link, job_type=etype or "Remote",
                            posted=time.strftime("%Y-%m-%d", time.gmtime(int(j.get("pubDate") or 0))),
                            stipend=(f"{j.get('minSalary') or ''}-{j.get('maxSalary') or ''} {j.get('currency') or ''}").strip("- "),
                            tags=[x for x in (sen.split() + [etype]) if x][:4])
        cursor = data.get("nextCursor")
        if i % 10 == 0:
            print(f"  himalayas page {i+1}: {len(out)} kept", flush=True)
        if not cursor:
            break
        time.sleep(0.2)
    print(f"  himalayas total {len(out)}", flush=True)
    return list(out.values())


def merge(new):
    old = json.load(open(OUT)) if os.path.exists(OUT) else []
    seen = {r.get("url"): r for r in old}
    added = sum(1 for r in new if r.get("url") and r.get("url") not in seen and not seen.setdefault(r["url"], r))
    rows = list(seen.values())
    json.dump(rows, open(OUT, "w"), indent=1)
    return len(old), len(rows), added


def main():
    for name, fn in [("weworkremotely", scan_wwr), ("remoteok", scan_remoteok),
                     ("remotive", scan_remotive), ("himalayas", scan_himalayas)]:
        print(f"== {name} ==", flush=True)
        try:
            rows = fn()
        except Exception as exc:
            print("  FAILED", name, exc, flush=True)
            rows = []
        a, b, c = merge(rows)
        print(f"  merged: {a} -> {b} (+{c} new from {name})", flush=True)


if __name__ == "__main__":
    main()
