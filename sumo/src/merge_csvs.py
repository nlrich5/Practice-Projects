"""
Merge individual tournament CSV files into a single combined CSV.

Usage:
    python src/merge_csvs.py <start_year> <end_year>

Output goes to output/merged/<start_year>_<end_year>.csv

Columns:
    Name, (Year) Hatsu Rank, (Year) Hatsu Record, (Year) Haru Rank, ...
    repeated for each tournament in chronological order:
        Hatsu, Haru, Natsu, Nagoya, Aki, Kyushu

Wrestlers appear in the merged output if they competed in at least one
tournament in the range.  Missing tournaments show empty cells.
"""

import csv
import re
import sys
from collections import OrderedDict
from pathlib import Path

BASHO_ORDER = ["hatsu", "haru", "natsu", "nagoya", "aki", "kyushu"]
BASHO_DISPLAY = {
    "hatsu": "Hatsu",
    "haru": "Haru",
    "natsu": "Natsu",
    "nagoya": "Nagoya",
    "aki": "Aki",
    "kyushu": "Kyushu",
}


def find_csv_for_basho(year_dir: Path, basho: str) -> Path | None:
    """Find the CSV file for a given basho in a year directory."""
    for f in year_dir.iterdir():
        if f.suffix == ".csv" and f"_{basho}_basho_" in f.name:
            return f
    return None


def parse_tournament_csv(path: Path) -> list[tuple[str, str, str]]:
    """
    Parse a tournament CSV and return a list of (name, rank, record) tuples.

    Expected format:
        Tournament,<title>
        Name,Rank,Record
        <name>,<rank>,<record>
        ...
    """
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        in_data = False
        for row in reader:
            if not row:
                continue
            if row[0] == "Name" and len(row) >= 3:
                in_data = True
                continue
            if in_data and len(row) >= 3:
                name, rank, record = row[0], row[1], row[2]
                if name:
                    rows.append((name, rank, record))
    return rows


def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <start_year> <end_year>")
        sys.exit(1)

    start_year = int(sys.argv[1])
    end_year = int(sys.argv[2])

    if start_year > end_year:
        print("Error: start_year must be <= end_year")
        sys.exit(1)

    project_root = Path(__file__).resolve().parent.parent
    csv_base = project_root / "output" / "csv"
    output_dir = project_root / "output" / "merged"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build the list of (year, basho) tournament slots in chronological order
    tournament_slots: list[tuple[int, str]] = []
    for year in range(start_year, end_year + 1):
        for basho in BASHO_ORDER:
            tournament_slots.append((year, basho))

    # Collect data: wrestlers[name][(year, basho)] = (rank, record)
    wrestlers: OrderedDict[str, dict[tuple[int, str], tuple[str, str]]] = OrderedDict()

    for year in range(start_year, end_year + 1):
        year_dir = csv_base / str(year)
        if not year_dir.is_dir():
            print(f"Warning: no data directory for {year}, skipping")
            continue

        for basho in BASHO_ORDER:
            csv_path = find_csv_for_basho(year_dir, basho)
            if csv_path is None:
                continue

            entries = parse_tournament_csv(csv_path)
            for name, rank, record in entries:
                if name not in wrestlers:
                    wrestlers[name] = {}
                wrestlers[name][(year, basho)] = (rank, record)

    # Sort wrestlers alphabetically
    sorted_names = sorted(wrestlers.keys())

    # Build header
    header = ["Name"]
    for year, basho in tournament_slots:
        label = f"{year} {BASHO_DISPLAY[basho]}"
        header.append(f"{label} Rank")
        header.append(f"{label} Record")

    # Build rows
    out_path = output_dir / f"{start_year}_{end_year}.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for name in sorted_names:
            row = [name]
            data = wrestlers[name]
            for slot in tournament_slots:
                if slot in data:
                    rank, record = data[slot]
                    row.append(rank)
                    row.append(record)
                else:
                    row.append("")
                    row.append("")
            writer.writerow(row)

    print(f"Merged {len(sorted_names)} wrestlers across {len(tournament_slots)} "
          f"tournament slots -> {out_path}")


if __name__ == "__main__":
    main()
