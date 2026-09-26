#!/usr/bin/env python3
"""Multi-source internship/job scanner (no login required).

Sources:
  * LinkedIn public "jobs-guest" search API (remote + internship/part-time)
  * Internshala work-from-home / part-time category pages
  * Unstop public opportunity search API
Fetching uses curl (system trust store); parsing uses BeautifulSoup.
"""
import html as htmlmod
import json
import os
import re
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
def _p(name):
    return os.path.join(HERE, name)

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
_P = _p
OUT = _P("raw-leads.json")

TECH_RX = re.compile(
    r"python|javascript|typescript|node|react|next\.?js|full[\s-]?stack|back[\s-]?end|"
    r"front[\s-]?end|web dev|software|developer|programmer|data scien|data engineer|"
    r"machine learning|\bml\b|\bai\b|nlp|devops|cloud|linux|docker|kubernetes|security|"
    r"cyber|blockchain|android|flutter|api|sql|automation|scrap|open[\s-]?source|"
    r"technical writer|\bqa\b|test|site reliability|platform|infrastructure",
    re.I)


def curl(url, headers=(), timeout=30):
    cmd = ["curl", "-sL", "--max-time", str(timeout), "-A", UA]
    for k, v in headers:
        cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout
    except Exception as exc:
        print("curl failed", url, exc, flush=True)
        return ""


def clean(txt):
    return re.sub(r"\s+", " ", htmlmod.unescape(txt or "")).strip()


LINKEDIN_COMBOS = [
    # --- internships, India (remote) ---
    ("SWE Intern", "India", "I", "2"),
    ("Software Developer Intern", "India", "I", "2"),
    ("Software Engineer Intern", "India", "I", "2"),
    ("Software Development Intern", "India", "I", "2"),
    ("Python Developer Intern", "India", "I", "2"),
    ("Python Intern", "India", "I", "2"),
    ("Backend Developer Intern", "India", "I", "2"),
    ("Backend Intern", "India", "I", "2"),
    ("Frontend Developer Intern", "India", "I", "2"),
    ("Frontend Intern", "India", "I", "2"),
    ("React Developer Intern", "India", "I", "2"),
    ("Node.js Developer Intern", "India", "I", "2"),
    ("Full Stack Developer Intern", "India", "I", "2"),
    ("Web Developer Intern", "India", "I", "2"),
    ("Data Analyst Intern", "India", "I", "2"),
    ("Data Engineer Intern", "India", "I", "2"),
    ("Data Science Intern", "India", "I", "2"),
    ("Machine Learning Intern", "India", "I", "2"),
    ("AI Intern", "India", "I", "2"),
    ("DevOps Intern", "India", "I", "2"),
    ("Cloud Intern", "India", "I", "2"),
    ("Cyber Security Intern", "India", "I", "2"),
    ("Information Security Intern", "India", "I", "2"),
    ("QA Intern", "India", "I", "2"),
    ("Software Testing Intern", "India", "I", "2"),
    ("Android Developer Intern", "India", "I", "2"),
    ("Flutter Intern", "India", "I", "2"),
    ("Open Source", "India", "I", "2"),
    ("Technical Writer Intern", "India", "I", "2"),
    ("Product Engineer Intern", "India", "I", "2"),
    ("Automation Intern", "India", "I", "2"),
    ("IT Support Intern", "India", "I", "2"),
    ("Linux Administrator Intern", "India", "I", "2"),
    ("Golang Developer Intern", "India", "I", "2"),
    # --- part-time, India (remote) ---
    ("Software Developer", "India", "P", "2"),
    ("Python Developer", "India", "P", "2"),
    ("Web Developer", "India", "P", "2"),
    ("Frontend Developer", "India", "P", "2"),
    ("Backend Developer", "India", "P", "2"),
    ("React Developer", "India", "P", "2"),
    ("Data Analyst", "India", "P", "2"),
    ("DevOps Engineer", "India", "P", "2"),
    ("Technical Support", "India", "P", "2"),
    ("Technical Writer", "India", "P", "2"),
    # --- internships, worldwide remote ---
    ("Software Engineer Intern", "", "I", "2"),
    ("Backend Intern", "", "I", "2"),
    ("Open Source Intern", "", "I", "2"),
    ("Python Intern", "", "I", "2"),
    ("Developer Intern", "", "I", "2"),
]


