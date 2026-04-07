# Proposal: Rank + Record Point System

## Concept

The official banzuke is essentially driven by two things: where you are now, and how you did last tournament. This proposal formalizes that into a simple numeric score:

```
score = rank_points + record_points
```

Sort all wrestlers by score descending → that's the predicted ranking.

---

## Division Overview

Professional sumo has six divisions, ranked highest to lowest. Each has different sizes, bout counts, and promotion rules:

| Division   | Size        | Bouts/Tournament | Salaried | Notes |
|------------|-------------|-------------------|----------|-------|
| Makuuchi   | 42 (fixed)  | 15                | Yes      | Top division; contains san'yaku (Y/O/S/K) + maegashira |
| Jūryō      | 28 (fixed)  | 15                | Yes      | Second division; together with makuuchi = *sekitori* |
| Makushita  | 120 (fixed) | 7                 | No       | Third division; most heavily contested |
| Sandanme   | 160 (fixed) | 7                 | No       | Fourth division |
| Jonidan    | ~200–250    | 7                 | No       | Fifth division; variable size, usually largest |
| Jonokuchi  | ~40–90      | 7                 | No       | Lowest division; entry point for new wrestlers |

Key structural facts:
- **Sekitori** (makuuchi + jūryō) fight 15 bouts and receive a salary.
- **Lower divisions** (makushita through jonokuchi) fight only 7 bouts and receive a small allowance.
- The **baseline winning record** differs: 8-7 for 15-bout divisions, 4-3 for 7-bout divisions.
- **East/West** subdivisions exist at every rank; East is slightly more prestigious.

---

## Rank Points

### Makuuchi (42 wrestlers, 15 bouts)

| Rank | Points |
|------|--------|
| Y    | 60000  |
| O    | 55000  |
| S    | 50000  |
| K    | 45000  |
| M1   | 40000  |
| M2   | 39000  |
| M3   | 38000  |
| M4   | 37000  |
| M5   | 36000  |
| M6   | 35000  |
| M7   | 34000  |
| M8   | 33000  |
| M9   | 32000  |
| M10  | 31000  |
| M11  | 30000  |
| M12  | 29000  |
| M13  | 28000  |
| M14  | 27000  |
| M15  | 26000  |
| M16  | 25000  |
| M17  | 24000  |

The gaps between sanyaku ranks (Y/O/S/K) are wider (5000) than between maegashira positions (1000), reflecting how much harder it is to break into — and fall out of — those ranks.

### Jūryō (28 wrestlers, 15 bouts)

Jūryō ranks continue the scale downward from makuuchi. The gap between M17 and J1 is slightly wider than between consecutive maegashira to reflect the division boundary.

| Rank | Points |
|------|--------|
| J1   | 22000  |
| J2   | 21000  |
| J3   | 20000  |
| J4   | 19000  |
| J5   | 18000  |
| J6   | 17000  |
| J7   | 16000  |
| J8   | 15000  |
| J9   | 14000  |
| J10  | 13000  |
| J11  | 12000  |
| J12  | 11000  |
| J13  | 10000  |
| J14  | 9000   |

The 2000-point gap between M17 (24000) and J1 (22000) reflects the meaningful division boundary while keeping the scale continuous.

### Makushita (120 wrestlers, 7 bouts)

The jump from jūryō to makushita is the biggest lifestyle change in sumo — from salaried professional to unpaid trainee. The point gap should reflect this.

| Rank  | Points |
|-------|--------|
| Ms1   | 6000   |
| Ms2   | 5950   |
| Ms3   | 5900   |
| ...   | ...    |
| Ms60  | 3050   |

**Formula:** `rank_points = 6000 - (rank_number - 1) * 50`

The 3000-point gap between J14 (9000) and Ms1 (6000) reflects the enormous sekitori boundary. Within makushita the spacing is tight (50/rank) because there are 120 slots covering a narrow skill band.

### Sandanme (160 wrestlers, 7 bouts)

| Rank  | Points |
|-------|--------|
| Sd1   | 2800   |
| Sd2   | 2775   |
| ...   | ...    |
| Sd80  | 825    |

**Formula:** `rank_points = 2800 - (rank_number - 1) * 25`

