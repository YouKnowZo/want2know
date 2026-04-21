#!/usr/bin/env python3
import sys
import json

def lookup(username):
    result = {"username": username, "found": False, "name": "", "bio": "",
              "company": "", "location": "", "blog": "", "email": "",
              "twitter": "", "avatar": "", "html_url": "",
              "public_repos": 0, "public_gists": 0, "followers": 0,
              "following": 0, "created_at": "", "updated_at": "",
              "top_repos": [], "languages": [], "error": ""}
    try:
        import requests
        username = username.strip().lstrip("@")
        if not username:
            result["error"] = "No username provided"
            print(json.dumps(result)); return
        result["username"] = username

        # Public GitHub API — no key needed for ~60 req/h per IP
        r = requests.get(f"https://api.github.com/users/{username}",
                         headers={"User-Agent": "Want2Know-OSINT/1.0",
                                  "Accept": "application/vnd.github+json"},
                         timeout=10)
        if r.status_code == 404:
            result["error"] = "GitHub user not found"
            print(json.dumps(result)); return
        if r.status_code == 403:
            result["error"] = "GitHub API rate limit exceeded — try again in a few minutes"
            print(json.dumps(result)); return
        if r.status_code != 200:
            result["error"] = f"GitHub returned status {r.status_code}"
            print(json.dumps(result)); return

        d = r.json()
        result.update({
            "found": True,
            "name": d.get("name") or "",
            "bio": d.get("bio") or "",
            "company": d.get("company") or "",
            "location": d.get("location") or "",
            "blog": d.get("blog") or "",
            "email": d.get("email") or "",
            "twitter": d.get("twitter_username") or "",
            "avatar": d.get("avatar_url") or "",
            "html_url": d.get("html_url") or "",
            "public_repos": d.get("public_repos") or 0,
            "public_gists": d.get("public_gists") or 0,
            "followers": d.get("followers") or 0,
            "following": d.get("following") or 0,
            "created_at": (d.get("created_at") or "")[:10],
            "updated_at": (d.get("updated_at") or "")[:10],
        })

        # Top repos
        try:
            rr = requests.get(
                f"https://api.github.com/users/{username}/repos",
                params={"sort": "updated", "per_page": 8},
                headers={"User-Agent": "Want2Know-OSINT/1.0",
                         "Accept": "application/vnd.github+json"},
                timeout=10
            )
            if rr.status_code == 200:
                lang_counter = {}
                for repo in rr.json():
                    if repo.get("fork"): continue
                    result["top_repos"].append({
                        "name": repo.get("name",""),
                        "url": repo.get("html_url",""),
                        "description": (repo.get("description") or "")[:140],
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "language": repo.get("language") or "",
                        "updated": (repo.get("updated_at") or "")[:10]
                    })
                    lang = repo.get("language")
                    if lang: lang_counter[lang] = lang_counter.get(lang, 0) + 1
                result["top_repos"] = result["top_repos"][:6]
                result["languages"] = sorted(lang_counter.items(), key=lambda x: -x[1])[:5]
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
