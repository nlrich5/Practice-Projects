from typing import List, Tuple

from wrestler import Wrestler

class DynamicBanzukeEngine:

    @staticmethod
    def format_tier(title_prefix: str, wrestlers: List[Wrestler]) -> List[Tuple[str, Wrestler]]:
        """
        Dynamically assigns East/West pairs (e.g. Ozeki 1 East, Ozeki 1 West, Ozeki 2 East)
        for any arbitrary number of wrestlers in a tier.
        """
        assigned = []
        for index, wrestler in enumerate(wrestlers):
            slot_number = (index // 2) + 1
            side = "East" if (index % 2 == 0) else "West"
            title = f"{title_prefix} {slot_number} {side}"
            assigned.append((title, wrestler))
        return assigned

    def build_banzuke(self, roster: List[Wrestler]) -> List[Tuple[str, Wrestler]]:
        """Ranks and formats a complete Makuuchi Banzuke regardless of Yokozuna/Ozeki counts."""

        # 1. Separate into protected status tiers vs rank-and-file candidates
        yokozuna_tier = [w for w in roster if w.is_yokozuna]
        ozeki_tier = [w for w in roster if w.is_ozeki and not w.is_yokozuna]
        
        # Non-Ozeki/Yokozuna are open to performance-based mobility
        open_candidates = [w for w in roster if not w.is_yokozuna and not w.is_ozeki]

        # 2. Sort each tier internally by target performance / current rank
        yokozuna_tier.sort(key=lambda w: (w.target_val, w.rank_val, -w.wins))
        ozeki_tier.sort(key=lambda w: (w.target_val, w.rank_val, -w.wins))
        open_candidates.sort(key=lambda w: (w.target_val, w.rank_val, -w.wins))

        # 3. Assemble the Banzuke dynamically
        banzuke: List[Tuple[str, Wrestler]] = []

        # Tier 1: Yokozuna (0 to N)
        banzuke.extend(self.format_tier("Yokozuna", yokozuna_tier))

        # Tier 2: Ozeki (0 to N)
        banzuke.extend(self.format_tier("Ozeki", ozeki_tier))

        # Tier 3: Sekiwake (Top 2 remaining open candidates)
        sekiwake_list = open_candidates[:2]
        banzuke.extend(self.format_tier("Sekiwake", sekiwake_list))

        # Tier 4: Komusubi (Next 2 remaining open candidates)
        komusubi_list = open_candidates[2:4]
        banzuke.extend(self.format_tier("Komusubi", komusubi_list))

        # Tier 5: Maegashira (All remaining open candidates)
        maegashira_list = open_candidates[4:]
        banzuke.extend(self.format_tier("Maegashira", maegashira_list))

        # Update each wrestler's underlying numeric rank_val for next cycle
        for index, (_, wrestler) in enumerate(banzuke):
            wrestler.rank_val = 1.0 + (index * 0.5)

        return banzuke


# --- Test Demonstration ---
if __name__ == "__main__":
    engine = DynamicBanzukeEngine()

    # Scenario A: Heavy Sanyaku Top-End (4 Yokozuna, 3 Ozeki)
    heavy_roster = [
        Wrestler("1", "Terunofuji", rank_val=1.0, target_val=1.0, is_yokozuna=True),
        Wrestler("2", "Hakuho II", rank_val=1.5, target_val=1.2, is_yokozuna=True),
        Wrestler("3", "Harumafuji II", rank_val=2.0, target_val=1.5, is_yokozuna=True),
        Wrestler("4", "Kakuryu II", rank_val=2.5, target_val=1.8, is_yokozuna=True),
        Wrestler("5", "Kotozakura", rank_val=3.0, target_val=3.0, is_ozeki=True),
        Wrestler("6", "Hoshoryu", rank_val=3.5, target_val=3.2, is_ozeki=True),
        Wrestler("7", "Onosato", rank_val=4.0, target_val=3.5, is_ozeki=True),
        Wrestler("8", "Wakamotohiro", rank_val=5.0, target_val=4.0),
        Wrestler("9", "Atamifuji", rank_val=5.5, target_val=4.5),
        Wrestler("10", "Abi", rank_val=6.0, target_val=5.0),
        Wrestler("11", "Ura", rank_val=6.5, target_val=5.5),
        Wrestler("12", "Tobizaru", rank_val=7.0, target_val=6.0),
    ]

    print("=== SCENARIO A: 4 Yokozuna, 3 Ozeki ===")
    for title, w in engine.build_banzuke(heavy_roster):
        print(f"{title:<20} | {w.name}")

    # Scenario B: No Yokozuna, 0 Ozeki (Era of complete vacancy)
    vacant_roster = [
        Wrestler("101", "Rookie Star A", rank_val=5.0, target_val=1.0),
        Wrestler("102", "Rookie Star B", rank_val=5.5, target_val=1.5),
        Wrestler("103", "Veteran C", rank_val=6.0, target_val=2.0),
        Wrestler("104", "Veteran D", rank_val=6.5, target_val=2.5),
        Wrestler("105", "Mid-tier E", rank_val=7.0, target_val=3.0),
    ]

    print("\n=== SCENARIO B: 0 Yokozuna, 0 Ozeki ===")
    for title, w in engine.build_banzuke(vacant_roster):
        print(f"{title:<20} | {w.name}")