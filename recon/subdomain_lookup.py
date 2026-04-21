#!/usr/bin/env python3
import sys
import json

def lookup(domain):
    result = {"domain": domain, "subdomains": [], "count": 0, "source": "crt.sh", "error": ""}
    try:
        import requests
        domain = domain.strip().lower().replace("https://","").replace("http://","").split("/")[0]
        result["domain"] = domain
        r = requests.get(
            f"https://crt.sh/?q=%25.{domain}&output=json",
            headers={"User-Agent": "Want2Know-OSINT/1.0"},
            timeout=15
        )
        if r.status_code != 200:
            result["error"] = f"crt.sh returned status {r.status_code}"
            print(json.dumps(result)); return

        try:
            data = r.json()
        except Exception:
            result["error"] = "Could not parse crt.sh response"
            print(json.dumps(result)); return

        seen = set()
        for entry in data:
            name = entry.get("name_value", "")
            for sub in name.split("\n"):
                sub = sub.strip().lower().lstrip("*.")
                if sub and sub.endswith(domain) and sub not in seen:
                    seen.add(sub)
        # Sort: root domain first, then alphabetically
        subs = sorted(seen, key=lambda s: (0 if s == domain else 1, s))
        result["subdomains"] = subs[:500]
        result["count"] = len(subs)
    except Exception as e:
        result["error"] = str(e)
    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error":"No domain provided"}))
    else:
        lookup(sys.argv[1])
