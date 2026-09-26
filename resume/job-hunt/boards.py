#!/usr/bin/env python3
"""Query public job-board APIs (Ashby + Greenhouse) of OSS / privacy /
devtools companies.

Writes:
  board-hits.json    - intern/entry-title roles (any location)
  board-focus.json   - remote/India/worldwide engineering roles that aren't senior-only
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def _p(name):
    return os.path.join(HERE, name)


UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

ASHBY = ["supabase", "posthog", "twenty", "linear", "resend", "railway", "deno"]
GREENHOUSE = ["brave", "bitwarden", "a16z", "mattermost", "gitlab", "canonical",
              "cloudflare", "proton", "tailscale", "elastic", "vercel", "netlify",
              "sentry", "n8n", "grafana", "mongodb", "redis", "render", "deno",
              "chainlink", "solana", "twilio", "duckduckgo", "automattic", "mozilla"]

KEY = re.compile(r"intern|trainee|graduate|entry[- ]level|junior|associate|"
                 r"apprentice|fellow", re.I)
REMOTE = re.compile(r"remote|anywhere|worldwide|distributed|india|apac|home based", re.I)
SENIOR = re.compile(r"senior|staff|principal|director|manager|head of|\bvp\b|chief|"
                    r"\blead\b|architect|\bsr\.?\b", re.I)
ENG = re.compile(r"engineer|developer|software|sre|devops|security|linux|data|"
                 r"support|qa|platform|infrastructure|research|developer advocate|"
                 r"technical writer|solutions", re.I)


def curl(url, timeout=25):
    try:
        return subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", UA, url],
                              capture_output=True, text=True).stdout
    except Exception:
        return ""


def ashby(slug):
    try:
        return json.loads(curl(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")).get("jobs", [])
    except Exception:
        return []


def greenhouse(slug):
    try:
        return json.loads(curl(
            f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=false")).get("jobs", [])
    except Exception:
        return []


def main():
    live, hits, focus = [], [], []
    seen_hit, seen_focus = set(), set()

    for slug in ASHBY:
        jobs = ashby(slug)
        if jobs:
            live.append(f"ashby:{slug}({len(jobs)})")
        for j in jobs:
            t, loc, u = j.get("title", ""), (j.get("location") or ""), j.get("jobUrl", "")
            if not u:
                continue
            if KEY.search(t) and u not in seen_hit:
                seen_hit.add(u)
                hits.append(["ashby:" + slug, t, loc, u])
            if REMOTE.search(loc) and ENG.search(t) and not SENIOR.search(t) and u not in seen_focus:
                seen_focus.add(u)
                focus.append(["ashby:" + slug, t, loc, u])

    for slug in GREENHOUSE:
        jobs = greenhouse(slug)
        if jobs:
            live.append(f"gh:{slug}({len(jobs)})")
        for j in jobs:
            t = j.get("title", "")
            loc = (j.get("location") or {}).get("name") or ""
            u = j.get("absolute_url", "")
            if not u:
                continue
            if KEY.search(t) and u not in seen_hit:
                seen_hit.add(u)
                hits.append(["gh:" + slug, t, loc, u])
            if REMOTE.search(loc) and ENG.search(t) and not SENIOR.search(t) and u not in seen_focus:
                seen_focus.add(u)
                focus.append(["gh:" + slug, t, loc, u])

    json.dump(hits, open(_p("board-hits.json"), "w"), indent=1)
    json.dump(focus, open(_p("board-focus.json"), "w"), indent=1)
    print("LIVE BOARDS:", " ".join(live))
    print(f"{len(hits)} intern/entry hits -> board-hits.json")
    print(f"{len(focus)} remote engineering roles -> board-focus.json")
    for src, t, loc, u in focus[:30]:
        print(f"  [{src}] {t} | {loc}")


if __name__ == "__main__":
    main()
