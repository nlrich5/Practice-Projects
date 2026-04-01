"""
Parse all HTML tables from .html files in the Years/ folder and export them as CSVs.

Each wikitable is exported to its own CSV file. Tables are named using the
page title (year) and a table index. If the table has a title row (first row
with a single spanning cell), that title is incorporated into the filename.

Output goes to an output/csv/ directory.
"""

import csv
import os
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup, Tag


def clean_text(text: str) -> str:
    """Normalize whitespace and strip a cell's text."""
    text = text.replace("ō", "o").replace("Ō", "O")
    text = text.replace("ū", "u").replace("Ū", "U")
    return re.sub(r"\s+", " ", text).strip()


def has_palegreen_bg(cell: Tag) -> bool:
    """Return True if a table cell has a PaleGreen background color."""
    style = (cell.get("style") or "").lower()
    return "palegreen" in style


def expand_table(table: Tag) -> tuple[list[list[str]], list[list[bool]]]:
    """
    Parse an HTML <table> into a 2-D list of strings,
    correctly handling colspan and rowspan.

    Returns (grid, yusho_grid) where yusho_grid[r][c] is True when the
    source <td> had a PaleGreen background (the Wikipedia convention for
    marking the yusho winner).
    """
    rows = table.find_all("tr")
    if not rows:
        return [], []

    # First pass: figure out the grid dimensions
    max_cols = 0
    for row in rows:
        col_count = 0
        for cell in row.find_all(["th", "td"]):
            col_count += int(cell.get("colspan", 1))
        if col_count > max_cols:
            max_cols = col_count

    num_rows = len(rows)
    # Build an empty grid
    grid: list[list[str | None]] = [[None] * max_cols for _ in range(num_rows)]
    yusho_grid: list[list[bool]] = [[False] * max_cols for _ in range(num_rows)]

    for r_idx, row in enumerate(rows):
        c_idx = 0
        for cell in row.find_all(["th", "td"]):
            # Skip cells already filled by a previous rowspan
            while c_idx < max_cols and grid[r_idx][c_idx] is not None:
                c_idx += 1
            if c_idx >= max_cols:
                break

            colspan = int(cell.get("colspan", 1))
            rowspan = int(cell.get("rowspan", 1))
            value = clean_text(cell.get_text())
            is_yusho = has_palegreen_bg(cell)

            for dr in range(rowspan):
                for dc in range(colspan):
                    rr = r_idx + dr
                    cc = c_idx + dc
                    if rr < num_rows and cc < max_cols:
                        grid[rr][cc] = value if (dr == 0 and dc == 0) else ""
                        yusho_grid[rr][cc] = is_yusho

            c_idx += colspan

    # Replace any remaining None with empty string
    for r in range(num_rows):
        for c in range(max_cols):
            if grid[r][c] is None:
                grid[r][c] = ""

    return grid, yusho_grid


def slugify(text: str, max_len: int = 60) -> str:
    """Turn arbitrary text into a safe filename fragment."""
    import unicodedata
    # Decompose accented chars and drop combining marks
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    # Handle remaining non-ASCII by replacing with underscore
    text = text.encode("ascii", "replace").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text).strip("_")
    return text[:max_len]


def extract_table_title(grid: list[list[str]]) -> str | None:
    """
    If the first row is a single merged title cell (all columns identical or
    only one non-empty value), return that title text.
    """
    if not grid:
        return None
    first_row = grid[0]
    non_empty = [v for v in first_row if v]
    if len(set(non_empty)) == 1:
        return non_empty[0]
    return None


