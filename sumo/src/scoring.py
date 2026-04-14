import argparse
import csv
import re
import sys

# --- Rank points from docs/proposal-rank-score.md ---

# Fixed sanyaku ranks
_FIXED_RANK_POINTS = {
    "Y":  60000,
    "O":  55000,
    "S":  50000,
    "K":  45000,
}

# Makuuchi maegashira: M1=40000, step -1000
# Juryo: J1=22000, step -1000
# Lower divisions use formulas (see _division_formula below)

_DIVISION_FORMULA = {
    #         prefix, base,  step
    "M":     ("M",   41000, 1000),   # M1 = 41000 - 1*1000 = 40000
    "J":     ("J",   23000, 1000),   # J1 = 23000 - 1*1000 = 22000
    "MS":    ("MS",  6050,  50),     # Ms1 = 6050 - 1*50 = 6000
    "SD":    ("SD",  2825,  25),     # Sd1 = 2825 - 1*25 = 2800
    "JD":    ("JD",  603,   3),      # Jd1 = 603 - 1*3 = 600
    "JK":    ("JK",  184,   4),      # Jk1 = 184 - 1*4 = 180
}

# Points per win above/below baseline
POINTS_PER_WIN_15 = 2000       # 15-bout divisions (Makuuchi, Juryo)
POINTS_PER_WIN_7 = 500         # 7-bout divisions (Makushita and below)

# Divisions that fight 15 bouts (baseline = 8 wins)
_15_BOUT_PREFIXES = {"Y", "O", "S", "K", "M", "J"}
# All others fight 7 bouts (baseline = 4 wins)


def rank_score(rank_str):
    """Convert a rank string (e.g. 'Y', 'O', 'M3', 'J14', 'Ms15') to rank points.

    Returns an integer, or None for unrecognised ranks.
    """
    rank = rank_str.strip().upper()

    if rank in _FIXED_RANK_POINTS:
        return _FIXED_RANK_POINTS[rank]

    if rank == "HD":
        return None

    # Try each division formula: M, J, MS, SD, JD, JK
    for key, (prefix, base, step) in _DIVISION_FORMULA.items():
        if rank.startswith(prefix):
            num_str = rank[len(prefix):]
            if num_str.isdigit():
                num = int(num_str)
                return base - num * step

    return None


def record_points(record_str, rank_str):
    """Compute record bonus/penalty from a record string like '12-3-0'.

    Uses the rank to determine if it's a 15-bout or 7-bout division.
    Returns an integer, or None if the record can't be parsed.
    """
    parts = record_str.strip().rstrip("*").split("-")
    if len(parts) < 2:
        return None

    wins = int(parts[0])
    prefix = re.match(r"[A-Za-z]+", rank_str.strip().upper())
    prefix = prefix.group() if prefix else ""

    if prefix in _15_BOUT_PREFIXES:
        return (wins - 8) * POINTS_PER_WIN_15
    else:
        return (wins - 4) * POINTS_PER_WIN_7


def total_score(rank_str, record_str):
    """Compute total score = rank_points + record_points."""
    rp = rank_score(rank_str)
    if rp is None:
        return None
    rec = record_points(record_str, rank_str)
    if rec is None:
        return rp
    return rp + rec


def read_csv(filepath):
    with open(filepath, newline="", encoding="utf-8") as f:
        first_line = f.readline()
        # If the first line is a tournament metadata row, skip it
        # and use the next line as the header.
        if first_line.startswith("Tournament,"):
            reader = csv.DictReader(f)  # next line becomes header
        else:
            f.seek(0)
            reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def main():
    parser = argparse.ArgumentParser(description="Score sumo data from a CSV file.")
    parser.add_argument("csv_file", help="Path to the input CSV file")
    parser.add_argument("-o", "--output", default=None,
                        help="Path to the output CSV file (default: <input>_scored.csv)")
    args = parser.parse_args()

    rows = read_csv(args.csv_file)
    print(f"Loaded {len(rows)} rows from {args.csv_file}")
    if rows:
        print(f"Columns: {list(rows[0].keys())}")

    # Detect tournament columns: find all columns ending with " Rank"
    if rows:
        all_cols = list(rows[0].keys())
        rank_cols = [c for c in all_cols if c.endswith(" Rank")]
        # Also handle simple "Rank"/"Record" columns
        if not rank_cols and "Rank" in all_cols:
            rank_cols = ["Rank"]

    for row in rows:
        for rank_col in rank_cols:
            # Derive the matching record and score column names
            if rank_col == "Rank":
                record_col = "Record"
                score_col = "TotalScore"
                rp_col = "RankScore"
                rec_col = "RecordPoints"
            else:
                basho = rank_col.rsplit(" Rank", 1)[0]  # e.g. "2025 Hatsu"
                record_col = f"{basho} Record"
                score_col = f"{basho} TotalScore"
                rp_col = f"{basho} RankScore"
                rec_col = f"{basho} RecordPoints"

            rank = row.get(rank_col, "")
            record = row.get(record_col, "")
            if not rank:
                row[rp_col] = ""
                row[rec_col] = ""
                row[score_col] = ""
                continue
            rp = rank_score(rank)
            rec = record_points(record, rank) if rp is not None else None
            ts = total_score(rank, record)
            row[rp_col] = rp if rp is not None else ""
            row[rec_col] = rec if rec is not None else ""
            row[score_col] = ts if ts is not None else ""

    # Determine output path
    output_path = args.output
    if output_path is None:
        base = args.csv_file.rsplit(".", 1)
        output_path = base[0] + "_scored.csv" if len(base) == 2 else args.csv_file + "_scored.csv"

    # Write scored CSV
    if rows:
        fieldnames = list(rows[0].keys())
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
