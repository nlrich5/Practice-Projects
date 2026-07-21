# NHL Schedule Parser — AI Dev Log

## Project Overview

**Goal:** Parse a 64-page NHL schedule PDF and extract game data into a CSV.  
**Source file:** `schedule.pdf` — 32 teams × 2 pages each. Page 0 of each pair is a graphic-only page that cannot be text-extracted; page 1 contains the readable schedule.  
**Tools:** Python, `pypdf`, `csv`, `json`, `re`

---

## Iteration 1 — Basic Text Extraction

**Task:** Extract and print the Anaheim Ducks' schedule from the PDF.

The PDF was structured with two pages per team. The first page (even index) was a graphic that yielded no usable text. The second page (odd index) contained the full schedule as extractable text. Page index `1` was confirmed as the Ducks' schedule.

The initial `main.py` simply loaded the PDF with `pypdf` and printed the raw text of page index `1` to verify extraction was working.

```python
from pypdf import PdfReader

reader = PdfReader("schedule.pdf")
first_page = reader.pages[1]
text = first_page.extract_text()
print(text)
```

**Output confirmed** the page rendered as a two-column layout, with each line containing up to two game entries side by side:

```
Fri.   Oct 2 7:00 PM  AT Vegas Sun.   Jan 3 5:00 PM     Philadelphia
Sun.   Oct 4 5:00 PM     Florida Tue.   Jan 5 7:00 PM     Minnesota
...
```

---

## Iteration 2 — Regex Parsing & CSV Output

**Task:** Parse the raw text into structured rows and write to a CSV.

A regex (`GAME_PATTERN`) was written to capture each game entry:

| Group | Captures |
|-------|----------|
| 1 | Day abbreviation (`Mon`, `Tue`, etc.) |
| 2 | Month + day number (`Oct 2`) |
| 3 | Time (`7:00 PM`) |
| 4 | Optional `AT ` prefix (away game indicator) |
| 5 | Opponent name |

The opponent name used a lazy match terminated by a lookahead. Two lookahead attempts were made:

- **First attempt** used `\s{2,}` (2+ spaces) to find the boundary between the left and right columns — this only matched the right-column games (42 of 84), missing all left-column entries where only a single space separated the opponent from the next day token.
- **Second attempt** broadened the lookahead to `\s+(?:Mon|Tue|...)\.|\s*$|\s*\n`, correctly matching both columns and capturing all **84 games**.

CSV columns at this stage: `Day`, `Date`, `Time`, `Location` (`Home`/`Away`), `Opponent`.

---

## Iteration 3 — Home Team / Away Team Columns

**Task:** Replace the `Location` + `Opponent` columns with `Home Team` and `Away Team`.

The `AT` flag was repurposed: instead of setting a `Location` string, it now determines which side of the matchup each team occupies.

```python
if at_flag:
    home_team = opponent   # game is at the opponent's arena
    away_team = "Anaheim Ducks"
else:
    home_team = "Anaheim Ducks"
    away_team = opponent
```

**Result:** CSV now has columns `Day`, `Date`, `Time`, `Home Team`, `Away Team`.  
Verified 42 home and 42 away games — correct for an 84-game season.

---

## Iteration 4 — Multi-Team Support via `teams.json`

**Task:** Create `create_teams_json.py` to build a JSON registry of all 32 teams with their PDF page indices and a `selected` flag.

Each odd-indexed page footer contained a line matching `"Schedule for the <Team Name>"`. The script iterated every other page, extracted the team name via regex, and wrote a JSON array:

```json
{
  "team": "Anaheim Ducks",
  "page_index": 1,
  "selected": "no"
}
```

All 32 teams were captured across page indices 1, 3, 5, … 63.

`main.py` was then refactored to:
1. Load `teams.json` and filter to `selected == "yes"` entries.
2. Extract and parse each selected team's schedule page.
3. Output one CSV file per team, named `<team_name>_schedule.csv`.

The hardcoded `"Anaheim Ducks"` string was replaced with the dynamic `team["team"]` value, and the parsing logic was moved into a reusable `parse_schedule(text, team_name)` function.

---

## Iteration 5 — Single Output File

**Task:** Consolidate all selected teams' games into one `schedule.csv` instead of per-team files.

Rather than opening and writing a file inside the loop, all parsed games were accumulated into a single `all_games` list and written once after the loop:

```python
all_games = []
for team in selected_teams:
    games = parse_schedule(...)
    all_games.extend(games)

with open("schedule.csv", "w", ...) as f:
    writer.writerows(all_games)
```

---

## Iteration 6 — Full Team Name Resolution

**Problem:** The PDF's opponent column uses shorthand city/location names (`Vegas`, `Florida`, `Tampa Bay`) rather than full team names. When these appeared as `Home Team` or `Away Team` values in the CSV, they were ambiguous and incomplete.

**Investigation:** All unique non-selected team names were extracted from the CSV and compared against `teams.json`. The short names corresponded to the city or location portion of the full team name, but a programmatic "drop last word" approach was unreliable due to multi-word nicknames (`Blue Jackets`, `Red Wings`, `Maple Leafs`, `Golden Knights`) and the `N.Y.` collision (Islanders vs. Rangers).

**Solution:** A hardcoded `SHORT_NAME_MAP` dictionary was added mapping all 32 shorthand names to their full team names:

```python
SHORT_NAME_MAP = {
    "Vegas":    "Vegas Golden Knights",
    "Florida":  "Florida Panthers",
    "Columbus": "Columbus Blue Jackets",
    ...
}
```

The opponent value is resolved via `SHORT_NAME_MAP.get(opponent, opponent)`, with a safe fallback to the raw value if no mapping exists.

**Result:** Zero single-word team names remaining in the output.

---

## Iteration 7 — Deduplication

**Problem:** When multiple selected teams have played each other, the same game appears in both teams' schedule pages and gets written twice to `schedule.csv`. For example, with Anaheim and Boston both selected, their two head-to-head matchups each appeared twice.

**Solution:** After collecting `all_games`, a deduplication pass was added using a `dict` keyed on `(Date, Home Team, Away Team)` — the three fields that uniquely identify a game. `dict.setdefault` keeps the first occurrence and silently ignores any duplicate:

```python
seen = {}
for game in all_games:
    key = (game["Date"], game["Home Team"], game["Away Team"])
    seen.setdefault(key, game)
all_games = list(seen.values())
```

**Result:** 168 raw rows → 166 deduplicated rows (2 Anaheim vs. Boston games removed).

---

## Final File Summary

| File | Purpose |
|------|---------|
| `main.py` | Reads `teams.json`, parses selected teams' schedules from `schedule.pdf`, deduplicates, and writes `schedule.csv` |
| `create_teams_json.py` | One-time script to generate `teams.json` with all 32 teams, their page indices, and a `selected` flag |
| `teams.json` | Registry of all 32 NHL teams — edit `selected` to `"yes"` to include a team |
| `schedule.csv` | Output — deduplicated game rows with `Day`, `Date`, `Time`, `Home Team`, `Away Team` |

## Post-AI Updates

- `create_teams_json.py` was deleted since it was a one-time script
- `main.py` has been renamed to `pdf_parser.py` in order to not conflict with Flask frontend
- `teams.json` has been renamed to `config.json` since it will handle more than just the teams
- 