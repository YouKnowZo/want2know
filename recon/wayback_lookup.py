#!/usr/bin/env python3
import sys
import json

def lookup(target):
    result = {"target": target, "snapshots": [], "count": 0,
              "first": None, "last": None, "error": ""}
    try:
        import requests
        target = target.strip()
        if not target.startswith("http"):
            target = "http://" + target
        # CDX API: list of snapshots
        r = requests.get(
            "https://web.archive.org/cdx/search/cdx",
            params={"url": target, "output": "json", "limit": -50,
                    "fl": "timestamp,original,statuscode,mimetype",
                    "filter": "statuscode:200", "collapse": "timestamp:6"},
            headers={"User-Agent": "Want2Know-OSINT/1.0"},
            timeout=25
        )
        if r.status_code != 200:
            result["error"] = f"Wayback returned status {r.status_code}"
            print(json.dumps(result)); return
        rows = r.json()
        if len(rows) <= 1:
            result["error"] = "No snapshots found in the Wayback Machine"
            print(json.dumps(result)); return
        # rows[0] is header
        for row in rows[1:]:
            ts, orig, status, mime = row
            year, month, day = ts[:4], ts[4:6], ts[6:8]
            result["snapshots"].append({
                "timestamp": ts,
                "date": f"{year}-{month}-{day}",
                "url": f"https://web.archive.org/web/{ts}/{orig}",
                "original": orig,
                "status": status,
                "mime": mime,
            })
        result["count"] = len(result["snapshots"])
        result["first"] = result["snapshots"][0]["date"]
        result["last"] = result["snapshots"][-1]["date"]
    except Exception as e:
        result["error"] = str(e)
    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error":"No URL provided"}))
    else:
        lookup(sys.argv[1])