### Jonidan (~200–250 wrestlers, 7 bouts)

Jonidan has a variable number of wrestlers. Use the actual count for the tournament.

| Rank  | Points |
|-------|--------|
| Jd1   | 600    |
| Jd2   | 597    |
| ...   | ...    |
| Jd125 | 228    |

**Formula:** `rank_points = 600 - (rank_number - 1) * 3`

### Jonokuchi (~40–90 wrestlers, 7 bouts)

| Rank  | Points |
|-------|--------|
| Jk1   | 180    |
| Jk2   | 176    |
| ...   | ...    |
| Jk45  | 4      |

**Formula:** `rank_points = 180 - (rank_number - 1) * 4`

### Full Scale Summary

| Division boundary       | Top rank pts | Bottom rank pts | Gap to next div |
|--------------------------|-------------|-----------------|-----------------|
| Makuuchi (Y → M17)      | 60000       | 24000           | 2000 to J1      |
| Jūryō (J1 → J14)        | 22000       | 9000            | 3000 to Ms1     |
| Makushita (Ms1 → Ms60)  | 6000        | 3050            | 250 to Sd1      |
| Sandanme (Sd1 → Sd80)   | 2800        | 825             | 225 to Jd1      |
| Jonidan (Jd1 → Jd125)   | 600         | 228             | 48 to Jk1       |
| Jonokuchi (Jk1 → Jk45)  | 180         | 4               | —               |

---

## Record Points

The record bonus/penalty is relative to the "hold rank" baseline: 8 wins for 15-bout divisions, 4 wins for 7-bout divisions.

### 15-bout divisions (Makuuchi, Jūryō)

```
record_points = (wins - 8) * points_per_win
```

- `points_per_win` = **2000**
  - 12-3-0 → +8000 points
  - 10-5-0 → +4000 points
  - 8-7-0 → 0 points
  - 7-8-0 → -2000 points
  - 5-10-0 → -6000 points
  - 0-0-15 → -16000 points (full absence is punishing)

### 7-bout divisions (Makushita, Sandanme, Jonidan, Jonokuchi)

```
record_points = (wins - 4) * points_per_win_lower
```

- `points_per_win_lower` = **500** (tunable)
  - 7-0 → +1500 points
  - 5-2 → +500 points
  - 4-3 → 0 points (kachi-koshi baseline)
  - 3-4 → -500 points
  - 0-0-7 → -2000 points

The lower `points_per_win` reflects the narrower rank-point spacing in these divisions. A 7-0 record in makushita (+1500) can vault a wrestler ~30 ranks, which matches observed banzuke moves.

---

## Worked Examples

### Makuuchi / Jūryō

| Wrestler | Rank | Record | Rank Pts | Record Pts | Total |
|----------|------|--------|----------|------------|-------|
| M1       | M1   | 5-10-0 | 40000    | -6000      | **34000** |
| M4       | M4   | 12-3-0 | 37000    | +8000      | **45000** |
| Yokozuna | Y    | 8-7-0  | 60000    | 0          | **60000** |
| M15      | M15  | 13-2-0 | 26000    | +10000     | **36000** |
| Ozeki    | O    | 5-10-0 | 55000    | -6000      | **49000** |
| J3       | J3   | 12-3-0 | 20000    | +8000      | **28000** |
| J14      | J14  | 3-12-0 | 9000     | -10000     | **-1000** |

As intended: M4 at 12-3 (45000) scores well above M1 at 5-10 (34000). An M15 with a dominant 13-2 lands around M3–M4 territory. A J3 at 12-3 (28000) reaches low maegashira range. A J14 at 3-12 drops into makushita territory.

### Makushita

| Wrestler | Rank | Record | Rank Pts | Record Pts | Total |
|----------|------|--------|----------|------------|-------|
| Ms1      | Ms1  | 7-0    | 6000     | +1500      | **7500** |
| Ms1      | Ms1  | 4-3    | 6000     | 0          | **6000** |
| Ms15     | Ms15 | 7-0    | 5300     | +1500      | **6800** |
| Ms60     | Ms60 | 7-0    | 3050     | +1500      | **4550** |

