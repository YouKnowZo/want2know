#!/usr/bin/env python3
import sys
import json
from datetime import datetime, timezone

def lookup(username):
    result = {"username": username, "found": False, "url": "",
              "created_utc": 0, "created_date": "", "account_age_days": 0,
              "comment_karma": 0, "link_karma": 0, "total_karma": 0,
              "is_gold": False, "is_mod": False, "verified_email": False,
              "icon_img": "", "subreddit_title": "", "subreddit_desc": "",
              "recent_subs": [], "recent_comments": [], "error": ""}
    try:
        import requests
        username = username.strip().lstrip("@").lstrip("u/").lstrip("/u/")
        if not username:
            result["error"] = "No username provided"
            print(json.dumps(result)); return
        result["username"] = username
        result["url"] = f"https://www.reddit.com/user/{username}"

        H = {"User-Agent": "web:want2know-osint:v1.0 (by /u/want2know_research)",
             "Accept": "application/json"}
        # Try multiple endpoints; reddit aggressively blocks server-to-server requests
        r = None
        last_status = 0
        for base in ("https://www.reddit.com", "https://old.reddit.com", "https://api.reddit.com"):
            try:
                r = requests.get(f"{base}/user/{username}/about.json",
                                 headers=H, timeout=10, allow_redirects=True)
                last_status = r.status_code
                if r.status_code == 200:
                    break
            except Exception:
                continue
        if not r or r.status_code != 200:
            if last_status == 404:
                result["error"] = "Reddit user not found"
            elif last_status in (403, 429):
                result["error"] = "Reddit is blocking automated requests right now. Open the profile link directly."
            else:
                result["error"] = f"Reddit returned status {last_status}"
            print(json.dumps(result)); return
        d = (r.json() or {}).get("data") or {}
        if not d:
            result["error"] = "Empty response from Reddit"
            print(json.dumps(result)); return

        result["found"] = True
        result["created_utc"] = d.get("created_utc") or 0
        if result["created_utc"]:
            dt = datetime.fromtimestamp(result["created_utc"], tz=timezone.utc)
            result["created_date"] = dt.strftime("%Y-%m-%d")
            result["account_age_days"] = (datetime.now(tz=timezone.utc) - dt).days
        result["comment_karma"] = d.get("comment_karma") or 0
        result["link_karma"] = d.get("link_karma") or 0
        result["total_karma"] = d.get("total_karma") or (result["comment_karma"] + result["link_karma"])
        result["is_gold"] = bool(d.get("is_gold"))
        result["is_mod"] = bool(d.get("is_mod"))
        result["verified_email"] = bool(d.get("has_verified_email"))
        result["icon_img"] = (d.get("icon_img") or "").split("?")[0]

        sub = d.get("subreddit") or {}
        result["subreddit_title"] = sub.get("title") or ""
        result["subreddit_desc"] = (sub.get("public_description") or "")[:280]

        # Recent comments → infer subreddits
        try:
            rc = requests.get(
                f"https://old.reddit.com/user/{username}/comments.json",
                params={"limit": 25}, headers=H, timeout=10
            )
            if rc.status_code == 200:
                items = ((rc.json() or {}).get("data") or {}).get("children") or []
                sub_count = {}
                for it in items:
                    c = (it or {}).get("data") or {}
                    sr = c.get("subreddit","")
                    if sr: sub_count[sr] = sub_count.get(sr, 0) + 1
                    if len(result["recent_comments"]) < 5:
                        result["recent_comments"].append({
                            "subreddit": sr,
                            "body": (c.get("body") or "")[:240],
                            "score": c.get("score", 0),
                            "permalink": "https://www.reddit.com" + (c.get("permalink") or "")
                        })
                result["recent_subs"] = sorted(sub_count.items(), key=lambda x: -x[1])[:8]
        except Exception:
            pass

    except Exception as e:
        result["error"] = str(e)
    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error":"No username provided"}))
    else:
        lookup(sys.argv[1])
