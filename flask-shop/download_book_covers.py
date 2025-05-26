"""
Download cover images for every book in books_to_update.json
and save them exactly under the image_path specified.

Requires: pip install requests
"""

import json, os, requests
from pathlib import Path

JSON_FILE = "books_to_update.json"
TIMEOUT    = 15   # seconds per request

def main():
    with open(JSON_FILE, encoding="utf-8") as f:
        books = json.load(f)

    for b in books:
        url  = b.get("image_url")
        path = Path(b["image_path"])
        if not url:
            print(f"⚠️  {b['title']}: no image_url provided, skipping")
            continue

        # ensure folder exists
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            r = requests.get(url, stream=True, timeout=TIMEOUT)
            if r.status_code != 200:
                print(f"❌ {b['title']}: failed ({r.status_code})")
                continue
            with open(path, "wb") as f_out:
                for chunk in r.iter_content(8192):
                    f_out.write(chunk)
            print(f"{b['title']}: saved → {path}")
        except Exception as e:
            print(f"{b['title']}: {e}")

    print("🏁 Finished.")

if __name__ == "__main__":
    main()
