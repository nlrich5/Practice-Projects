"""Aggregate team counts per city for each sport.

Reads "output/Potential Cities - Sports.csv" and produces a table with one row
per city (keyed by City, State/Prov, Country) and a count column for each sport:
Soccer, Baseball, Hockey.
"""

from pathlib import Path

import pandas as pd

INPUT_PATH = Path("output/Potential Cities - Sports.csv")
OUTPUT_PATH = Path("output/city_sport_counts.csv")

SPORTS = ["Soccer", "Baseball", "Hockey"]
KEYS = ["City", "State/Prov", "Country"]


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    # Count teams per city/sport, then pivot sports into columns.
    counts = (
        df.groupby(KEYS + ["Sport"]).size().unstack("Sport", fill_value=0).reset_index()
    )

    # Ensure all requested sport columns exist, in the desired order.
    for sport in SPORTS:
        if sport not in counts.columns:
            counts[sport] = 0

    result = counts[KEYS + SPORTS].sort_values(KEYS).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"Wrote {len(result)} cities to {OUTPUT_PATH}")
    print(result.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
