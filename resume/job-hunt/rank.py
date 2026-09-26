#!/usr/bin/env python3
"""Rank every scanned lead for Prit's profile: FOSS/privacy-minded 3rd-year CSE
student ('28 batch) wanting remote internships / part-time technical work.

Merges raw-leads.json (LinkedIn/Internshala/Unstop) with raw-leads-extra.json
(Himalayas/RemoteOK/Remotive/Jobicy/Arbeitnow/WWR/HN/fossjobs).
"""
import datetime as dt
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def _p(name):
    return os.path.join(HERE, name)


# --- what he is actually good at / wants ---
STACK = re.compile(
    r"python|typescript|javascript|node(\.js)?|react|next\.?js|astro|tailwind|\bgo\b|golang|"
    r"full[\s-]?stack|back[\s-]?end|front[\s-]?end|web dev|api|rest|graphql|sql|postgres|"
    r"supabase|frappe|linux|arch|docker|kubernetes|nginx|devops|self[\s-]?host|"
    r"browser extension|webextension|manifest v3|firefox|chrome\b|privacy|adblock|security|"
    r"open[\s-]?source|foss|scrap|crawl|parse|ocr|automation|etl|pipeline|data scien|"
    r"machine learning|\bml\b|\bai\b|\bllm\b|rag\b|agent(ic)?|nlp|cloudflare", re.I)
ROLE_OK = re.compile(
    r"intern|trainee|apprentice|graduate|entry[\s-]?level|junior|associate|"
    r"part[\s-]?time|contract|freelance|contributor|fresher|\bii?\b|level 1", re.I)
ENG_TITLE = re.compile(
    r"engineer|developer|programmer|software|swe\b|sde\b|architect|analyst|scientist|"
    r"administrator|sysadmin|devops|sre|qa\b|tester|support|technical|it\b|web|mobile|"
    r"data|security|cloud|platform|infrastructure|automation|research|writer", re.I)
BAD_ROLE = re.compile(
    r"senior|staff|principal|director|manager|head of|\bvp\b|chief|lead\b|architect|"
    r"marketing|sales|business development|\bhr\b|human resource|content writ|copywrit|"
    r"social media|influencer|account(ing)?|finance|recruit|telecall|campus ambassador|"
    r"graphic design|video edit|\bseo\b|field|nurse|teacher|driver|internship in finance|"
    r"data entry|typing|fundrais|operations manager|customer care", re.I)
REMOTE_OK = re.compile(r"remote|anywhere|worldwide|global|india|asia|apac|ist\b|work from home|wfh", re.I)
PAID = re.compile(r"₹|rs\.?\s?\d|\$\s?\d|\d{4,}|/month|per month|stipend|salary", re.I)
UNPAID = re.compile(r"unpaid|no stipend|volunteer", re.I)
DREAM = re.compile(
    r"brave|proton|supabase|canonical|appwrite|cal\.com|appsmith|chatwoot|tooljet|hoppscotch|"
    r"mattermost|gitlab|automattic|posthog|grafana|hasura|directus|nhost|twenty|tailscale|"
    r"cloudflare|sentry|snyk|bitwarden|1password|mozilla|duckduckgo|tutanota|mullvad|"
    r"ente|tattle|pinaca|zingg|frappe|zulip|open ?source|foss united|freedom|tor project|"
    r"element|matrix|nextcloud|kagi|vivaldi|ecosia", re.I)
# remote-hiring employer boards (their roles are remote-friendly by default;
# rank.py scores their location from tags instead of the title string)
CONTRACTOR = ("mercor", "scale ai", "turing", "labelbox", "toloka")

TODAY = dt.date.today()


def days_old(posted):
    s = (posted or "")[:10]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return (TODAY - dt.datetime.strptime(s, fmt).date()).days
        except Exception:
            continue
    return None


def score(r):
    title = r.get("title", "")
    blob = " ".join([title, r.get("company", ""), r.get("location", ""),
                     " ".join(r.get("tags") or []), r.get("stipend", "")])
    s = 0
    stack = len(set(m.group(0).lower() for m in STACK.finditer(blob)))
    s += min(stack, 6)
    if ENG_TITLE.search(title):
        s += 3
    if ROLE_OK.search(title) or r.get("job_type") in ("Internship", "Part-time"):
        s += 5
    if r.get("remote"):
        s += 2
    if REMOTE_OK.search(blob):
        s += 2
    if DREAM.search(blob):
        s += 4
    if r.get("stipend") and PAID.search(r["stipend"]) and not UNPAID.search(r["stipend"]):
        s += 3
    if UNPAID.search(blob):
        s -= 6
    if r.get("source") == "internshala" and r.get("stipend") and "unpaid" in r["stipend"].lower():
        s -= 4
    co = (r.get("company") or "").lower()
    if r.get("source") == "contractor" and any(x in co for x in CONTRACTOR):
        s += 3  # remote-friendly AI/data contracting: keep exploring details
    if BAD_ROLE.search(title):
        s -= 12
    # company named after a city/state where the candidate does NOT live is
    # usually a location string pasted into the title: drop those rows hard
    if re.search(r"\b(new york|los angeles|san francisco|austin|boston|seattle|"
                 r"london|dublin|berlin|singapore|dubai|toronto|vancouver)\b", title, re.I):
        s -= 15
    d = days_old(r.get("posted"))
    if d is not None:
        r["age_days"] = d
        if d <= 7:
            s += 3
        elif d <= 30:
            s += 2
        elif d > 180:
            s -= 3
    if not r.get("url", "").startswith("http"):
        s -= 50
    return s


def main():
    rows = []
    for f in ("raw-leads.json", "raw-leads-extra.json"):
        path = _p(f)
        if os.path.exists(path):
            data = json.load(open(path))
            rows += data
            print(f"loaded {len(data):>5} rows from {f}")
    for r in rows:
        r["score"] = score(r)
    seen, uniq = set(), []
    for r in sorted(rows, key=lambda x: -x["score"]):
        if r["score"] <= -10:
            continue
        key = (re.sub(r"\W+", "", r["title"].lower())[:60],
               re.sub(r"\W+", "", (r.get("company") or "").lower())[:30])
        if key in seen:
            prev = next(x for x in uniq if x["_key"] == key)
            for t in r.get("tags") or []:
                if t not in prev["tags"]:
                    prev["tags"].append(t)
            continue
        seen.add(key)
        r["_key"] = key
        uniq.append(r)
    for r in uniq:
        r.pop("_key", None)
    json.dump(uniq, open(_p("raw-leads-ranked.json"), "w"), indent=1)
    counts = {}
    for r in uniq:
        counts[r["source"]] = counts.get(r["source"], 0) + 1
    print(f"\n{len(uniq)} unique leads kept")
    print("by source:", counts)
    print("score >=12:", sum(1 for r in uniq if r["score"] >= 12),
          "| >=8:", sum(1 for r in uniq if r["score"] >= 8))
    for r in uniq[:25]:
        print(f"  [{r['score']:>2}] {r['source'][:9]:<9} {r['title'][:58]:<58} @ {(r.get('company') or '')[:26]}")


if __name__ == "__main__":
    main()