def transform_tournament_grid(
    grid: list[list[str]], yusho_grid: list[list[bool]]
) -> list[list[str]]:
    """
    Transform the 17-column East/West tournament grid into a flat list of
    [Name, Rank, Record] rows.

    Input columns (per row, after title & header):
      0=W 1=- 2=L 3=- 4=A 5=ø? 6='' 7=EastName 8=Rank 9=ø? 10='' 11=WestName
      12=W 13=- 14=L 15=- 16=A

    Output: header row + one row per wrestler with name, rank, and W-L-A record.
    The yusho winner's record is marked with a trailing *.
    Vacant slots (empty name with 0-0-0/0-0-15 record) are skipped.
    """
    if not grid or len(grid) < 3:
        return grid

    # Check if this looks like a tournament table (17 columns, data rows start at index 2)
    if len(grid[0]) != 17:
        return grid

    title = extract_table_title(grid)
    result: list[list[str]] = []

    if title:
        result.append(["Tournament", title])

    result.append(["Name", "Rank", "Record"])

    # Data rows start after title row (index 0) and header row (index 1)
    for r_idx, row in enumerate(grid[2:], start=2):
        if len(row) < 17:
            continue

        rank = row[8]

        # East wrestler — yusho indicated by PaleGreen background on name cell (col 7)
        east_name = row[7].rstrip("*")
        east_yusho = yusho_grid[r_idx][7] if r_idx < len(yusho_grid) else False
        east_record = f"{row[0]}-{row[2]}-{row[4]}{'*' if east_yusho else ''}"

        # West wrestler — yusho indicated by PaleGreen background on name cell (col 11)
        west_name = row[11].rstrip("*")
        west_yusho = yusho_grid[r_idx][11] if r_idx < len(yusho_grid) else False
        west_record = f"{row[12]}-{row[14]}-{row[16]}{'*' if west_yusho else ''}"

        # Add east wrestler if not vacant
        if east_name:
            result.append([east_name, rank, east_record])

        # Add west wrestler if not vacant
        if west_name:
            result.append([west_name, rank, west_record])

    return result


def is_legend_table(grid: list[list[str]]) -> bool:
    """Return True if this is a small legend/notes table (e.g. 'indicates a pull-out')."""
    if len(grid) <= 5:
        full_text = " ".join(cell for row in grid for cell in row).lower()
        if "indicates a pull" in full_text or "absent rank" in full_text:
            return True
    return False


def extract_year(filename: str) -> str | None:
    """Extract a four-digit year from a filename like '2021 in sumo.html'."""
    match = re.search(r"(\d{4})", filename)
    return match.group(1) if match else None


def process_file(html_path: Path, output_base: Path) -> int:
    """Parse one HTML file, write CSV files for each wikitable. Returns count."""
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    # Derive a base name from the filename (e.g. "2021_in_sumo")
    base_name = slugify(html_path.stem)

    # Put CSVs into a year subfolder
    year = extract_year(html_path.name)
    output_dir = output_base / year if year else output_base
    output_dir.mkdir(parents=True, exist_ok=True)

    tables = soup.find_all("table", class_="wikitable")
    if not tables:
        # Fall back to all tables if none have wikitable class
        tables = soup.find_all("table")

    seen_names: dict[str, int] = {}
    count = 0
    for idx, table in enumerate(tables):
        grid, yusho_grid = expand_table(table)
        if not grid or all(all(cell == "" for cell in row) for row in grid):
            continue  # skip empty tables

        # Skip legend/notes tables
        if is_legend_table(grid):
            continue

        # Try to get a descriptive title from the table itself
        title = extract_table_title(grid)
        if title:
            suffix = slugify(title)
        else:
            suffix = f"table_{idx}"

        # De-duplicate filenames
        key = suffix
        if key in seen_names:
            seen_names[key] += 1
            suffix = f"{suffix}_{seen_names[key]}"
        else:
            seen_names[key] = 0

        # Transform tournament result tables into flat Name/Rank/Record rows
        grid = transform_tournament_grid(grid, yusho_grid)

        filename = f"{base_name}_{suffix}.csv"
        out_path = output_dir / filename

        with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            for row in grid:
                writer.writerow(row)

        print(f"  -> {out_path.relative_to(output_base)}")
        count += 1

    return count


def main():
    project_root = Path(__file__).resolve().parent.parent
    years_dir = project_root / "Years"
    output_base = project_root / "output" / "csv"
    output_base.mkdir(parents=True, exist_ok=True)

    html_files = sorted(years_dir.glob("*.html"))
    if not html_files:
        print(f"No .html files found in {years_dir}")
        sys.exit(1)

    total = 0
    for html_file in html_files:
        print(f"\nProcessing: {html_file.name}")
        count = process_file(html_file, output_base)
        total += count

    print(f"\nDone! Exported {total} tables to {output_base}")


if __name__ == "__main__":
    main()
