# Migration: Data Pipeline → Sumo Management Game

This document covers the architectural shift from the current CSV-based analysis pipeline to a SQLite-backed game engine.

---

## Roster Approach: Fictional Wrestlers Inspired by Real Archetypes

The game will use a fully fictional roster rather than real wrestler names and career records. This avoids cultural sensitivity around depicting revered athletes in a game context, sidesteps right-of-publicity concerns if the game is ever distributed, and removes the obligation to accurately port 30+ years of real career data.

The real sumo *system* is entirely preserved — the six divisions, the banzuke, promotion and demotion rules, the six annual basho, the yusho. None of that is proprietary.

### Archetype Approach

Fictional wrestlers are built around recognizable sumo archetypes rather than named individuals:

| Archetype | Description |
|---|---|
| The Dominant Yokozuna | A long-reigning champion from a wrestling-rich country, seemingly unbeatable in his prime |
| The Hometown Hero | A Japanese-born wrestler beloved by crowds, always competitive but just short of the top |
| The Veteran | A former Ozeki fighting to stay relevant, respected but fading |
| The Prodigy | A young wrestler rocketing up the ranks, inconsistent but explosive |
| The Grinder | A mid-maegashira who never misses a tournament and never surprises anyone |
| The Giant | An enormous wrestler who wins on size alone in the lower divisions but struggles with technique at the top |

These archetypes inform starting attributes (baseline win probability, injury risk, rank ceiling) without mapping to any specific real person.

### Historical Data as a Tuning Tool

The existing CSV pipeline still serves a purpose: run the simulation against real historical outcomes (1992–present) to calibrate win probabilities and rank movement rates. Once the simulation produces realistic-looking banzuke progression, the historical data has done its job and the game proceeds entirely with fictional wrestlers.

---

## Why Migrate

The current pipeline was built to verify the scoring and ranking system against historical Wikipedia data. It works well for that purpose, but has structural problems for a game:

- CSVs have no relationships — linking wrestlers to stables, results to tournaments, or tracking career history requires complex multi-file joins in Python
- Mutating files in place (e.g. `rank_year.py` rewriting scored CSVs) makes re-running steps error-prone
- No concept of mutable game state — injuries, age, stamina, contracts cannot be cleanly modeled in flat files
- Querying (e.g. "all Ozeki with a losing record this year") requires manual Python loops instead of a single SQL statement

---

## New Pipeline Overview

### Phase 1: Calibration (one-time)

Run the simulation against real historical data to tune win probability and rank movement parameters until the model produces realistic banzuke progression.

```
Wikipedia HTML  →  html_tables_to_csv.py  →  scoring.py  →  calibrate.py  →  tuned parameters
```

Once parameters are satisfactory, the historical pipeline is archived. The game starts with a hand-crafted fictional roster seeded directly into SQLite — not ported from real records.

