import json
from typing import Optional

import networkx as nx

from wrestler import Wrestler


class MatchupEngine:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)

    def generate(
        self,
        day: int,
        wrestlers: list[Wrestler],
        past_matchups: set[frozenset],
    ) -> list[tuple[Wrestler, Wrestler]]:
        if day <= 8:
            return self._stage1(day, wrestlers, past_matchups)
        elif day <= 12:
            return self._stage2(wrestlers, past_matchups)
        else:
            return self._stage3(wrestlers, past_matchups)

    # -------------------------------------------------------------------------
    # Stage 1 (days 1-8): position-based schedule from config
    # -------------------------------------------------------------------------

    def _stage1(self, day: int, wrestlers: list[Wrestler], past_matchups: set[frozenset]):
        day_key = f"day{day}"
        schedule = self.config["stage1"].get(day_key)
        if not schedule:
            raise ValueError(f"No stage1 schedule defined for {day_key}")

        position_map = {w.rank_position: w for w in wrestlers}
        pairs = []
        used = set()

        for pos_a, pos_b in schedule:
            wrestler_a = position_map.get(pos_a)
            wrestler_b = position_map.get(pos_b)

            if not wrestler_a or not wrestler_b:
                continue
            if wrestler_a.id in used or wrestler_b.id in used:
                continue
            if frozenset({wrestler_a.id, wrestler_b.id}) in past_matchups:
                # fall back to nearest available unmet opponent by rank proximity
                wrestler_b = next(
                    (w for w in wrestlers
                     if w.id not in used
                     and w.id != wrestler_a.id
                     and frozenset({wrestler_a.id, w.id}) not in past_matchups),
                    None,
                )
                if not wrestler_b:
                    continue

            pairs.append((wrestler_a, wrestler_b))
            used.add(wrestler_a.id)
            used.add(wrestler_b.id)

        return pairs

    # -------------------------------------------------------------------------
    # Stage 2 (days 9-12): weighted rank + record buckets
    # -------------------------------------------------------------------------

    def _stage2(self, wrestlers: list[Wrestler], past_matchups: set[frozenset]):
        cfg = self.config["stage2"]
        rw = cfg["record_weight"]
        kw = cfg["rank_weight"]
        n_buckets = cfg["buckets"]

        def score(w: Wrestler) -> float:
            return (rw * w.wins) + (kw * (len(wrestlers) - w.rank_position))

        sorted_wrestlers = sorted(wrestlers, key=score, reverse=True)
        buckets = self._split_buckets(sorted_wrestlers, n_buckets)
        return self._pair_buckets(buckets, past_matchups, protect_leader=True)

    # -------------------------------------------------------------------------
    # Stage 3 (days 13-15): pure Swiss by record
    # -------------------------------------------------------------------------

    def _stage3(self, wrestlers: list[Wrestler], past_matchups: set[frozenset]):
        sorted_wrestlers = sorted(
            wrestlers,
            key=lambda w: (w.wins, -w.rank_position),
            reverse=True,
        )
        return self._pair_bucket(sorted_wrestlers, past_matchups, protect_leader=False)

    # -------------------------------------------------------------------------
    # Bucket helpers
    # -------------------------------------------------------------------------

    def _split_buckets(self, sorted_wrestlers: list[Wrestler], n: int) -> list[list[Wrestler]]:
        size = len(sorted_wrestlers) // n
        buckets = []
        for i in range(n):
            start = i * size
            end = start + size if i < n - 1 else len(sorted_wrestlers)
            buckets.append(sorted_wrestlers[start:end])
        return buckets

    def _pair_buckets(
        self,
        buckets: list[list[Wrestler]],
        past_matchups: set[frozenset],
        protect_leader: bool,
    ) -> list[tuple[Wrestler, Wrestler]]:
        pairs = []
        floated: Optional[Wrestler] = None

        for i, bucket in enumerate(buckets):
            pool = ([floated] + bucket) if floated else list(bucket)
            floated = None

            if len(pool) % 2 != 0:
                floated = pool[-1]
                pool = pool[:-1]

            is_top_bucket = (i == 0)
            pairs += self._pair_bucket(
                pool,
                past_matchups,
                protect_leader=(protect_leader and is_top_bucket),
            )

        return pairs

    def _pair_bucket(
        self,
        pool: list[Wrestler],
        past_matchups: set[frozenset],
        protect_leader: bool,
    ) -> list[tuple[Wrestler, Wrestler]]:
        if len(pool) < 2:
            return []

        # Build a graph where edges connect valid (unmet) pairs.
        # Edge weight = score similarity (lower = closer) so min_weight_matching
        # produces opponents with the most similar scores.
        G = nx.Graph()
        G.add_nodes_from(w.id for w in pool)

        id_to_wrestler = {w.id: w for w in pool}

        for i, a in enumerate(pool):
            for b in pool[i + 1:]:
                if frozenset({a.id, b.id}) not in past_matchups:
                    score_diff = abs(pool.index(a) - pool.index(b))
                    G.add_edge(a.id, b.id, weight=score_diff)

        if len(G.edges) == 0:
            return []

        matching = nx.min_weight_matching(G)

        pairs = [(id_to_wrestler[a], id_to_wrestler[b]) for a, b in matching]

        # protect_leader: ensure the top two wrestlers don't meet until the
        # matching forces it — swap the top wrestler's opponent if possible
        if protect_leader and len(pairs) >= 2:
            pairs = self._defer_leader_matchup(pairs, pool, past_matchups)

        return pairs

    def _defer_leader_matchup(
        self,
        pairs: list[tuple[Wrestler, Wrestler]],
        pool: list[Wrestler],
        past_matchups: set[frozenset],
    ) -> list[tuple[Wrestler, Wrestler]]:
        """If the top two wrestlers in pool are matched against each other,
        try to swap one of their opponents to delay the marquee matchup."""
        top_ids = {pool[0].id, pool[1].id}
        leader_pair_idx = next(
            (i for i, (a, b) in enumerate(pairs)
             if a.id in top_ids and b.id in top_ids),
            None,
        )
        if leader_pair_idx is None:
            return pairs  # already deferred naturally

        top1, top2 = pairs[leader_pair_idx]

        # find another pair to swap with — both new pairings must be unmet
        for swap_idx, (a, b) in enumerate(pairs):
            if swap_idx == leader_pair_idx:
                continue
            if top1.id in {a.id, b.id} or top2.id in {a.id, b.id}:
                continue
            if (frozenset({top1.id, a.id}) not in past_matchups
                    and frozenset({top2.id, b.id}) not in past_matchups):
                pairs = list(pairs)
                pairs[leader_pair_idx] = (top1, a)
                pairs[swap_idx] = (top2, b)
                return pairs

        return pairs  # couldn't find a valid swap — accept the matchup