Ms1 with a perfect 7-0 (7500) reaches J14 territory (9000) — close but may need a bonus bout win to clinch promotion. Ms15 at 7-0 (6800) jumps to ~Ms1 range. This matches real banzuke behavior.

### Lower Divisions

| Wrestler | Rank | Record | Rank Pts | Record Pts | Total |
|----------|------|--------|----------|------------|-------|
| Sd1      | Sd1  | 7-0    | 2800     | +1500      | **4300** |
| Jd1      | Jd1  | 7-0    | 600      | +1500      | **2100** |
| Jk1      | Jk1  | 7-0    | 180      | +1500      | **1680** |

A perfect Sd1 (4300) reaches mid-makushita. A perfect Jd1 (2100) reaches lower sandanme. This matches typical 7-0 promotion jumps across divisions.

---

## Yokozuna and Ozeki Promotion/Demotion Rules

The score system handles S, K, and maegashira ranks well, but Yokozuna and Ozeki follow special rules that override pure score sorting. These must be applied as a separate layer **after** computing scores.

### Yokozuna Promotion

A wrestler can only be promoted to Yokozuna from Ozeki. The de facto standard:

- **Two consecutive tournament championships as Ozeki**, OR
- **Equivalent performance:** at least one championship and one runner-up across the last three tournaments, with **no record below 12 wins** in any of the three.

Yokozuna is a permanent rank — there is no demotion. A Yokozuna who performs poorly is expected to retire.

**Algorithm rule:** After score sorting, check if any current Ozeki meets the promotion criteria using their last 2–3 tournament records. If so, elevate them to Y regardless of score.

### Ozeki Promotion

A wrestler is typically promoted to Ozeki from Sekiwake or Komusubi. The standard:

- **33+ wins over the last 3 tournaments** while ranked san'yaku (S or K), including **10+ wins as Sekiwake in the most recent tournament**.
- Starting from Maegashira is possible but requires a higher bar (e.g., 34+ wins or a championship).

**Algorithm rule:** After score sorting, check if any S/K wrestler meets the 33-win threshold over 3 tournaments. If so, place them at O regardless of score.

### Ozeki Demotion (Kadoban System)

Ozeki demotion is a **two-step process**, not an immediate drop:

1. An Ozeki with a losing record (make-koshi, 7-8 or worse) becomes **kadoban**.
2. If kadoban and they get a winning record (8-7+) next tournament → restored to regular Ozeki.
3. If kadoban and they get another losing record → demoted to **Sekiwake** (never lower, regardless of how bad the record is).
4. If they win **10+ bouts** in that Sekiwake tournament → immediately restored to Ozeki.
5. If they fail to win 10+ at Sekiwake, they must earn promotion the normal way (33 wins over 3 tournaments).

**Algorithm rule:** Track a `kadoban` flag per Ozeki. An Ozeki's score should never place them below S, and their demotion path must follow the two-step procedure above rather than raw score sorting.

### Yokozuna Stability

Yokozuna cannot be demoted. Even with a 0-0-15 absence, they remain Y. In practice they retire rather than perform poorly, but the algorithm must keep them at Y until they are removed from the dataset.

**Algorithm rule:** All current Yokozuna are pinned at Y. Their score is informational only and does not affect their rank placement.

---

## Jūryō / Makushita Promotion Boundary (The Sekitori Line)

This is the most consequential boundary in sumo. Special rules apply:

- **Makushita top 30 with 7-0:** Unconditional promotion to jūryō.
- **Makushita below top 30 with 7-0:** Promoted into the top 30; a second consecutive 7-0 promotes to jūryō.
- **Bonus bouts:** Top makushita wrestlers may get an 8th bout against a jūryō wrestler near the end of the tournament. A loss is ignored; a win counts — a true bonus for the makushita wrestler.
- **Jūryō promotions are announced early** (days after the tournament) because of the salary/lifestyle implications.

**Algorithm rule:** When a makushita wrestler's score exceeds the lowest jūryō score, flag them for promotion. Apply the 7-0-in-top-30 rule as an override: any Ms1–Ms30 wrestler with a perfect record is promoted regardless of score comparison.

---

## Cross-Division Promotion Rules (Lower Divisions)

