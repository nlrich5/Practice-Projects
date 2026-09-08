# ESPN Fantasy Football with Python

A guide to pulling fantasy football data from ESPN using the `espn_api` library.

## Installation

```bash
pip install espn_api
```

## Authentication

ESPN requires two cookies from your browser session for private leagues. To get them:

1. Log into [ESPN Fantasy Football](https://fantasy.espn.com)
2. Open browser DevTools (F12) → Application → Cookies
3. Find and copy the values for `espn_s2` and `SWID`

```python
from espn_api.football import League

league = League(
    league_id=12345,   # found in your league's URL
    year=2026,
    espn_s2='your_espn_s2_cookie',
    swid='your_swid_cookie'
)
```

> **Public leagues** don't require `espn_s2` or `swid`.

---

## Team Information

```python
for team in league.teams:
    print(team.team_name)
    print(team.owner)
    print(team.wins, team.losses)
    print(team.points_for, team.points_against)
    print(team.standing)       # current standings position
    print(team.roster)         # list of Player objects on this team
```

### Standings

```python
standings = league.standings()
for i, team in enumerate(standings, 1):
    print(f"{i}. {team.team_name} — {team.wins}W {team.losses}L")
```

---

## Player Information

Players are accessed through team rosters or the free agent pool.

### Rostered Players

```python
for team in league.teams:
    print(f"\n{team.team_name}")
    for player in team.roster:
        print(f"  {player.name} ({player.position}) — {player.nfl_team}")
        print(f"    Total points: {player.total_points}")
        print(f"    Projected:    {player.projected_total_points}")
        print(f"    % Owned:      {player.percent_owned}")
        print(f"    Injured:      {player.injured}")
```

### Free Agents

```python
# Fetch top 50 free agent RBs
free_agents = league.free_agents(size=50, position='RB')

for player in free_agents:
    print(f"{player.name} — {player.total_points} pts, {player.percent_owned}% owned")
```

Supported `position` values: `QB`, `RB`, `WR`, `TE`, `K`, `D/ST`

---

## Weekly Matchups & Box Scores

```python
week = 1
box_scores = league.box_scores(week=week)

for match in box_scores:
    print(f"{match.home_team.team_name} {match.home_score} vs "
          f"{match.away_score} {match.away_team.team_name}")
```

### Player Scores for a Matchup

```python
for match in box_scores:
    print(f"\n{match.home_team.team_name} lineup:")
    for player in match.home_lineup:
        print(f"  {player.name} ({player.slot_position}) — {player.points} pts")
```

`slot_position` reflects where the player was started (e.g. `QB`, `FLEX`, `BE` for bench).

---

## Scores by Week

```python
# Get a team's score for every completed week
team = league.teams[0]
for week_num, score in enumerate(team.scores, 1):
    print(f"Week {week_num}: {score}")
```

---

## Useful Attributes Reference

### League
| Attribute | Description |
|---|---|
| `league.teams` | All teams in the league |
| `league.standings()` | Teams sorted by standing |
| `league.free_agents(size, position)` | Available free agents |
| `league.box_scores(week)` | Matchup + lineup data for a week |
| `league.current_week` | Current week number |
| `league.settings` | League settings (scoring, roster slots, etc.) |

### Team
| Attribute | Description |
|---|---|
| `team.team_name` | Team name |
| `team.owner` | Owner name |
| `team.wins` / `team.losses` | Season record |
| `team.points_for` / `team.points_against` | Season totals |
| `team.roster` | List of `Player` objects |
| `team.scores` | List of weekly scores |
| `team.schedule` | List of opponent teams by week |

### Player
| Attribute | Description |
|---|---|
| `player.name` | Full name |
| `player.position` | NFL position (QB, RB, etc.) |
| `player.nfl_team` | NFL team abbreviation |
| `player.total_points` | Season total fantasy points |
| `player.projected_total_points` | Projected season total |
| `player.percent_owned` | % of leagues that own them |
| `player.injured` | Boolean injury status |
| `player.stats` | Dict of weekly stats |

---

## Going Further

If you need broader NFL player data beyond your league (historical stats, all players, advanced metrics), consider pairing `espn_api` with:

- [`nfl_data_py`](https://github.com/nflverse/nfl_data_py) — play-by-play and player stats
- [`pro_football_reference_web_scraper`](https://github.com/mjk2244/pro-football-reference-web-scraper) — historical data from PFR
