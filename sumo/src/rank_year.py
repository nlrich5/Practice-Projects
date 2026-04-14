"""Assign predicted next-tournament ranks based on TotalScore + special rules.

Usage:
    python src/rank_year.py 2025

Reads scored CSVs from output/scoring/<year>/, adds a PredictedRank column,
and writes them back in place.
"""
import argparse
import csv
import os
import re
import sys

from scoring import read_csv

BASHO_ORDER = ["hatsu", "haru", "natsu", "nagoya", "aki", "kyushu"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_wins(record_str):
    """Extract wins from a record string like '12-3-0' or '12-3-0*'."""
    parts = record_str.strip().rstrip("*").split("-")
    if len(parts) >= 1 and parts[0].isdigit():
        return int(parts[0])
    return 0


def parse_losses(record_str):
    """Extract losses from a record string."""
    parts = record_str.strip().rstrip("*").split("-")
    if len(parts) >= 2 and parts[1].isdigit():
        return int(parts[1])
    return 0


def is_makekoshi(record_str, rank_str):
    """Return True if the record is a losing record for the division."""
    wins = parse_wins(record_str)
    prefix = re.match(r"[A-Za-z]+", rank_str.strip().upper())
    prefix = prefix.group() if prefix else ""
    if prefix in {"Y", "O", "S", "K", "M", "J"}:
        return wins < 8
    else:
        return wins < 4


def is_champion(record_str):
    """Heuristic: record string ends with '*' indicating a tournament win."""
    return record_str.strip().endswith("*")


def rank_prefix(rank_str):
    m = re.match(r"[A-Za-z]+", rank_str.strip())
    return m.group().upper() if m else ""


# ---------------------------------------------------------------------------
# Rank assignment engine
# ---------------------------------------------------------------------------

def assign_ranks(wrestlers, ozeki_kadoban, history):
    """Assign PredictedRank to each wrestler dict (in place).

    Args:
        wrestlers: list of dicts with Name, Rank, Record, TotalScore
        ozeki_kadoban: set of wrestler names currently kadoban
        history: list of prior tournament lists (each is list of dicts)
                 most recent last. Used for promotion checks.

    Returns:
        updated ozeki_kadoban set for next tournament.
    """
    # Build lookup for this tournament
    by_name = {w["Name"]: w for w in wrestlers}

    # --- Step 1: Determine who stays Yokozuna (pinned) ---
    yokozuna = []
    for w in wrestlers:
        if rank_prefix(w["Rank"]) == "Y":
            yokozuna.append(w["Name"])

    # --- Step 2: Yokozuna promotion check ---
    # Ozeki with 2 consecutive championships or equivalent
    for w in wrestlers:
        if rank_prefix(w["Rank"]) == "O" and w["Name"] not in yokozuna:
            if _check_yokozuna_promotion(w, history):
                yokozuna.append(w["Name"])

    # --- Step 3: Determine Ozeki ---
    new_kadoban = set()
    ozeki = []

    for w in wrestlers:
        name = w["Name"]
        if name in yokozuna:
            continue
        rp = rank_prefix(w["Rank"])
        record = w.get("Record", "")

        if rp == "O":
            if is_makekoshi(record, w["Rank"]):
                if name in ozeki_kadoban:
                    # Second consecutive makekoshi -> demote to S
                    # (handled below, not added to ozeki list)
                    continue
                else:
                    # First makekoshi -> kadoban, stays O
                    new_kadoban.add(name)
                    ozeki.append(name)
            else:
                # Winning record -> stays O, clears kadoban
                ozeki.append(name)

    # --- Step 4: Ozeki promotion check ---
    # S/K with 33+ wins over last 3 tournaments (including current)
    for w in wrestlers:
        name = w["Name"]
        if name in yokozuna or name in ozeki:
            continue
        rp = rank_prefix(w["Rank"])
        if rp in ("S", "K"):
            if _check_ozeki_promotion(w, history):
                ozeki.append(name)

    # --- Step 5: Ozeki re-promotion check ---
    # Demoted ozeki at S with 10+ wins -> back to O
    for w in wrestlers:
        name = w["Name"]
        if name in yokozuna or name in ozeki:
            continue
        rp = rank_prefix(w["Rank"])
        if rp == "S" and name in ozeki_kadoban:
            # This was a demoted ozeki at sekiwake
            if parse_wins(w.get("Record", "")) >= 10:
                ozeki.append(name)

    # --- Step 6: Sort remaining wrestlers by TotalScore ---
    assigned = set(yokozuna) | set(ozeki)
    remaining = [w for w in wrestlers if w["Name"] not in assigned]

    # Sort by TotalScore descending (handle empty/missing)
    def sort_key(w):
        ts = w.get("TotalScore", "")
        return int(ts) if ts != "" else -999999
    remaining.sort(key=sort_key, reverse=True)

    # Also sort ozeki by score for ordering within rank
    ozeki_ws = [by_name[n] for n in ozeki]
    ozeki_ws.sort(key=sort_key, reverse=True)
    ozeki = [w["Name"] for w in ozeki_ws]

    yokozuna_ws = [by_name[n] for n in yokozuna]
    yokozuna_ws.sort(key=sort_key, reverse=True)
    yokozuna = [w["Name"] for w in yokozuna_ws]

    # --- Step 7: Assign rank labels ---
    # Yokozuna
    for name in yokozuna:
        by_name[name]["PredictedRank"] = "Y"

    # Ozeki
    for name in ozeki:
        by_name[name]["PredictedRank"] = "O"

    # From remaining, assign S, K, then maegashira
    # Standard: 2 Sekiwake, 2 Komusubi, then M1-M17 (2 per rank)
    # But if fewer wrestlers available, adjust
    idx = 0

    # Sekiwake: minimum 1, typically 2
    n_seki = min(2, len(remaining) - idx)
    for i in range(n_seki):
        remaining[idx]["PredictedRank"] = "S"
        idx += 1

    # Komusubi: minimum 1, typically 2
    n_komu = min(2, len(remaining) - idx)
    for i in range(n_komu):
        remaining[idx]["PredictedRank"] = "K"
        idx += 1

    # Maegashira: 2 per rank number
    mae_num = 1
    while idx < len(remaining):
        slots = min(2, len(remaining) - idx)
        for i in range(slots):
            remaining[idx]["PredictedRank"] = f"M{mae_num}"
            idx += 1
        mae_num += 1

    # Wrestlers with no TotalScore (shouldn't happen in scored data, but safety)
    for w in wrestlers:
        if "PredictedRank" not in w:
            w["PredictedRank"] = ""

    return new_kadoban


def _check_yokozuna_promotion(wrestler, history):
    """Check if an Ozeki qualifies for Yokozuna promotion.

    Criteria: 2 consecutive championships as Ozeki, or equivalent
    (championship + runner-up with no record below 12 wins in last 3).
    """
    name = wrestler["Name"]
    record = wrestler.get("Record", "")
    wins = parse_wins(record)

    # Need at least one prior tournament
    if not history:
        return False

    # Current tournament must be a championship
    if not is_champion(record):
        return False

    # Check previous tournament
    prev = _find_wrestler_in_tournament(name, history[-1])
    if not prev:
        return False

    prev_rp = rank_prefix(prev.get("Rank", ""))
    if prev_rp not in ("O", "Y"):
        return False

    prev_wins = parse_wins(prev.get("Record", ""))

    # Two consecutive championships
    if is_champion(prev.get("Record", "")) and is_champion(record):
        return True

    # Equivalent: both 12+ wins, at least one championship
    if wins >= 12 and prev_wins >= 12:
        return True

    return False


def _check_ozeki_promotion(wrestler, history):
    """Check if an S/K qualifies for Ozeki promotion.

    Criteria: 33+ wins over last 3 tournaments while at S/K,
    with 10+ wins in the most recent.
    """
    name = wrestler["Name"]
    current_wins = parse_wins(wrestler.get("Record", ""))

    if current_wins < 10:
        return False

    # Gather wins from last 3 tournaments (current + 2 prior)
    total_wins = current_wins
    tournaments_counted = 1

    for prev_tourney in reversed(history[-2:]):
        prev = _find_wrestler_in_tournament(name, prev_tourney)
        if prev:
            prev_rp = rank_prefix(prev.get("Rank", ""))
            if prev_rp in ("S", "K", "O"):
                total_wins += parse_wins(prev.get("Record", ""))
                tournaments_counted += 1

    if tournaments_counted >= 3 and total_wins >= 33:
        return True

    # Also allow 2-tournament promotion with very high wins (rare but possible)
    if tournaments_counted >= 2 and total_wins >= 33:
        return True

    return False


def _find_wrestler_in_tournament(name, tournament_rows):
    """Find a wrestler by name in a tournament's row list."""
    for w in tournament_rows:
        if w.get("Name") == name:
            return w
    return None


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def find_scored_csvs(year):
    """Find scored CSVs in output/scoring/<year>/ in basho order."""
    scoring_dir = os.path.join("output", "scoring", str(year))
    if not os.path.isdir(scoring_dir):
        print(f"Error: directory not found: {scoring_dir}", file=sys.stderr)
        sys.exit(1)

    ordered = []
    for basho in BASHO_ORDER:
        expected = os.path.join(scoring_dir, f"{year}_{basho}.csv")
        if os.path.exists(expected):
            ordered.append((basho, expected))
    return ordered


def write_csv(rows, filepath):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Assign predicted ranks for all tournaments in a year.")
    parser.add_argument("year", type=int, help="Year to process (e.g. 2025)")
    args = parser.parse_args()

    year = args.year
    scored_csvs = find_scored_csvs(year)

    if not scored_csvs:
        print(f"No scored CSVs found for {year}.", file=sys.stderr)
        sys.exit(1)

    print(f"Ranking {len(scored_csvs)} tournaments for {year}...")

    # Also try to load previous year's last tournament for history context
    history = []
    prev_year_csvs = find_scored_csvs(year - 1) if os.path.isdir(
        os.path.join("output", "scoring", str(year - 1))) else []
    for basho, path in prev_year_csvs[-2:]:  # last 2 of previous year
        rows = read_csv(path)
        history.append(rows)

    ozeki_kadoban = set()

    # Detect initial kadoban from first tournament if we have prior history
    # (A wrestler who was O last tournament with makekoshi is kadoban now)
    if history:
        last_prev = history[-1]
        for w in last_prev:
            if rank_prefix(w.get("Rank", "")) == "O" and is_makekoshi(
                    w.get("Record", ""), w.get("Rank", "")):
                ozeki_kadoban.add(w["Name"])

    for basho, csv_path in scored_csvs:
        rows = read_csv(csv_path)

        ozeki_kadoban = assign_ranks(rows, ozeki_kadoban, history)
        history.append(rows)

        write_csv(rows, csv_path)
        print(f"  {basho:8s}: ranked {len(rows)} wrestlers -> {csv_path}")

        # Show top ranks
        for w in rows:
            pr = w.get("PredictedRank", "")
            if pr in ("Y", "O", "S", "K"):
                print(f"           {w['Name']:20s} {w['Rank']:4s} {w.get('Record',''):8s} "
                      f"-> {pr}")

    print("Done.")


if __name__ == "__main__":
    main()
