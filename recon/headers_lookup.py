#!/usr/bin/env python3
import sys
import json

SECURITY_HEADERS = {
    "strict-transport-security": ("HSTS", "Forces HTTPS connections"),
    "content-security-policy": ("CSP", "Restricts resource loading to prevent XSS"),
    "x-frame-options": ("X-Frame-Options", "Prevents clickjacking"),
    "x-content-type-options": ("X-Content-Type-Options", "Stops MIME-type sniffing"),
    "referrer-policy": ("Referrer-Policy", "Controls referrer info leakage"),
    "permissions-policy": ("Permissions-Policy", "Restricts browser feature access"),
    "x-xss-protection": ("X-XSS-Protection", "Legacy XSS filter (deprecated)"),
    "cross-origin-opener-policy": ("COOP", "Isolates browsing context"),
    "cross-origin-embedder-policy": ("COEP", "Controls cross-origin embedding"),
    "cross-origin-resource-policy": ("CORP", "Controls cross-origin resource sharing"),
}

def lookup(url):
    result = {
        "url": url, "final_url": "", "status_code": 0, "server": "",
        "headers": {}, "security": {"present": [], "missing": [], "score": 0, "grade": "F"},
        "tech_hints": [], "cookies": [], "error": ""
    }
    try:
        import requests
        if not url.startswith("http"):
            url = "https://" + url
        r = requests.get(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "Want2Know-OSINT/1.0"})
        result["final_url"] = r.url
        result["status_code"] = r.status_code
        result["server"] = r.headers.get("Server","")
        result["headers"] = dict(r.headers)

        present, missing = [], []
        for h, (label, desc) in SECURITY_HEADERS.items():
            if h in {k.lower() for k in r.headers.keys()}:
                value = next((v for k,v in r.headers.items() if k.lower()==h), "")
                present.append({"header": label, "description": desc, "value": value[:200]})
            else:
                missing.append({"header": label, "description": desc})
        result["security"]["present"] = present
        result["security"]["missing"] = missing
        score = int((len(present) / len(SECURITY_HEADERS)) * 100)
        result["security"]["score"] = score
        if score >= 90: grade = "A"
        elif score >= 75: grade = "B"
        elif score >= 60: grade = "C"
        elif score >= 40: grade = "D"
        else: grade = "F"
        result["security"]["grade"] = grade

        # Tech hints
        tech = []
        if r.headers.get("Server"): tech.append(f"Server: {r.headers['Server']}")
        if r.headers.get("X-Powered-By"): tech.append(f"Powered by: {r.headers['X-Powered-By']}")
        if r.headers.get("X-Generator"): tech.append(f"Generator: {r.headers['X-Generator']}")
        if r.headers.get("Via"): tech.append(f"Via: {r.headers['Via']}")
        if r.headers.get("CF-Ray"): tech.append("CDN: Cloudflare")
        if r.headers.get("X-Vercel-Id"): tech.append("Hosted on: Vercel")
        if r.headers.get("X-Amz-Cf-Id"): tech.append("CDN: Amazon CloudFront")
        if r.headers.get("X-Github-Request-Id"): tech.append("Hosted on: GitHub")
        result["tech_hints"] = tech

        for c in r.cookies:
            result["cookies"].append({"name": c.name, "domain": c.domain, "secure": c.secure})

    except Exception as e:
        result["error"] = str(e)
    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error":"No URL provided"}))
    else:
        lookup(sys.argv[1])