**Better calibration source:** [sumodb.sumogames.de](http://sumodb.sumogames.de) (Sumo Reference) has structured bout-level data for every tournament since the 1950s — far more granular than Wikipedia tournament summaries.

---

### Phase 2: Game Loop (each basho)

```
sumo.db (current state)
    │
    ▼
Player decisions (stable management, training, etc.)
    │
    ▼
Day-by-day tournament simulation (matchup_engine.py → bout outcome)
    │
    ▼
scoring.py  →  score each wrestler's final result
    │
    ▼
DynamicBanzukeEngine  →  assign new ranks (with Yokozuna/Ozeki promotion rules)
    │
    ▼
Write results + new ranks  →  sumo.db
    │
    ▼
Advance time → next basho
```

Six basho per year: Hatsu (Jan), Haru (Mar), Natsu (May), Nagoya (Jul), Aki (Sep), Kyushu (Nov).

---

## Tournament Simulation: Matchup Engine

Each tournament runs 15 days. Matchups are generated day-by-day by `matchup_engine.py`, which reads from `src/config/matchup_schedule.json`.

### Three-Stage Structure

**Stage 1 — Days 1–8: Position-based schedule**

Wrestlers are assigned a rank position (1–42) at the start of each tournament. The matchup schedule in config maps position pairs for each day. Buckets keep competitive tiers separated:

- Bucket A (Joi): all sanyaku + top `sanyaku_count` maegashira (size = `sanyaku_count * 2`)
- Bucket B (Mid): next half of remaining maegashira
- Bucket C (Lower): bottom half of remaining maegashira

The full 8-day position schedule is hardcoded in `matchup_schedule.json`. If a scheduled pair has already fought (e.g. due to a mid-tournament withdrawal), a fallback opponent is selected by rank proximity.

**Stage 2 — Days 9–12: Weighted rank + record buckets**

Wrestlers are sorted by a blended score and split into three dynamic buckets:

```
stage2_score = (record_weight * wins) + (rank_weight * (42 - rank_position))
```

Default weights: `record_weight = 0.6`, `rank_weight = 0.4` (tunable in config). Within each bucket, `networkx.min_weight_matching` finds the optimal pairing by score similarity, guaranteeing no forced rematches as long as unmet opponents exist in the bucket.

**Stage 3 — Days 13–15: Pure Swiss**

Sorted strictly by wins (rank as tiebreaker). Single pool, no buckets. The yusho race drives matchups — the leader faces the closest chaser every day.

### Leader Protection

In stages 2 and 3, the top two wrestlers in the hot bucket are prevented from meeting each other until a valid swap is no longer possible. This preserves the marquee yusho-deciding matchup for the final days.

### Bout Outcome Simulation

Once matched, bout outcomes are resolved by a win probability model:

```
win_probability = sigmoid(rank_diff + form_bonus + random_noise)
```

Where `rank_diff` is the numeric rank gap, `form_bonus` reflects current tournament record relative to expectation, and `random_noise` introduces realistic upset variance. Wrestler attributes (win probability baseline, injury risk) act as additional modifiers.

---

## Suggested SQLite Schema

```sql
CREATE TABLE stables (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    head_coach  TEXT
);

CREATE TABLE wrestlers (
    id               INTEGER PRIMARY KEY,
    name             TEXT NOT NULL,
    stable_id        INTEGER REFERENCES stables(id),
    birth_year       INTEGER,
    rank             TEXT,           -- current rank string: Y, O, S, K, M3, J11, etc.
    rank_val         REAL,           -- float encoding used by DynamicBanzukeEngine
    is_yokozuna      INTEGER DEFAULT 0,
    is_ozeki         INTEGER DEFAULT 0,
    is_kadoban       INTEGER DEFAULT 0,
    retirement_date  TEXT            -- NULL if active
);

CREATE TABLE tournaments (
    id      INTEGER PRIMARY KEY,
    year    INTEGER NOT NULL,
    basho   TEXT NOT NULL,           -- Hatsu, Haru, Natsu, Nagoya, Aki, Kyushu
    date    TEXT                     -- ISO date of first day
);

CREATE TABLE results (
    id            INTEGER PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id),
    wrestler_id   INTEGER REFERENCES wrestlers(id),
    rank_at_time  TEXT NOT NULL,     -- rank held entering the tournament
    wins          INTEGER NOT NULL,
    losses        INTEGER NOT NULL,
    absences      INTEGER DEFAULT 0,
    is_yusho      INTEGER DEFAULT 0  -- 1 if tournament winner
);

CREATE TABLE bouts (
    id            INTEGER PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id),
    day           INTEGER NOT NULL,       -- 1–15
    wrestler_a_id INTEGER REFERENCES wrestlers(id),
    wrestler_b_id INTEGER REFERENCES wrestlers(id),
    winner_id     INTEGER REFERENCES wrestlers(id),
    position_a    INTEGER,               -- ordinal rank position at time of matchup
    position_b    INTEGER
);
```

`results` replaces all files in `output/csv/`, `output/merged/`, and `output/scoring/`. `bouts` enables per-day matchup history, rematch prevention, and post-hoc analysis of the matchup schedule.

---

## Shared Data Model: `wrestler.py`

All scripts that work with wrestler objects import from `src/wrestler.py` rather than defining their own class:

```python
@dataclass
class Wrestler:
    id: int
    name: str
    wins: int = 0
    losses: int = 0
    rank_position: int = 0      # 1-42 ordinal assigned at tournament start
    rank_val: float = 0.0       # float encoding used by DynamicBanzukeEngine
    target_val: float = 0.0     # performance target score calculated post-basho
    is_yokozuna: bool = False
    is_ozeki: bool = False
    is_kadoban: bool = False
```

---

## Fate of Current Scripts

| Script | Status | Notes |
|---|---|---|
| `download_sumo_pages.py` | Retire after calibration | Only needed for historical data |
| `html_tables_to_csv.py` | Retire after calibration | Only needed for historical data |
| `merge_csvs.py` | Retire | Replaced by SQL queries across `results` + `tournaments` |
| `scoring.py` | **Keep** | Called during simulation to score each tournament result |
| `score_year.py` | Retire | Scoring now happens in-memory during the game loop |
| `rank_year.py` | Replace | Logic folded into upgraded `DynamicBanzukeEngine` |
| `rank_gemini.py` | **Promote to core** | Becomes the ranking engine; needs Yokozuna/Ozeki rules ported in from `rank_year.py` |
| `matchup_engine.py` | **New — keep** | Generates day-by-day tournament matchups |
| `wrestler.py` | **New — keep** | Shared `Wrestler` dataclass imported by all scripts |

---

## Integrating `rank_gemini.py`

`rank_gemini.py` has the right architecture (wrestler objects, dynamic slot assignment) but is missing the special-case promotion rules that `rank_year.py` handles. Before promoting it to the core engine:

1. Port kadoban tracking from `rank_year.py` into `DynamicBanzukeEngine`
2. Port Yokozuna promotion checks (2 consecutive championships, or dual 12+ performances)
3. Port Ozeki promotion checks (33+ wins over 3 tournaments, 10+ in most recent)
4. Port Ozeki re-promotion (demoted Ozeki at Sekiwake with 10+ wins)
5. Replace the hardcoded test scenarios with real data loaded from SQLite

See `docs/promotion_rules.md` for the official criteria and `rank_year.py` for the current implementation of each rule.

---

## Migration Steps

1. **Calibrate** — run the simulation against historical CSV data; tune win probability and rank movement parameters until banzuke progression looks realistic
2. **Design fictional roster** — create wrestlers using the archetype table above; assign starting ranks, attributes, and stables
3. **Write `seed_database.py`** — inserts the fictional roster into `wrestlers`, `stables`, and an opening `tournaments` row into SQLite
4. **Upgrade `rank_gemini.py`** — add promotion/kadoban rules; accept wrestler list from DB query; write output back to DB
5. **Build game loop** — wire up `matchup_engine.py`, bout outcome simulation, `scoring.py`, and `DynamicBanzukeEngine` into a turn-based loop reading from and writing to `sumo.db`
6. **Archive** — move `Years/`, `output/`, and retired scripts to an `archive/` folder once calibration is complete
