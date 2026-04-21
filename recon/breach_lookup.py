#!/usr/bin/env python3
import sys
import json
import re

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

def lookup(email):
    result = {"email": email, "breached": False, "breach_count": 0,
              "breaches": [], "pastes": [], "exposed_data": [],
              "risk_score": 0, "risk_label": "", "industry": "",
              "error": ""}
    try:
        import requests
        email = email.strip().lower()
        if not EMAIL_RE.match(email):
            result["error"] = "Invalid email format"
            print(json.dumps(result)); return
        result["email"] = email

        # XposedOrNot — free, no API key required
        r = requests.get(
            f"https://api.xposedornot.com/v1/breach-analytics",
            params={"email": email},
            headers={"User-Agent": "Want2Know-OSINT/1.0"},
            timeout=12
        )
        if r.status_code == 404:
            # Not in any breach
            result["breached"] = False
            print(json.dumps(result)); return
        if r.status_code != 200:
            result["error"] = f"Breach API returned status {r.status_code}"
            print(json.dumps(result)); return

        data = r.json()
        bsumm = (data.get("BreachesSummary") or {}).get("site", "")
        breach_names = [b.strip() for b in bsumm.split(";") if b.strip()] if bsumm else []
        details = (data.get("ExposedBreaches") or {}).get("breaches_details", []) or []

        result["breach_count"] = len(breach_names) or len(details)
        result["breached"] = result["breach_count"] > 0

        for b in details:
            result["breaches"].append({
                "name": b.get("breach", ""),
                "domain": b.get("domain", ""),
                "date": b.get("xposed_date", ""),
                "records": b.get("xposed_records", 0),
                "exposed_data": b.get("xposed_data", "").split(";") if b.get("xposed_data") else [],
                "industry": b.get("industry", ""),
                "logo": b.get("logo", ""),
                "summary": b.get("details", "")[:280] if b.get("details") else ""
            })

        # Risk
        rs = (data.get("BreachMetrics") or {}).get("risk", [])
        if rs and isinstance(rs, list) and rs:
            result["risk_score"] = rs[0].get("risk_score", 0)
            result["risk_label"] = rs[0].get("risk_label", "")

        # Pastes
        pastes = data.get("PastesSummary") or {}
        if pastes and pastes.get("cnt"):
            result["pastes"] = [{"count": pastes.get("cnt", 0)}]

        # Aggregated exposed data categories
        xposed = (data.get("BreachMetrics") or {}).get("xposed_data", [])
        if xposed and isinstance(xposed, list) and xposed:
            children = (xposed[0].get("children") or [])
            for c in children:
                for sub in (c.get("children") or []):
                    if sub.get("name"):
                        result["exposed_data"].append(sub["name"])

    except Exception as e:
        result["error"] = str(e)
    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error":"No email provided"}))
    else:
        lookup(sys.argv[1])
