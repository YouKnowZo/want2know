#!/usr/bin/env python3
import sys
import json
import re
import hashlib

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
DISPOSABLE = {
    "mailinator.com","tempmail.com","10minutemail.com","guerrillamail.com",
    "yopmail.com","trashmail.com","getnada.com","throwawaymail.com",
    "maildrop.cc","sharklasers.com","dispostable.com","mailnesia.com"
}
FREE_PROVIDERS = {
    "gmail.com","yahoo.com","outlook.com","hotmail.com","aol.com","icloud.com",
    "protonmail.com","proton.me","mail.com","gmx.com","yandex.com","zoho.com",
    "live.com","msn.com","tutanota.com","fastmail.com"
}

def doh_query(domain, qtype):
    try:
        import requests
        r = requests.get(
            "https://cloudflare-dns.com/dns-query",
            params={"name": domain, "type": qtype},
            headers={"accept": "application/dns-json"},
            timeout=5
        )
        if r.status_code == 200:
            return r.json().get("Answer", []) or []
    except Exception:
        pass
    return []

def lookup(email):
    result = {
        "email": email, "valid_format": False, "domain": "",
        "username": "", "is_disposable": False, "is_free_provider": False,
        "mx_records": [], "has_mx": False, "spf_present": False,
        "dmarc_present": False, "gravatar_url": "", "gravatar_profile": "",
        "md5_hash": "", "sha1_hash": "", "sha256_hash": "",
        "breach_check_url": "", "google_dorks": [], "error": ""
    }
    try:
        email = email.strip().lower()
        result["email"] = email
        if not EMAIL_RE.match(email):
            result["error"] = "Invalid email format"
            print(json.dumps(result)); return

        result["valid_format"] = True
        local, domain = email.split("@", 1)
        result["username"] = local
        result["domain"] = domain
        result["is_disposable"] = domain in DISPOSABLE
        result["is_free_provider"] = domain in FREE_PROVIDERS

        # Hashes (useful for HIBP, gravatar, OSINT pivoting)
        result["md5_hash"] = hashlib.md5(email.encode()).hexdigest()
        result["sha1_hash"] = hashlib.sha1(email.encode()).hexdigest()
        result["sha256_hash"] = hashlib.sha256(email.encode()).hexdigest()
        result["gravatar_url"] = f"https://www.gravatar.com/avatar/{result['md5_hash']}?d=404&s=200"
        result["gravatar_profile"] = f"https://www.gravatar.com/{result['md5_hash']}.json"
        result["breach_check_url"] = f"https://haveibeenpwned.com/account/{email}"

        # MX records
        mx = doh_query(domain, "MX")
        result["mx_records"] = [a.get("data","") for a in mx][:10]
        result["has_mx"] = len(result["mx_records"]) > 0

        # SPF / DMARC
        txt = doh_query(domain, "TXT")
        for t in txt:
            data = t.get("data","")
            if "spf1" in data.lower():
                result["spf_present"] = True
        dmarc = doh_query(f"_dmarc.{domain}", "TXT")
        result["dmarc_present"] = len(dmarc) > 0

        # OSINT pivots
        result["google_dorks"] = [
            f'"{email}"',
            f'"{local}" site:linkedin.com',
            f'"{local}" site:github.com',
            f'"{email}" filetype:pdf',
            f'intext:"{email}"'
        ]

    except Exception as e:
        result["error"] = str(e)
    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No email provided"}))
    else:
        lookup(sys.argv[1])
