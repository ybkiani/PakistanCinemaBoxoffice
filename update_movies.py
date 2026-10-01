#!/usr/bin/env python3
"""
Pakistan Cinema daily updater.
Conservative by design: a failed scrape NEVER wipes the last healthy feed.
It checks configured public cinema pages for movie-title candidates and preserves
the curated/previous records unless it has enough confidence to update them.
"""
from __future__ import annotations
import json, re, html, hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"movies.json"
PKT=timezone(timedelta(hours=5))

SOURCES=[
 {"name":"Showtimes.pk","url":"https://www.showtimes.pk/"},
 {"name":"Cinepax","url":"https://cinepax.com/Browsing/Movies/NowShowing"},
 {"name":"Universal Cinemas","url":"https://universalcinemas.com/Browsing/Movies/NowShowing"},
 {"name":"ME Cinemas","url":"https://www.mecinemas.com/movies.php"},
 {"name":"CineStar","url":"https://cinestar.pk/Browsing/Movies/NowShowing"},
]

def fetch(url):
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 PakistanCinemaBoxoffice/1.0"})
    with urlopen(req,timeout=25) as r:
        return r.read().decode("utf-8","ignore")

def clean(s):
    s=re.sub(r"<[^>]+>"," ",s)
    return re.sub(r"\s+"," ",html.unescape(s)).strip()

def load_old():
    try: return json.loads(OUT.read_text(encoding="utf-8"))
    except Exception: return {"movies":[],"sources":SOURCES}

def candidate_titles(page):
    # Generic discovery only. Existing records remain authoritative until a source
    # provides a recognizable title match. This prevents navigation labels from
    # becoming fake movies when cinema markup changes.
    patterns=[
      r'<h[1-4][^>]*>(.*?)</h[1-4]>',
      r'class=["\'][^"\']*(?:movie|film)[^"\']*(?:title|name)[^"\']*["\'][^>]*>(.*?)</',
      r'class=["\'][^"\']*(?:title|name)[^"\']*["\'][^>]*>(.*?)</'
    ]
    out=[]
    blacklist={"now showing","coming soon","movies","cinemas","book now","buy tickets","home","contact us","about us"}
    for p in patterns:
        for raw in re.findall(p,page,re.I|re.S):
            t=clean(raw)
            if 2<len(t)<80 and t.lower() not in blacklist and not re.search(r"\b(login|register|privacy|terms)\b",t,re.I):
                out.append(t)
    return list(dict.fromkeys(out))

def main():
    old=load_old()
    movies=old.get("movies",[])
    reports=[]
    discovered=[]
    for src in SOURCES:
        try:
            page=fetch(src["url"])
            titles=candidate_titles(page)
            discovered += titles
            reports.append({**src,"ok":True,"candidates":len(titles)})
        except Exception as e:
            reports.append({**src,"ok":False,"error":str(e)[:120]})
    # Confirm presence of known titles without inventing records from weak generic markup.
    norm=lambda x: re.sub(r"[^a-z0-9]","",x.lower())
    found={norm(x) for x in discovered}
    for m in movies:
        if norm(m.get("title","")) in found:
            m["seen_in_latest_scan"]=True
    payload={
      "last_updated":datetime.now(PKT).isoformat(timespec="seconds"),
      "update_status":"success" if any(x.get("ok") for x in reports) else "sources_unavailable_previous_data_retained",
      "sources":[{"name":x["name"],"url":x["url"]} for x in SOURCES],
      "source_health":reports,
      "movies":movies
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Wrote {OUT}; {len(movies)} retained movies; {sum(x.get('ok',False) for x in reports)}/{len(reports)} sources reachable.")

if __name__=="__main__":
    main()
