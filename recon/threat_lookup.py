#!/usr/bin/env python3
import sys
import json

def lookup(target):
    result = {"target": target, "is_malicious": False, "sources": [],
              "urlhaus": {"hits": 0, "entries": []},
              "phishtank": {"hits": 0, "entries": []},
              "verdict": "clean", "error": ""}
    try:
        import requests
        target = target.strip().replace("https://","").replace("http://","").split("/")[0]
        result["target"] = target

        # URLhaus (Abuse.ch) — free, no key required
        try:
            r = requests.post(
                "https://urlhaus-api.abuse.ch/v1/host/",
                data={"host": target},
                timeout=10
            )
            if r.status_code == 200:
                d = r.json()
                if d.get("query_status") == "ok":
                    urls = d.get("urls", []) or []
                    result["urlhaus"]["hits"] = len(urls)
                    for u in urls[:10]:
                        result["urlhaus"]["entries"].append({
                            "url": u.get("url",""),
                            "threat": u.get("threat",""),
                            "tags": u.get("tags") or [],
                            "date_added": u.get("date_added",""),
                            "status": u.get("url_status",""),
                            "reporter": u.get("reporter","")
                        })
                    if urls:
                        result["sources"].append("URLhaus")
        except Exception as e:
            pass

        # ThreatFox (Abuse.ch) — free, no key needed for host search
        try:
            r = requests.post(
                "https://threatfox-api.abuse.ch/api/v1/",
                json={"query": "search_ioc", "search_term": target},
                timeout=10
            )
            if r.status_code == 200:
                d = r.json()
                if d.get("query_status") == "ok":
                    for ioc in (d.get("data") or [])[:5]:
                        result["urlhaus"]["entries"].append({
                            "url": ioc.get("ioc",""),
                            "threat": ioc.get("threat_type",""),
                            "tags": [ioc.get("malware","")] if ioc.get("malware") else [],
                            "date_added": ioc.get("first_seen",""),
                            "status": "ioc",
                            "reporter": "ThreatFox"
                        })
                    if d.get("data"):
                        result["sources"].append("ThreatFox")
        except Exception as e:
            pass

        result["is_malicious"] = result["urlhaus"]["hits"] > 0 or len(result["urlhaus"]["entries"]) > 0
        result["verdict"] = "malicious" if result["is_malicious"] else "clean"

    except Exception as e:
        result["error"] = str(e)
    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error":"No target provided"}))
    else:
        lookup(sys.argv[1])
