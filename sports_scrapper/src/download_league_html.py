"""Download the HTML page for each Wikipedia league listed in the leagues CSV.

Reads output/junior_leagues.csv, and for every row whose link type is
"internal" (i.e. a Wikipedia page) downloads the page HTML into raws/leagues/.
External links are skipped. Pages already downloaded are skipped so the script
can be re-run safely.
"""

import re
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import pandas as pd
import requests

CSV_PATH = Path("output/junior_leagues.csv")
OUTPUT_DIR = Path("raws/leagues")
REQUEST_DELAY = 1.0  # seconds between requests, be polite to Wikipedia
HEADERS = {
    "User-Agent": "sports_scrapper/1.0 (educational project; contact: local user)"
}


def slugify(url: str) -> str:
    """Build a safe filename from the page title in the URL."""
    title = unquote(urlparse(url).path.rsplit("/", 1)[-1])
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", title)
    return f"{safe}.html"


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    wiki_rows = df[df["Link type"] == "internal"]
    print(f"Found {len(wiki_rows)} Wikipedia links to download.")

    session = requests.Session()
    session.headers.update(HEADERS)

    downloaded = 0
    skipped = 0
    failed = 0

    for _, row in wiki_rows.iterrows():
        url = row["URL"]
        name = row["League"]
        dest = OUTPUT_DIR / slugify(url)

        if dest.exists():
            print(f"  skip (exists): {name}")
            skipped += 1
            continue

        try:
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            dest.write_text(resp.text, encoding="utf-8")
            print(f"  ok: {name} -> {dest.name}")
            downloaded += 1
            time.sleep(REQUEST_DELAY)
        except requests.RequestException as exc:
            print(f"  FAILED: {name} ({url}): {exc}")
            failed += 1

    print(
        f"\nDone. Downloaded {downloaded}, skipped {skipped}, failed {failed}."
    )


if __name__ == "__main__":
    main()
