#!/usr/bin/env python3
import sys
import json

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "CAA"]

def doh_query(domain, qtype):
    try:
        import requests
        r = requests.get(
            "https://cloudflare-dns.com/dns-query",
            params={"name": domain, "type": qtype},
            headers={"accept": "application/dns-json"},
            timeout=6
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("Answer", []) or []
    except Exception:
        pass
    return []

def lookup(domain):
    result = {"domain": domain, "records": {}, "summary": {}, "error": ""}
    try:
        domain = domain.strip().lower().replace("https://","").replace("http://","").split("/")[0]
        result["domain"] = domain
        for rtype in RECORD_TYPES:
            answers = doh_query(domain, rtype)
            cleaned = []
            for a in answers:
                cleaned.append({
                    "name": a.get("name",""),
                    "ttl": a.get("TTL", 0),
                    "data": a.get("data","")
                })
            result["records"][rtype] = cleaned
        result["summary"] = {
            "total_records": sum(len(v) for v in result["records"].values()),
            "has_mx": len(result["records"].get("MX", [])) > 0,
            "has_spf": any("spf1" in r.get("data","").lower() for r in result["records"].get("TXT", [])),
            "has_dmarc": False,
            "nameservers": [r["data"] for r in result["records"].get("NS", [])],
            "ipv4": [r["data"] for r in result["records"].get("A", [])],
            "ipv6": [r["data"] for r in result["records"].get("AAAA", [])],
        }
        # DMARC sub-lookup
        dmarc = doh_query(f"_dmarc.{domain}", "TXT")
        result["summary"]["has_dmarc"] = len(dmarc) > 0
        if dmarc:
            result["records"]["DMARC"] = [{"name": f"_dmarc.{domain}", "ttl": d.get("TTL",0), "data": d.get("data","")} for d in dmarc]
    except Exception as e:
        result["error"] = str(e)
    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error":"No domain provided"}))
    else:
        lookup(sys.argv[1])
