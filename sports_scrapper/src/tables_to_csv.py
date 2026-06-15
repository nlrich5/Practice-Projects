"""Convert all HTML tables in the Minor League Baseball file into a single CSV."""

from io import StringIO
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

HTML_PATH = Path("raws/List of Minor League Baseball leagues and teams.html")
OUTPUT_PATH = Path("output/minor_league_tables.csv")


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    frames = []
    for table in soup.find_all("table", class_="wikitable"):
        caption_tag = table.find("caption")
        caption = caption_tag.get_text(strip=True) if caption_tag else "Unnamed table"

        # Parse this single table with pandas.
        df = pd.read_html(StringIO(str(table)))[0]

        # Tag each row with the table it came from.
        df.insert(0, "Table", caption)
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"Wrote {len(combined)} rows from {len(frames)} tables to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
