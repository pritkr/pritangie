#!/usr/bin/env python3
"""Render the scanned+ranked listings into a compact markdown shortlist."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def _p(name):
    return os.path.join(HERE, name)


rows = json.load(open(_p("raw-leads-ranked.json")))


def keep(r):
    t = r["title"].lower()
    if r["source"] == "linkedin":
        # guest API ignores the part-time filter: drop mislabelled full-time rows
        return "intern" in t and r["score"] >= 7
    if r["source"] == "internshala":
        return r["score"] >= 9
    if r["source"] == "unstop":
        return r["remote"] and r["score"] >= 6
    return False


sections = [
    ("Internshala — work-from-home / part-time tech internships (paid listed)",
     [r for r in rows if r["source"] == "internshala" and keep(r)][:30]),
    ("Unstop — online / remote internships", [r for r in rows if r["source"] == "unstop" and keep(r)][:25]),
    ("LinkedIn — internship postings (verify remote status on the posting)",
     [r for r in rows if r["source"] == "linkedin" and keep(r)][:30]),
]

out = ["# Auto-generated shortlist — scanned 2026-09-24\n",
       "Sources: LinkedIn public jobs API (286 rows), Internshala (297), Unstop (56). "
       "Scored for remote / paid / software-engineering fit; the full raw data is in "
       "`raw-leads.json`.\n"]

for title, items in sections:
    out.append(f"\n## {title}\n")
    out.append("| Role | Org | Pay | Duration | Type | Link |")
    out.append("|---|---|---|---|---|---|")
    for r in items:
        pay = (r.get("stipend") or "—").replace("|", "/")
        dur = (r.get("duration") or "—").replace("|", "/")
        loc = (r.get("location") or "").replace("|", "/")
        if r["source"] == "linkedin" and loc:
            dur = loc
        out.append(f"| {r['title'][:70]} | {r['company'][:34]} | {pay[:22]} | {dur[:24]} | "
                   f"{r['job_type']} | [open]({r['url']}) |")

with open(_p("leads-shortlist.md"), "w") as fh:
    fh.write("\n".join(out) + "\n")
print("wrote leads-shortlist.md", sum(len(i) for _, i in sections), "rows")
