"""
Download all "Year in sumo" Wikipedia pages as HTML files into the Years/ folder.

Usage:
    python src/download_sumo_pages.py                  # default range: 1992-2025
    python src/download_sumo_pages.py 2000 2010        # custom range: 2000-2010
    python src/download_sumo_pages.py --skip-existing   # don't re-download files already present

Respects Wikipedia etiquette with a User-Agent header and a delay between requests.
"""

import os
import sys
import time
from pathlib import Path

import requests

BASE_URL = "https://en.wikipedia.org/wiki/{year}_in_sumo"
USER_AGENT = "SumoScraper/1.0 (personal project; polite crawl)"
REQUEST_DELAY = 1.5  # seconds between requests

DEFAULT_START_YEAR = 1992
DEFAULT_END_YEAR = 2025


def download_page(year: int, output_dir: Path, skip_existing: bool = False) -> bool:
    """Download a single year's page. Returns True if successful."""
    filename = f"{year} in sumo.html"
    out_path = output_dir / filename

    if skip_existing and out_path.exists():
        print(f"  {year}: skipped (already exists)")
        return True

    url = BASE_URL.format(year=year)
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
    except requests.RequestException as e:
        print(f"  {year}: ERROR - {e}")
        return False

    if response.status_code == 404:
        print(f"  {year}: no page found (404)")
        return False
    elif response.status_code != 200:
        print(f"  {year}: unexpected status {response.status_code}")
        return False

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    size_kb = out_path.stat().st_size / 1024
    print(f"  {year}: saved ({size_kb:.0f} KB)")
    return True


def main():
    start_year = DEFAULT_START_YEAR
    end_year = DEFAULT_END_YEAR
    skip_existing = False

    # Parse arguments
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    if "--skip-existing" in flags:
        skip_existing = True

    if len(args) >= 2:
        start_year = int(args[0])
        end_year = int(args[1])
    elif len(args) == 1:
        start_year = int(args[0])

    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "Years"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading '{start_year} in sumo' through '{end_year} in sumo'")
    print(f"Output: {output_dir}")
    print(f"Skip existing: {skip_existing}")
    print(f"Delay between requests: {REQUEST_DELAY}s\n")

    success = 0
    skipped = 0
    failed = 0

    for year in range(start_year, end_year + 1):
        result = download_page(year, output_dir, skip_existing)
        if result:
            success += 1
        else:
            failed += 1

        # Be polite — wait between requests
        if year < end_year:
            time.sleep(REQUEST_DELAY)

    print(f"\nDone! Downloaded: {success}, Failed/missing: {failed}")


if __name__ == "__main__":
    main()
