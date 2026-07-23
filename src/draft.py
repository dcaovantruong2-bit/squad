"""Flexible formation-first drafting system.

At the start of a run, the player drafts their squad:
  1. Pick 1 GK from ALL goalkeepers
  2. Pick 4 Defenders (CB + FB) from ALL defenders — any mix!
  3. Pick 3 Midfielders (CM/CDM/CAM) from ALL midfielders
  4. Pick 2 Attackers (ST/LW/RW) from ALL attackers

Total: 10 players. The defender round gives complete flexibility —
build a back 4, back 3, or back 5 from any combination of CBs and FBs.
"""

import random
from dataclasses import dataclass, field
from src.cards import PlayerCard


# Map player positions to draft position groups
POSITION_GROUPS = {
    "GK": "GK",
    "CB": "DEF", "FB": "DEF",
    "CM": "MID", "CDM": "MID", "CAM": "MID",
    "ST": "ATK", "LW": "ATK", "RW": "ATK",
}

# Draft order: group → count → label
DRAFT_ROUNDS = [
    {"group": "GK",  "count": 1, "label": "Pick your Goalkeeper (1)"},
    {"group": "DEF", "count": 4, "label": "Pick 4 Defenders — any mix of CBs & FBs"},
    {"group": "MID", "count": 3, "label": "Pick 3 Midfielders"},
    {"group": "ATK", "count": 2, "label": "Pick 2 Attackers"},
]


@dataclass
class DraftPick:
    """A single drafting decision: pick `count` player(s) from `pool`."""
    group: str              # "GK", "DEF", "MID", "ATK"
    count: int              # how many to pick
    pool: list[PlayerCard]  # ALL available players in this group
    label: str              # "Pick 4 Defenders — any mix of CBs & FBs"

    @property
    def can_pick_multiple(self) -> bool:
        return self.count > 1

    def select(self, player: PlayerCard) -> bool:
        """Remove a player from the pool (for multi-pick rounds)."""
        if player in self.pool:
            self.pool.remove(player)
            return True
        return False


@dataclass
class DraftState:
    """Tracks drafting progress across multiple picks."""
    picks: list[DraftPick] = field(default_factory=list)
    selected: list[PlayerCard] = field(default_factory=list)
    current_pick_idx: int = 0

    @property
    def current_pick(self) -> DraftPick | None:
        if 0 <= self.current_pick_idx < len(self.picks):
            return self.picks[self.current_pick_idx]
        return None

    @property
    def is_complete(self) -> bool:
        return self.current_pick_idx >= len(self.picks)

    @property
    def progress_pct(self) -> float:
        if not self.picks:
            return 100.0
        return (self.current_pick_idx / len(self.picks)) * 100

    def confirm_pick(self, chosen: list[PlayerCard]) -> bool:
        """Confirm the current pick with chosen players. Advances to next pick."""
        pick = self.current_pick
        if not pick:
            return True
        if len(chosen) != pick.count:
            return False
        pool_ids = {p.id for p in pick.pool}
        for p in chosen:
            if p.id not in pool_ids:
                return False
        self.selected.extend(chosen)
        self.current_pick_idx += 1
        return self.is_complete

    def get_selected_ids(self) -> list[str]:
        return [p.id for p in self.selected]

    def get_squad_summary(self) -> str:
        lines = [f"Squad ({len(self.selected)} players):"]
        by_pos = {}
        for p in self.selected:
            by_pos.setdefault(p.position, []).append(p.name)
        for pos in sorted(by_pos.keys()):
            names = ", ".join(by_pos[pos])
            lines.append(f"  {pos}: {names}")
        trait_counts = {}
        for p in self.selected:
            for t in p.traits:
                trait_counts[t] = trait_counts.get(t, 0) + 1
        lines.append("\nTrait synergy potential:")
        for trait, count in sorted(trait_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {trait}: {count}")
        return "\n".join(lines)


def generate_draft(
    players: list[PlayerCard],
    seed: int | None = None,
) -> DraftState:
    """Generate a draft sequence showing ALL players in each group.

    Draft flow: GK → DEF (CB+FB) → MID → ATK.
    All players in each group are shown (no subsetting).
    """
    if seed is not None:
        random.seed(seed)

    # Group players by draft group
    groups = {"GK": [], "DEF": [], "MID": [], "ATK": []}
    for p in players:
        group = POSITION_GROUPS.get(p.position)
        if group:
            groups[group].append(p)

    # Shuffle each group for variety in display order
    for g in groups:
        random.shuffle(groups[g])

    # Build draft picks — show ALL players in each group
    picks = []
    for round_def in DRAFT_ROUNDS:
        group = round_def["group"]
        count = round_def["count"]
        label = round_def["label"]
        pool = groups[group]

        if not pool:
            continue

        picks.append(DraftPick(
            group=group,
            count=count,
            pool=list(pool),
            label=label,
        ))

    if seed is not None:
        random.seed()

    return DraftState(picks=picks)


def generate_reward_cards(
    available_players: list[PlayerCard],
    count: int = 3,
    include_synergies: bool = False,
    seed: int | None = None,
) -> list[dict]:
    """Generate post-match reward card options."""
    if seed is not None:
        random.seed(seed)

    rewards = []
    if not available_players:
        return [
            {"type": "shop", "card": {"item": "morale_boost", "name": "Morale Boost", "desc": "+5 morale", "cost": 0}},
            {"type": "shop", "card": {"item": "energy_drink", "name": "Energy Drink", "desc": "Restore one player's energy", "cost": 0}},
            {"type": "shop", "card": {"item": "tactical_shift", "name": "Tactical Shift", "desc": "+5 add_mult next round", "cost": 0}},
        ][:count]

    shuffled = list(available_players)
    random.shuffle(shuffled)
    player_count = min(count, len(shuffled))
    for i in range(player_count):
        rewards.append({"type": "player", "card": shuffled[i]})

    if include_synergies and len(rewards) < count:
        shop_items = [
            {"type": "shop", "card": {"item": "energy_drink", "name": "Energy Drink", "desc": "Restore one player's energy", "cost": 0}},
            {"type": "shop", "card": {"item": "morale_boost", "name": "Morale Boost", "desc": "+5 morale", "cost": 0}},
            {"type": "shop", "card": {"item": "tactical_shift", "name": "Tactical Shift", "desc": "+5 add_mult next round", "cost": 0}},
        ]
        random.shuffle(shop_items)
        while len(rewards) < count:
            rewards.append(shop_items.pop())

    if seed is not None:
        random.seed()

    return rewards[:count]