def scan_linkedin():
    from bs4 import BeautifulSoup
    out = {}
    base = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    for kw, loc, jt, wt in LINKEDIN_COMBOS:
        for start in (0, 25, 50):
            url = (f"{base}?keywords={kw.replace(' ', '%20')}&location={loc}"
                   f"&f_JT={jt}&f_WT={wt}&sortBy=DD&start={start}")
            body = curl(url, [("Accept", "text/html")])
            if "<li" not in body:
                continue
            soup = BeautifulSoup(body, "lxml")
            for card in soup.select("li"):
                a = card.select_one("a.base-card__full-link")
                title = card.select_one(".base-search-card__title")
                comp = card.select_one(".base-search-card__subtitle")
                loc_el = card.select_one(".job-search-card__location")
                date_el = card.select_one("time")
                if not (a and title):
                    continue
                link = a.get("href", "").split("?")[0]
                if not link:
                    continue
                rec = {
                    "source": "linkedin",
                    "title": clean(title.get_text()),
                    "company": clean(comp.get_text()) if comp else "",
                    "location": clean(loc_el.get_text()) if loc_el else "",
                    "stipend": "",
                    "duration": "",
                    "posted": (date_el.get("datetime") if date_el else "") or "",
                    "url": link,
                    "job_type": "Internship" if jt == "I" else "Part-time",
                    "remote": True,
                    "tags": [kw],
                }
                out[link] = rec
        print(f"  linkedin[{kw}/{loc or 'worldwide'}/{'intern' if jt == 'I' else 'part-time'}] -> {len(out)} total", flush=True)
        time.sleep(1)
    return list(out.values())


INTERNSHALA_PAGES = [
    ("Web Development", "https://internshala.com/internships/work-from-home-web-development-internships/"),
    ("Web Development p2", "https://internshala.com/internships/work-from-home-web-development-internships/page-2/"),
    ("Software Development", "https://internshala.com/internships/work-from-home-software-development-internships/"),
    ("Software Development p2", "https://internshala.com/internships/work-from-home-software-development-internships/page-2/"),
    ("Front End Development", "https://internshala.com/internships/work-from-home-front-end-development-internships/"),
    ("Backend Development", "https://internshala.com/internships/work-from-home-backend-development-internships/"),
    ("Node JS Development", "https://internshala.com/internships/work-from-home-node-js-development-internships/"),
    ("Data Science", "https://internshala.com/internships/work-from-home-data-science-internships/"),
    ("Machine Learning", "https://internshala.com/internships/work-from-home-machine-learning-internships/"),
    ("Artificial Intelligence", "https://internshala.com/internships/work-from-home-artificial-intelligence-internships/"),
    ("Data Analytics", "https://internshala.com/internships/work-from-home-data-analytics-internships/"),
    ("Cyber Security", "https://internshala.com/internships/work-from-home-cyber-security-internships/"),
    ("DevOps", "https://internshala.com/internships/work-from-home-devops-internships/"),
    ("Programming", "https://internshala.com/internships/work-from-home-programming-internships/"),
    ("Software Testing", "https://internshala.com/internships/work-from-home-software-testing-internships/"),
    ("Android App Development", "https://internshala.com/internships/work-from-home-android-app-development-internships/"),
    ("Flutter Development", "https://internshala.com/internships/work-from-home-flutter-development-internships/"),
    ("PHP Development", "https://internshala.com/internships/work-from-home-php-development-internships/"),
    ("WordPress Development", "https://internshala.com/internships/work-from-home-wordpress-development-internships/"),
    ("Technical Writing", "https://internshala.com/internships/work-from-home-technical-writing-internships/"),
    ("UI/UX Design", "https://internshala.com/internships/work-from-home-ui-ux-design-internships/"),
    ("All WFH internships", "https://internshala.com/internships/work-from-home-internships/"),
    ("All WFH internships p2", "https://internshala.com/internships/work-from-home-internships/page-2/"),
    ("JavaScript Development", "https://internshala.com/internships/work-from-home-javascript-development-internships/"),
    ("Full Stack Development", "https://internshala.com/internships/work-from-home-full-stack-development-internships/"),
    ("Cloud Computing", "https://internshala.com/internships/work-from-home-cloud-computing-internships/"),
    ("Information Technology", "https://internshala.com/internships/work-from-home-information-technology-internships/"),
    ("Product Management", "https://internshala.com/internships/work-from-home-product-management-internships/"),
    ("Backend Development p2", "https://internshala.com/internships/work-from-home-backend-development-internships/page-2/"),
    ("Data Science p2", "https://internshala.com/internships/work-from-home-data-science-internships/page-2/"),
    ("Cyber Security p2", "https://internshala.com/internships/work-from-home-cyber-security-internships/page-2/"),
    ("SW Dev Part-time", "https://internshala.com/internships/part-time-software-development-internships/"),
    ("Web Dev Part-time", "https://internshala.com/internships/part-time-web-development-internships/"),
]


