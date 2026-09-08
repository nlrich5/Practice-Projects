import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from matchup_engine import MatchupEngine, Wrestler

CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "matchup_schedule.json")


def make_roster(n=42):
    """Create a roster of n wrestlers with sequential rank positions."""
    return [
        Wrestler(id=i, name=f"Wrestler{i}", wins=0, losses=0,
                 rank_position=i, rank_val=float(43 - i))
        for i in range(1, n + 1)
    ]


def make_roster_with_records(win_pattern: list[int]) -> list[Wrestler]:
    """Create a roster where each wrestler's wins come from win_pattern."""
    return [
        Wrestler(id=i, name=f"Wrestler{i}", wins=win_pattern[i - 1],
                 losses=8 - win_pattern[i - 1], rank_position=i, rank_val=float(43 - i))
        for i in range(1, len(win_pattern) + 1)
    ]


@pytest.fixture
def engine():
    return MatchupEngine(CONFIG)


@pytest.fixture
def roster():
    return make_roster(42)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_full_tournament(engine, roster):
    """Simulate all 15 days and return (all_pairs, past_matchups)."""
    past = set()
    all_pairs = []
    for day in range(1, 16):
        print(f"Day {day}")
        pairs = engine.generate(day, roster, past)
        for a, b in pairs:
            past.add(frozenset({a.id, b.id}))

            # give winner +1 win for record-based stages to have meaningful data
            a.wins += 1
            b.losses += 1

            print(f"  {a.name} (pos={a.rank_position}, {a.wins}-{a.losses}) vs {b.name} (pos={b.rank_position}, {b.wins}-{b.losses})")
        all_pairs.extend(pairs)

    return all_pairs, past


# ---------------------------------------------------------------------------
# Full tournament printout
# ---------------------------------------------------------------------------

def test_print_full_tournament(engine, roster):
    run_full_tournament(engine, roster)


# ---------------------------------------------------------------------------
# Basic sanity
# ---------------------------------------------------------------------------

def test_stage1_day1_returns_pairs(engine, roster):
    pairs = engine.generate(1, roster, set())
    assert len(pairs) > 0


def test_each_wrestler_appears_once_per_day(engine, roster):
    past = set()
    for day in range(1, 16):
        pairs = engine.generate(day, roster, past)
        ids = [w.id for pair in pairs for w in pair]
        assert len(ids) == len(set(ids)), f"Duplicate wrestler on day {day}"
        for a, b in pairs:
            past.add(frozenset({a.id, b.id}))


def test_no_repeat_matchups_full_tournament(engine, roster):
    past = set()
    for day in range(1, 16):
        pairs = engine.generate(day, roster, past)
        for a, b in pairs:
            pair = frozenset({a.id, b.id})
            assert pair not in past, f"Repeat matchup {a.id} vs {b.id} on day {day}"
            past.add(pair)
            a.wins += 1  # advance records so stage 2/3 sorting has meaningful data


def test_stage_routing(engine, roster):
    past = set()
    # Stage 1: days 1-8 should use config schedule (position-based)
    for day in range(1, 9):
        pairs = engine.generate(day, roster, past)
        assert len(pairs) > 0, f"No pairs on stage1 day {day}"
        for a, b in pairs:
            past.add(frozenset({a.id, b.id}))

    # Stage 2: days 9-12
    for day in range(9, 13):
        pairs = engine.generate(day, roster, past)
        assert len(pairs) > 0, f"No pairs on stage2 day {day}"
        for a, b in pairs:
            past.add(frozenset({a.id, b.id}))

    # Stage 3: days 13-15
    for day in range(13, 16):
        pairs = engine.generate(day, roster, past)
        assert len(pairs) > 0, f"No pairs on stage3 day {day}"


# ---------------------------------------------------------------------------
# Stage 1
# ---------------------------------------------------------------------------