### Makushita ↔ Sandanme

Standard promotion/demotion based on record. No special rules beyond score sorting.

### Sandanme ↔ Jonidan

Standard promotion/demotion based on record. No special rules.

### Jonidan ↔ Jonokuchi

- **Jonokuchi is the only division where wrestlers can be promoted with a losing record.** This is especially common in May tournaments when a flood of new recruits from maezumō enters, pushing even 3-4 wrestlers up to jonidan.
- New wrestlers enter jonokuchi based on their **maezumō** (pre-tournament) performance.

**Algorithm rule:** In jonokuchi, do not strictly enforce make-koshi = demotion. If the division is overflowing (especially May), allow upward movement even with losing records.

### Variable Division Sizes

Jonidan and jonokuchi have variable sizes. The algorithm must:
1. Use the actual wrestler count for the current tournament.
2. Dynamically compute rank_points based on the formulas above.
3. Handle new entrants who have no prior score (assign them to the bottom of jonokuchi).

---

## Handling Edge Cases

- **Full absence (0-0-15 or 0-0-7):** Treated as 0 wins. 15-bout: record_points = -16000. 7-bout: record_points = -2000. Big drops, matching reality. Exceptions: Yokozuna stay at Y; Ozeki follow kadoban rules.
- **Partial absence (e.g., 2-4-9):** Use only actual wins → record_points = (2 - 8) * 2000 = -12000 for 15-bout. For 7-bout: (2 - 4) * 500 = -1000.
- **Not ranked (empty rank):** Wrestler is not in the division and gets no score. If they appear in a later tournament, they enter with whatever rank they're given.
- **Maezumō entrants:** New wrestlers enter at the bottom of jonokuchi. Their first score is computed after their first ranked tournament.
- **Retirement:** Remove wrestler from scoring. No special handling needed.

---

## What to Tune

| Parameter | Description | Starting Value |
|-----------|-------------|----------------|
| Sanyaku point gaps | Spacing between Y/O/S/K | 5000 per tier |
| Maegashira point gap | Spacing between each M rank | 1000 per rank |
| Makuuchi→Jūryō gap | Gap between M17 and J1 | 2000 |
| Jūryō rank gap | Spacing between each J rank | 1000 per rank |
| Jūryō→Makushita gap | Gap between J14 and Ms1 | 3000 |
| Makushita rank gap | Spacing between each Ms rank | 50 per rank |
| Sandanme rank gap | Spacing between each Sd rank | 25 per rank |
| Jonidan rank gap | Spacing between each Jd rank | 3 per rank |
| Jonokuchi rank gap | Spacing between each Jk rank | 4 per rank |
| `points_per_win` (15-bout) | How much each win above/below 8 matters | 2000 |
| `points_per_win_lower` (7-bout) | How much each win above/below 4 matters | 500 |

These can be optimized by comparing predicted rankings against the actual next-tournament banzuke across the full 1992–2025 dataset.

---

## Implementation Steps

1. Build a rank parser that handles all six divisions: `"M4"` → 37, `"J3"` → 20, `"Ms15"` → 5.30, etc.
2. Build a record parser: `"12-3-0"` → wins=12, `"5-2"` → wins=5.
3. Detect bout count from division (15 for makuuchi/jūryō, 7 for all others).
4. Compute scores for all wrestlers after each tournament.
5. **Apply special rules as a post-processing layer:**
   - Pin all Yokozuna at Y.
   - Check Ozeki promotion criteria (33 wins / 3 tournaments from S/K).
   - Check Yokozuna promotion criteria (2 consecutive championships or equivalent from O).
   - Apply kadoban tracking for Ozeki with losing records.
   - Clamp demoted Ozeki to Sekiwake (never lower).
   - Apply makushita 7-0-in-top-30 auto-promotion to jūryō.
   - Handle jonokuchi losing-record promotions (May tournament overflow).
6. Sort remaining wrestlers within each division by score.
7. For each consecutive pair of tournaments, compare predicted ranking against the actual banzuke for tournament N+1.
8. Measure accuracy (e.g., average rank-position error) per division.
9. Tune the point tables and `points_per_win` values to minimize error.
