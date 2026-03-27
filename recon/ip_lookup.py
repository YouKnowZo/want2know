#!/usr/bin/env python3
import sys
import json
import urllib.request
import socket

def lookup(target):
    result = {
        "query": target,
        "ip": "",
        "status": "",
        "country": "",
        "countryCode": "",
        "region": "",
        "regionName": "",
        "city": "",
        "zip": "",
        "lat": "",
        "lon": "",
        "timezone": "",
        "isp": "",
        "org": "",
        "as_info": "",
        "error": ""
    }

    try:
        # Resolve domain to IP first if it looks like a domain
        ip = target
        if not target.replace('.', '').replace(':', '').isdigit():
            try:
                ip = socket.gethostbyname(target)
                result["ip"] = ip
            except Exception as e:
                result["error"] = f"Could not resolve hostname: {e}"
                print(json.dumps(result))
                return

        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            result["status"] = data.get("status", "")
            result["ip"] = data.get("query", ip)
            result["country"] = data.get("country", "")
            result["countryCode"] = data.get("countryCode", "")
            result["region"] = data.get("region", "")
            result["regionName"] = data.get("regionName", "")
            result["city"] = data.get("city", "")
            result["zip"] = data.get("zip", "")
            result["lat"] = data.get("lat", "")
            result["lon"] = data.get("lon", "")
            result["timezone"] = data.get("timezone", "")
            result["isp"] = data.get("isp", "")
            result["org"] = data.get("org", "")
            result["as_info"] = data.get("as", "")
            if data.get("status") == "fail":
                result["error"] = data.get("message", "Lookup failed")
    except Exception as e:
        result["error"] = str(e)

    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No target provided"}))
    else:
        lookup(sys.argv[1])
