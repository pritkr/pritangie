#!/usr/bin/env python3
"""Vet real postings: fetch each posting's text and score disclosed pay,
remote confirmation, student eligibility and stack fit. Output: /tmp/vetted.json"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

def fetch(url, t=15):
    try:
        p = subprocess.run(["curl","-sL","--max-time",str(t),"-A",UA,url],
                           capture_output=True, text=True, timeout=t+5)
        return p.stdout or ""
    except Exception:
        return ""

def text(html):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S|re.I)
    h = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", h, flags=re.I)
    return re.sub(r"[ \t]+", " ", re.sub(r"<[^>]+>", " ", h))

PAY = re.compile(r"(?:₹|rs\.?\s?|inr|\$|usd|eur|€)\s?\d[\d,\.]*\s*(?:k|lakh|lpa)?\s*(?:/|per\s*)?\s*"
                 r"(?:month|mo|year|annum|hour|hr|day|week|month)?|\d[\d,]*\s*(?:per|a)\s*month", re.I)
UNPAID = re.compile(r"unpaid|no stipend|without stipend|voluntary|not paid", re.I)
REMOTE = re.compile(r"work from home|wfh|fully remote|100% remote|remote[- ]first|remote role|"
                    r"work remotely|remote job|anywhere|distributed team|remote position", re.I)
ONSITE = re.compile(r"on[- ]?site|onsite|in[- ]office|mandatory.*office|must be available.*office", re.I)
STUDENT_OK = re.compile(r"fresher|final year|third year|3rd year|undergraduate|student|pursuing|"
                        r"no experience|entry[- ]level|0[- ]?1 year|junior|graduate", re.I)
STACK = re.compile(r"python|javascript|typescript|node(?:\.js)?|react|next\.?js|astro|tailwind|"
                   r"golang|\bgo\b|sql|postgres|supabase|frappe|linux|docker|nginx|api|rest|graphql|"
                   r"scrap|crawl|automation|ci/cd|github actions|ai|llm|agent|prompt", re.I)
NICE = re.compile(r"mentor|mentorship|training|onboarding|certificat|portfolio|github|open source|"
                  r"flexib|async|prepaid|payout|weekly payment", re.I)
BAD = re.compile(r"unpaid|no stipend|commission|target based|field sales|telecalling|"
                 r"data entry|back office|graphic design|video editing|social media", re.I)

def main():
    rows = json.load(open(os.path.join(HERE, "raw-leads-ranked.json")))
    opened = {x.strip() for x in open(os.path.join(HERE, "opened.txt")) if x.strip().startswith("http")}
    EARLY = re.compile(r"intern|trainee|apprentice|graduate|entry|junior|associate|fresher|part[- ]?time", re.I)
    cands = [r for r in rows
             if r["url"] not in opened and EARLY.search(r["title"])
             and r.get("score", 0) >= 12
             and re.search(r"remote|india|worldwide|anywhere|online|apac|work from home|see posting",
                           r.get("location", "") or "", re.I)]
    cands.sort(key=lambda r: -r.get("score", 0))
    cands = cands[:45]
    out = []
    for i, r in enumerate(cands, 1):
        body = text(fetch(r["url"]))
        if len(body) < 300:
            body = (r.get("stipend", "") or "") + " " + r["title"] + " " + (r.get("tags") or [""])[0]
            fetched = False
        else:
            fetched = True
        pay = sorted(set(m.group(0).strip() for m in PAY.finditer(body)))[:4]
        v = dict(r)
        v["pay_found"] = pay
        v["unpaid"] = bool(UNPAID.search(body))
        v["remote_confirmed"] = bool(REMOTE.search(body)) or bool(r.get("remote"))
        v["onsite_flag"] = bool(ONSITE.search(body))
        v["student_ok"] = bool(STUDENT_OK.search(body))
        v["stack_hits"] = sorted({m.group(0).lower() for m in STACK.finditer(body)})[:8]
        v["nice"] = sorted({m.group(0).lower() for m in NICE.finditer(body)})[:5]
        v["text_len"] = len(body)
        v["fetched"] = fetched
        out.append(v)
        print(f"{i:>2}/{len(cands)} {r['source']:<11} {r['title'][:40]:<40} pay={len(pay)} remote={v['remote_confirmed']} student={v['student_ok']} stack={len(v['stack_hits'])}", flush=True)
        time.sleep(0.6)
    json.dump(out, open("/tmp/vetted.json", "w"), indent=1)
    print("WROTE /tmp/vetted.json", len(out), flush=True)

if __name__ == "__main__":
    main()
