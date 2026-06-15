"""Extract the current "Teams" table from each downloaded league HTML page.

For every file in raws/leagues/ this finds the heading for the current teams
section (e.g. "Teams", "Current teams", "Member teams") and parses the table(s)
that follow it, stopping before any "Former / Defunct / Old / Timeline" section.
All rows are combined into a single CSV, tagged with the source league.
"""

import re
from io import StringIO
from pathlib import Path
from urllib.parse import unquote, urlparse

import pandas as pd
from bs4 import BeautifulSoup, Tag

LEAGUES_DIR = Path("raws/leagues")
LEAGUES_CSV = Path("output/junior_leagues.csv")
OUTPUT_DIR = Path("output/teams_by_section")

HEADING_TAGS = ("h2", "h3", "h4")

SKIP_TABLE_CLASSES = {
    "navbox",
    "infobox",
    "vertical-navbox",
    "metadata",
    "sidebar",
    "toccolours",
    "mbox-small",
}

# A heading id that names the *current* teams section we want.
WANTED_RE = re.compile(r"(current[_ ]?teams|member[_ ]?teams|^teams)", re.IGNORECASE)

# A heading id that means we've gone too far and should stop.
STOP_RE = re.compile(
    r"(former|defunct|old|past|timeline|inactive|future|history|results|champions)",
    re.IGNORECASE,
)


def norm(text: str) -> str:
    return " ".join(text.split())


def slugify(url: str) -> str:
    """Derive the downloaded HTML filename from a Wikipedia URL."""
    title = unquote(urlparse(url).path.rsplit("/", 1)[-1])
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", title)
    return f"{safe}.html"


def load_sections() -> dict[str, str]:
    """Map source HTML filename -> Section from the leagues CSV."""
    df = pd.read_csv(LEAGUES_CSV)
    df = df[df["Link type"] == "internal"]
    return {slugify(url): section for url, section in zip(df["URL"], df["Section"])}


def find_heading_tag(tag: Tag) -> Tag | None:
    """Return the h2/h3/h4 inside a mw-heading wrapper (or the tag itself)."""
    if tag.name in HEADING_TAGS:
        return tag
    if isinstance(tag, Tag) and "mw-heading" in (tag.get("class") or []):
        return tag.find(HEADING_TAGS)
    return None


def extract_tables(html: str) -> list[pd.DataFrame]:
    soup = BeautifulSoup(html, "lxml")

    # Build an ordered list of (heading_tag, id) for all section headings.
    headings = []
    for tag in soup.find_all(HEADING_TAGS):
        hid = tag.get("id", "")
        headings.append((tag, hid))

    # Find the first heading whose id marks the current-teams section.
    target = None
    for tag, hid in headings:
        if hid and WANTED_RE.search(hid) and not STOP_RE.search(hid):
            target = tag
            break
    if target is None:
        return []

    # Walk forward from the target heading, collecting tables until we hit a
    # heading that signals a "former/old/etc." section.
    frames: list[pd.DataFrame] = []
    for el in target.find_all_next():
        if not isinstance(el, Tag):
            continue
        if el.name in HEADING_TAGS:
            hid = el.get("id", "")
            if hid and STOP_RE.search(hid):
                break
            # A new current-style section heading also ends the previous table.
            if hid and WANTED_RE.search(hid) and el is not target:
                continue
        if el.name == "table":
            classes = el.get("class") or []
            # Skip navigation / infobox / metadata style tables.
            if any(c in classes for c in SKIP_TABLE_CLASSES):
                continue
            # Some pages have malformed span attrs like colspan="2;" that break
            # the parser; strip them to digits only before parsing.
            for cell in el.find_all(["td", "th"]):
                for attr in ("colspan", "rowspan"):
                    if cell.has_attr(attr):
                        digits = re.sub(r"\D", "", cell[attr])
                        if digits:
                            cell[attr] = digits
                        else:
                            del cell[attr]
            try:
                parsed = pd.read_html(StringIO(str(el)))[0]
            except Exception:
                continue
            # Ignore tiny/degenerate tables (e.g. legends, single cells).
            if parsed.shape[0] >= 1 and parsed.shape[1] >= 2:
                frames.append(parsed)
    return frames


def main() -> None:
    sections = load_sections()
    # Group the per-league DataFrames by their section.
    by_section: dict[str, list[pd.DataFrame]] = {}
    no_table = []

    for path in sorted(LEAGUES_DIR.glob("*.html")):
        league = path.stem.replace("_", " ")
        frames = extract_tables(path.read_text(encoding="utf-8"))
        if not frames:
            no_table.append(path.name)
            continue
        df = pd.concat(frames, ignore_index=True)
        df.insert(0, "League", league)
        df.insert(1, "Source file", path.name)
        section = sections.get(path.name, "Unknown")
        by_section.setdefault(section, []).append(df)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for section, frames in sorted(by_section.items()):
        combined = pd.concat(frames, ignore_index=True)
        # Drop columns that are entirely empty within this section.
        combined = combined.dropna(axis=1, how="all")
        slug = re.sub(r"[^A-Za-z0-9]+", "_", section).strip("_").lower()
        out = OUTPUT_DIR / f"teams_{slug}.csv"
        combined.to_csv(out, index=False, encoding="utf-8")
        print(f"{section}: {len(combined)} rows, {combined.shape[1]} cols -> {out}")

    if no_table:
        print(f"\nNo current-teams table found in {len(no_table)} files:")
        for name in no_table:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
