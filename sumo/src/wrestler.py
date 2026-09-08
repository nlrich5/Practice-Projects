from dataclasses import dataclass, field


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