def test_stage1_uses_position_schedule(engine, roster):
    pairs = engine.generate(1, roster, set())
    pair_positions = {(min(a.rank_position, b.rank_position),
                       max(a.rank_position, b.rank_position))
                      for a, b in pairs}
    # day1 schedule starts with [1,7]
    assert (1, 7) in pair_positions


def test_stage1_fallback_on_rematch(engine, roster):
    """If a scheduled pair has already fought, a fallback opponent is used."""
    past = {frozenset({1, 7})}  # pre-seed the day1 1v7 matchup as already fought
    pairs = engine.generate(1, roster, past)
    ids_of_1 = [b.id for a, b in pairs if a.id == 1] + \
               [a.id for a, b in pairs if b.id == 1]
    # wrestler 1 should be paired with someone other than 7
    assert ids_of_1 == [] or 7 not in ids_of_1


def test_stage1_all_days_defined(engine, roster):
    """All 8 stage1 days in the config should return pairs without error."""
    past = set()
    for day in range(1, 9):
        pairs = engine.generate(day, roster, past)
        assert len(pairs) > 0, f"Stage 1 day {day} returned no pairs"
        for a, b in pairs:
            past.add(frozenset({a.id, b.id}))


# ---------------------------------------------------------------------------
# Stage 2
# ---------------------------------------------------------------------------

def test_stage2_higher_record_faces_similar_record(engine):
    """Wrestlers with 7 wins should be paired with other high-win wrestlers."""
    wins = [7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0, 0,
            7, 6, 5, 4, 3, 2, 1, 0, 7, 6, 5, 4, 3, 2, 1, 0,
            6, 5, 4, 3, 2, 1, 0, 6, 5, 4]
    roster = make_roster_with_records(wins)
    past = set()
    pairs = engine.generate(9, roster, past)

    # the wrestler with most wins (id=1, 7 wins) should face another high-win wrestler
    top_match = next((a, b) for a, b in pairs if a.id == 1 or b.id == 1)
    opponent = top_match[1] if top_match[0].id == 1 else top_match[0]
    assert opponent.wins >= 5, "Top wrestler matched against low-win opponent in stage 2"


def test_stage2_bucket_count(engine, roster):
    past = set()
    # seed past matchups from stage 1
    for day in range(1, 9):
        pairs = engine.generate(day, roster, past)
        for a, b in pairs:
            past.add(frozenset({a.id, b.id}))

    pairs = engine.generate(9, roster, past)
    assert len(pairs) == 21  # 42 wrestlers / 2


# ---------------------------------------------------------------------------
# Stage 3
# ---------------------------------------------------------------------------

def test_stage3_sorted_by_wins(engine):
    """The best-record wrestler should face the second-best-record wrestler."""
    wins = [8, 8, 7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1,
            8, 7, 6, 5, 4, 3, 2, 1, 8, 7, 6, 5, 4, 3, 2, 1,
            7, 6, 5, 4, 3, 2, 1, 7, 6, 5]
    roster = make_roster_with_records(wins)
    past = set()
    pairs = engine.generate(13, roster, past)

    # wrestler id=1 has 8 wins and rank_position=1 — should face another 8-win wrestler
    top_match = next((a, b) for a, b in pairs if a.id == 1 or b.id == 1)
    opponent = top_match[1] if top_match[0].id == 1 else top_match[0]
    assert opponent.wins == 8, "Top wrestler not facing equal-record opponent in stage 3"


def test_stage3_no_repeats_when_pool_constrained(engine):
    """Stage 3 fallback should not produce a repeat if any unmet opponent exists."""
    small_roster = make_roster(6)
    # pre-seed so wrestler 1 has fought everyone except wrestler 6
    past = {frozenset({1, 2}), frozenset({1, 3}), frozenset({1, 4}), frozenset({1, 5})}
    pairs = engine.generate(13, small_roster, past)
    ids_of_1 = [b.id for a, b in pairs if a.id == 1] + \
               [a.id for a, b in pairs if b.id == 1]
    if ids_of_1:
        assert ids_of_1[0] == 6, "Should match wrestler 1 with only unmet opponent (6)"
