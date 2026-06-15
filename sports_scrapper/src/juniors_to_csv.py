"""Extract all junior ice hockey leagues linked in raws/juniors.html into a CSV.

For each linked league we capture its name, the URL, whether the link is
internal (Wikipedia) or external, and the section context it appears under
(level / governing body) derived from the preceding headings and list items.
"""

from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup, Tag

HTML_PATH = Path("raws/juniors.html")
OUTPUT_PATH = Path("output/junior_leagues.csv")
WIKI_BASE = "https://en.wikipedia.org"

# Heading levels we treat as section context.
HEADING_TAGS = {"h4", "h5", "h6"}


def clean(text: str) -> str:
    return " ".join(text.split())


def main() -> None:
    soup = BeautifulSoup(HTML_PATH.read_text(encoding="utf-8"), "lxml")

    rows = []
    # Track the most recent heading at each level so we always know the context.
    headings: dict[str, str] = {}
    # Track the current <dt> label (e.g. "Tier I", "Independent junior leagues").
    current_label = ""

    for el in soup.descendants:
        if not isinstance(el, Tag):
            continue

        if el.name in HEADING_TAGS:
            headings[el.name] = clean(el.get_text())
            # Reset deeper levels when a higher heading appears.
            if el.name == "h4":
                headings.pop("h5", None)
                headings.pop("h6", None)
                current_label = ""
            elif el.name == "h5":
                headings.pop("h6", None)
                current_label = ""
            continue

        if el.name == "dt":
            current_label = clean(el.get_text())
            continue

        if el.name == "a":
            href = el.get("href", "")
            name = clean(el.get_text())
            if not name or not href:
                continue
            # Skip Wikipedia edit-section / utility links.
            if "action=edit" in href or href.startswith("#"):
                continue

            is_external = "external" in (el.get("class") or [])
            url = href if is_external else WIKI_BASE + href

            rows.append(
                {
                    "League": name,
                    "Section": headings.get("h5", headings.get("h4", "")),
                    "Subsection": headings.get("h6", ""),
                    "Label": current_label,
                    "Link type": "external" if is_external else "internal",
                    "URL": url,
                }
            )

    df = pd.DataFrame(rows).drop_duplicates(subset=["League", "URL"]).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"Wrote {len(df)} leagues to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