def scan_internshala():
    from bs4 import BeautifulSoup
    out = {}
    for label, url in INTERNSHALA_PAGES:
        body = curl(url, [("Accept", "text/html")], timeout=35)
        if "individual_internship" not in body:
            print(f"  internshala[{label}] -> no cards", flush=True)
            continue
        soup = BeautifulSoup(body, "lxml")
        n = 0
        for card in soup.select("div.individual_internship"):
            a = card.select_one("a.job-title-href")
            if not a:
                continue
            href = a.get("href", "")
            link = ("https://internshala.com" + href) if href.startswith("/") else href
            text = clean(card.get_text(" "))
            comp = card.select_one("p.company-name")
            stipend = card.select_one(".stipend")
            loc_el = card.select_one(".locations")
            dur = ""
            for row in card.select(".row-1-item"):
                if row.select_one("i.ic-16-calendar"):
                    dur = clean(row.get_text())
            key = link.split("?")[0]
            if key in out:
                out[key]["tags"] = sorted(set(out[key]["tags"] + [label]))
                continue
            out[key] = {
                "source": "internshala",
                "title": clean(a.get_text()),
                "company": clean(comp.get_text()) if comp else "",
                "location": clean(loc_el.get_text()) if loc_el else "",
                "stipend": clean(stipend.get_text()) if stipend else "",
                "duration": dur,
                "posted": "",
                "url": link,
                "job_type": "Part-time" if re.search(r"part[\s-]?time", text, re.I) else "Internship",
                "remote": "work from home" in text.lower(),
                "tags": [label],
            }
            n += 1
        print(f"  internshala[{label}] -> {n} new (total {len(out)})", flush=True)
        time.sleep(1)
    return list(out.values())


def scan_unstop():
    out = {}
    for page in range(1, 16):
        url = ("https://unstop.com/api/public/opportunity/search-result?"
               f"opportunity=internships&per_page=30&page={page}&sortBy=recent")
        body = curl(url, [("Accept", "application/json")])
        try:
            data = json.loads(body).get("data", {}).get("data", [])
        except Exception:
            print("  unstop page", page, "parse fail", flush=True)
            break
        if not data:
            break
        for item in data:
            title = clean(item.get("title", ""))
            org = item.get("organisation") if isinstance(item.get("organisation"), dict) else {}
            skills = [s.get("skill_name", "") for s in (item.get("required_skills") or []) if isinstance(s, dict)]
            blob = f"{title} {' '.join(skills)} {str(item.get('details', ''))[:500]}"
            if not TECH_RX.search(blob):
                continue
            link = item.get("seo_url") or item.get("short_url") or ""
            if not link:
                continue
            out[link] = {
                "source": "unstop",
                "title": title,
                "company": clean(org.get("name", "")),
                "location": "Online/Remote" if item.get("region") == "online" else str(item.get("region") or ""),
                "stipend": "paid" if str(item.get("isPaid")) == "True" else "",
                "duration": "",
                "posted": str(item.get("approved_date") or item.get("updated_at") or "")[:10],
                "url": link,
                "job_type": "Internship",
                "remote": item.get("region") == "online",
                "tags": [s for s in skills if s][:6],
            }
        print(f"  unstop page {page} -> total {len(out)}", flush=True)
        time.sleep(1)
    return list(out.values())


def main():
    rows = []
    print("== linkedin ==", flush=True)
    rows += scan_linkedin()
    print("== internshala ==", flush=True)
    rows += scan_internshala()
    print("== unstop ==", flush=True)
    rows += scan_unstop()
    with open(OUT, "w") as fh:
        json.dump(rows, fh, indent=1)
    counts = {s: sum(1 for r in rows if r["source"] == s) for s in ("linkedin", "internshala", "unstop")}
    print(f"WROTE {OUT}: {len(rows)} rows {counts}", flush=True)


if __name__ == "__main__":
    main()
