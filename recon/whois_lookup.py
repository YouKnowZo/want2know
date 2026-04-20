#!/usr/bin/env python3
import sys
import json
import requests

def lookup(target):
    target = target.strip().lower()
    result = {
        "target": target,
        "type": "",
        "name": "",
        "handle": "",
        "status": [],
        "created": "",
        "updated": "",
        "expires": "",
        "registrar": "",
        "registrant": "",
        "nameservers": [],
        "country": "",
        "error": ""
    }

    try:
        import ipaddress
        ipaddress.ip_address(target)
        is_ip = True
    except Exception:
        is_ip = False

    try:
        if is_ip:
            result["type"] = "IP Network"
            url = f"https://rdap.arin.net/registry/ip/{target}"
        else:
            result["type"] = "Domain"
            url = f"https://rdap.org/domain/{target}"

        resp = requests.get(url, timeout=12, headers={"Accept": "application/json"})
        resp.raise_for_status()
        data = resp.json()

        result["name"]   = data.get("name", "") or data.get("ldhName", "")
        result["handle"] = data.get("handle", "")
        result["status"] = data.get("status", [])
        result["country"] = data.get("country", "")

        for event in data.get("events", []):
            action = event.get("eventAction", "")
            date   = event.get("eventDate", "")[:10]
            if action == "registration":
                result["created"] = date
            elif action == "expiration":
                result["expires"] = date
            elif action in ("last changed", "last update of RDAP database"):
                result["updated"] = date

        for entity in data.get("entities", []):
            roles  = entity.get("roles", [])
            vcard  = entity.get("vcardArray", [])
            name   = ""
            if vcard and len(vcard) > 1:
                for item in vcard[1]:
                    if item[0] == "fn":
                        name = item[3]
            if "registrar" in roles and not result["registrar"]:
                result["registrar"] = name
            elif "registrant" in roles and not result["registrant"]:
                result["registrant"] = name

        nameservers = []
        for ns in data.get("nameservers", []):
            ns_name = ns.get("ldhName", "")
            if ns_name:
                nameservers.append(ns_name.lower())
        result["nameservers"] = nameservers

        if is_ip:
            cidrs = data.get("cidr0_cidrs", [])
            if cidrs:
                result["cidr"] = ", ".join(
                    f"{c.get('v4prefix', c.get('v6prefix',''))}/{c.get('length','')}"
                    for c in cidrs
                )

    except requests.exceptions.HTTPError as e:
        result["error"] = f"WHOIS lookup failed (HTTP {e.response.status_code}). Domain may not be registered or RDAP is unsupported for this TLD."
    except Exception as e:
        result["error"] = f"Lookup failed: {str(e)}"

    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No target provided"}))
    else:
        lookup(sys.argv[1])
