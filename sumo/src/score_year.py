"""Score all tournament CSVs for a given year.

Usage:
    python src/score_year.py 2025

Reads per-tournament CSVs from output/csv/<year>/ and writes scored CSVs
to output/scoring/<year>/.
"""
import argparse
import os
import sys

from scoring import read_csv, rank_score, record_points, total_score

import csv


BASHO_ORDER = ["hatsu", "haru", "natsu", "nagoya", "aki", "kyushu"]


def find_tournament_csvs(year):
    """Find all tournament CSVs for a year, returned in basho order."""
    csv_dir = os.path.join("output", "csv", str(year))
    if not os.path.isdir(csv_dir):
        print(f"Error: directory not found: {csv_dir}", file=sys.stderr)
        sys.exit(1)

    files = os.listdir(csv_dir)
    ordered = []
    for basho in BASHO_ORDER:
        for f in files:
            if basho in f.lower() and f.endswith(".csv"):
                ordered.append(os.path.join(csv_dir, f))
                break
    return ordered


def basho_name_from_path(filepath):
    """Extract basho name (e.g. 'hatsu') from the CSV filename."""
    fname = os.path.basename(filepath).lower()
    for basho in BASHO_ORDER:
        if basho in fname:
            return basho
    return os.path.splitext(os.path.basename(filepath))[0]


def score_tournament(rows):
    """Add RankScore, RecordPoints, TotalScore columns to rows in-place."""
    for row in rows:
        rank = row.get("Rank", "")
        record = row.get("Record", "")
        if not rank:
            row["RankScore"] = ""
            row["RecordPoints"] = ""
            row["TotalScore"] = ""
            continue
        rp = rank_score(rank)
        rec = record_points(record, rank) if rp is not None else None
        ts = total_score(rank, record)
        row["RankScore"] = rp if rp is not None else ""
        row["RecordPoints"] = rec if rec is not None else ""
        row["TotalScore"] = ts if ts is not None else ""


def write_csv(rows, filepath):
    """Write rows to a CSV file."""
    if not rows:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Score all tournament CSVs for a given year.")
    parser.add_argument("year", type=int, help="Year to process (e.g. 2025)")
    args = parser.parse_args()

    year = args.year
    tournament_csvs = find_tournament_csvs(year)

    if not tournament_csvs:
        print(f"No tournament CSVs found for {year}.", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.join("output", "scoring", str(year))
    os.makedirs(out_dir, exist_ok=True)

    print(f"Scoring {len(tournament_csvs)} tournaments for {year}...")

    for csv_path in tournament_csvs:
        basho = basho_name_from_path(csv_path)
        rows = read_csv(csv_path)
        score_tournament(rows)

        out_path = os.path.join(out_dir, f"{year}_{basho}.csv")
        write_csv(rows, out_path)
        print(f"  {basho:8s}: {len(rows)} wrestlers -> {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
