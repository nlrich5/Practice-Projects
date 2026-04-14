# src/ — Sumo Data Pipeline Scripts

Scripts for downloading, parsing, scoring, and ranking sumo tournament data. Run all scripts from the **project root** directory.

---

## Pipeline Overview

```
1. download_sumo_pages.py   → Downloads Wikipedia HTML pages
2. html_tables_to_csv.py    → Parses HTML tables into per-tournament CSVs
3. merge_csvs.py            → Merges tournament CSVs into a single file
4. score_year.py            → Computes rank/record scores per tournament
5. rank_year.py             → Assigns predicted next-tournament ranks
```

Scoring and ranking can also be done on individual files using `scoring.py` directly.

---

## Scripts

### `download_sumo_pages.py`

Downloads "Year in sumo" Wikipedia pages as HTML files into the `Years/` folder.

```bash
# Download all pages (1992–2025)
python src/download_sumo_pages.py

# Custom year range
python src/download_sumo_pages.py 2000 2010

# Skip files already downloaded
python src/download_sumo_pages.py --skip-existing
```

**Output:** `Years/<year>_in_sumo.html`

---

### `html_tables_to_csv.py`

Parses HTML tables from downloaded Wikipedia pages and exports each as a CSV.

```bash
python src/html_tables_to_csv.py
```

**Output:** `output/csv/<year>/` — one CSV per tournament table (e.g. `2025_in_sumo_2025_hatsu_basho_results_makuuchi_division.csv`)

---

### `merge_csvs.py`

Merges individual tournament CSVs into a single combined CSV spanning a year range. Each wrestler gets one row with columns for every tournament's rank and record.

```bash
# Merge 2024–2025
python src/merge_csvs.py 2024 2025

# Single year
python src/merge_csvs.py 2025 2025
```

**Output:** `output/merged/<start_year>_<end_year>.csv`

---

### `scoring.py`

Core scoring library and standalone script. Computes `RankScore`, `RecordPoints`, and `TotalScore` for each wrestler based on the rank + record point system defined in `docs/proposal-rank-score.md`.

```bash
# Score a single CSV file (auto-names output)
python src/scoring.py output/csv/2025/2025_in_sumo_2025_hatsu_basho_results_makuuchi_division.csv

# Specify output path
python src/scoring.py input.csv -o output.csv
```

Handles both single-tournament CSVs (with `Rank`/`Record` columns) and merged multi-tournament CSVs (with `<Year> <Basho> Rank`/`<Year> <Basho> Record` columns).

**Output columns added:** `RankScore`, `RecordPoints`, `TotalScore` (per tournament if multi-tournament format)

---

### `score_year.py`

Scores all six tournaments for a given year in one command.

```bash
python src/score_year.py 2025
```

**Input:** `output/csv/<year>/` (per-tournament CSVs from `html_tables_to_csv.py`)
**Output:** `output/scoring/<year>/<year>_<basho>.csv` (e.g. `output/scoring/2025/2025_hatsu.csv`)

Each output CSV contains the original columns plus `RankScore`, `RecordPoints`, and `TotalScore`.

---

### `rank_year.py`

Assigns a `PredictedRank` to each wrestler for all tournaments in a year. Processes tournaments sequentially (Hatsu → Kyushu) and applies the special ranking rules from `docs/proposal-rank-score.md`:

- **Yokozuna** are pinned — never demoted regardless of record
- **Yokozuna promotion** — Ozeki with 2 consecutive championships (or equivalent 12+ win performances)
- **Ozeki kadoban** — first losing record as Ozeki triggers kadoban; second consecutive losing record demotes to Sekiwake
- **Ozeki promotion** — S/K wrestlers with 33+ wins over 3 tournaments (10+ in the most recent)
- **Ozeki re-promotion** — demoted Ozeki at Sekiwake with 10+ wins returns to Ozeki
- Remaining wrestlers sorted by `TotalScore` descending → assigned S (2), K (2), then M1–M17 (2 per rank)

```bash
# Must run score_year.py first
python src/score_year.py 2025
python src/rank_year.py 2025
```

**Input/Output:** Reads and updates CSVs in `output/scoring/<year>/` in place, adding the `PredictedRank` column.

If scored data exists for the previous year, it is loaded automatically to provide tournament history context for promotion checks and kadoban tracking.

---

## Typical Full Pipeline

```bash
# 1. Download Wikipedia pages
python src/download_sumo_pages.py

# 2. Parse HTML to CSVs
python src/html_tables_to_csv.py

# 3. (Optional) Merge into a single file
python src/merge_csvs.py 2024 2025

# 4. Score a year
python src/score_year.py 2025

# 5. Assign predicted ranks
python src/rank_year.py 2025
```

Results will be in `output/scoring/2025/` with columns:
`Name, Rank, Record, RankScore, RecordPoints, TotalScore, PredictedRank`

---

## Directory Structure

```
output/
├── csv/<year>/          # Per-tournament CSVs from HTML parsing
├── merged/              # Merged multi-year CSVs
└── scoring/<year>/      # Scored + ranked tournament CSVs
```
