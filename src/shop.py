"""Shop and Morale economy for Squad — the roguelike loop.

Morale is earned between rounds and spent in the shop:
  Win a phase:        +1 Morale
  Win a round:        +3 Morale
  Beat target by 50%: +2 Morale (bonus)
  Win the match:      +5 Morale
  Clean sweep:        +3 Morale (bonus for 3-0)

Shop items persist for one match (run) unless stated otherwise.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class ShopItem:
    """An item that can be bought with Morale between rounds."""
    id: str
    name: str
    cost: int
    description: str
    effect_type: str  # "stat_boost", "fatigue_reset", "chips_buff", "add_mult_buff",
                      # "x_mult_buff", "trait_grant", "formation_swap", "super_sub"
    params: dict = field(default_factory=dict)
    max_per_run: int = 1  # How many times you can buy this per run
    rarity: str = "common"  # common, uncommon, rare


# ─── Shop Item Definitions ──────────────────────────────────────────────

SHOP_ITEMS = [
    ShopItem(
        id="inspired_sub",
        name="Inspired Sub",
        cost=2,
        description="Restore one player's fatigue to 100%",
        effect_type="fatigue_reset",
        max_per_run=2,
        rarity="common",
    ),
    ShopItem(
        id="tactical_upgrade",
        name="Tactical Upgrade",
        cost=3,
        description="+1 to a chosen stat (ATK/PAC/PAS/DEF/SPC) on one player",
        effect_type="stat_boost",
        max_per_run=3,
        rarity="common",
    ),
    ShopItem(
        id="set_piece_drill",
        name="Set Piece Drill",
        cost=4,
        description="Next round: all phases get +40 chips",
        effect_type="chips_buff",
        params={"chips": 40},
        max_per_run=1,
        rarity="uncommon",
    ),
    ShopItem(
        id="super_sub",
        name="Super Sub",
        cost=2,
        description="Next round: fielded player gets ×1.3 if at 100% fatigue",
        effect_type="super_sub",
        max_per_run=2,
        rarity="common",
    ),
    ShopItem(
        id="tactical_shift",
        name="Tactical Shift",
        cost=5,
        description="Next round: +5 add_mult on all phases",
        effect_type="add_mult_buff",
        params={"add_mult": 5},
        max_per_run=1,
        rarity="uncommon",
    ),
    ShopItem(
        id="veterans_wisdom",
        name="Veteran's Wisdom",
        cost=6,
        description="One player gains a random positive trait",
        effect_type="trait_grant",
        max_per_run=1,
        rarity="rare",
    ),
    ShopItem(
        id="formation_tweak",
        name="Formation Tweak",
        cost=3,
        description="Swap to a different formation for the remaining matches",
        effect_type="formation_swap",
        max_per_run=1,
        rarity="common",
    ),
    ShopItem(
        id="momentum_injector",
        name="Momentum Injector",
        cost=4,
        description="Next phase starts at ×1.5 momentum (skips ×1.0)",
        effect_type="momentum_boost",
        params={"momentum": 1.5},
        max_per_run=1,
        rarity="uncommon",
    ),
    ShopItem(
        id="scout_report",
        name="Scout Report",
        cost=2,
        description="See all 6 phase cards before picking 3 (always available)",
        effect_type="scout",
        max_per_run=3,
        rarity="common",
    ),
    ShopItem(
        id="double_session",
        name="Double Training Session",
        cost=4,
        description="All fielded players fatigue penalty reduced: ×0.8 instead of ×0.7",
        effect_type="fatigue_penalty_reduction",
        params={"penalty": 0.8},
        max_per_run=1,
        rarity="uncommon",
    ),
]


# ─── Shop Inventory ─────────────────────────────────────────────────────

def get_shop_inventory(reroll: bool = False, seed: int | None = None) -> list[ShopItem]:
    """Return 4 random items for the shop (always includes some common+uncommon)."""
    import random
    if seed is not None:
        random.seed(seed)

    common = [i for i in SHOP_ITEMS if i.rarity == "common"]
    uncommon = [i for i in SHOP_ITEMS if i.rarity == "uncommon"]
    rare = [i for i in SHOP_ITEMS if i.rarity == "rare"]

    # Always offer: 2 common, 1 uncommon, 1 rare (50% chance)
    selected = random.sample(common, min(2, len(common)))
    selected += random.sample(uncommon, min(1, len(uncommon)))
    if random.random() < 0.5 and rare:
        selected += random.sample(rare, min(1, len(rare)))
    else:
        selected += random.sample(uncommon, min(1, len(uncommon)))

    random.shuffle(selected)
    return selected[:4]


# ─── Morale Tracking ────────────────────────────────────────────────────

def calculate_morale_earnings(
    phases_won: int,
    phases_total: int,
    round_won: bool,
    round_target: int,
    round_score: int,
    match_won: bool = False,
    clean_sweep: bool = False,
) -> dict:
    """Calculate Morale earned after a round.

    Returns dict with breakdown and total.
    """
    earnings = {
        "phase_wins": phases_won if phases_won > 0 else 0,
        "round_win_bonus": 3 if round_won else 0,
        "score_milestone": 2 if round_won and round_score >= round_target * 1.5 else 0,
        "match_win_bonus": 5 if match_won else 0,
        "clean_sweep_bonus": 3 if clean_sweep else 0,
    }
    total = sum(earnings.values())
    earnings["total"] = total
    return earnings


# ─── Active Buffs (applied per round from shop purchases) ───────────────

@dataclass
class ActiveBuffs:
    """Tracks active shop-bought buffs for the current round."""
    extra_chips: int = 0
    extra_add_mult: int = 0
    extra_x_mult: float = 1.0
    fatigue_penalty: float = 0.7  # override for fatigue
    momentum_override: float | None = None  # override for next phase momentum
    super_sub_active: bool = False  # fresh players get ×1.3
    scout_active: bool = False  # always see all 6 phases

    def apply_to_round(self, round_buffs: dict) -> dict:
        """Merge active buffs into a round buffs dict for display."""
        if self.extra_chips:
            round_buffs["extra_chips"] = round_buffs.get("extra_chips", 0) + self.extra_chips
        if self.extra_add_mult:
            round_buffs["extra_add_mult"] = round_buffs.get("extra_add_mult", 0) + self.extra_add_mult
        if self.extra_x_mult != 1.0:
            round_buffs["extra_x_mult"] = round_buffs.get("extra_x_mult", 1.0) * self.extra_x_mult
        return round_buffs


# ─── Apply Shop Item Effects ────────────────────────────────────────────

def apply_shop_item(item: ShopItem, match_state, players, formations=None) -> str:
    """Apply a shop item's effect. Returns a result message string."""
    from src.cards import PlayerCard

    if item.effect_type == "fatigue_reset":
        # Called with a specific player selected
        return "fatigue_reset_pending"  # Need to pick a player

    elif item.effect_type == "stat_boost":
        return "stat_boost_pending"  # Need to pick a player + stat

    elif item.effect_type == "chips_buff":
        chips = item.params.get("chips", 40)
        if not hasattr(match_state, "shop_buffs"):
            match_state.shop_buffs = ActiveBuffs()
        match_state.shop_buffs.extra_chips += chips
        return f"All phases this round get +{chips} chips!"

    elif item.effect_type == "add_mult_buff":
        am = item.params.get("add_mult", 5)
        if not hasattr(match_state, "shop_buffs"):
            match_state.shop_buffs = ActiveBuffs()
        match_state.shop_buffs.extra_add_mult += am
        return f"All phases this round get +{am} add_mult!"

    elif item.effect_type == "super_sub":
        if not hasattr(match_state, "shop_buffs"):
            match_state.shop_buffs = ActiveBuffs()
        match_state.shop_buffs.super_sub_active = True
        return "Fresh players get ×1.3 this round!"

    elif item.effect_type == "trait_grant":
        return "trait_grant_pending"  # Need to pick a player

    elif item.effect_type == "formation_swap":
        return "formation_swap_pending"  # Need to pick a formation

    elif item.effect_type == "momentum_boost":
        mom = item.params.get("momentum", 1.5)
        if not hasattr(match_state, "shop_buffs"):
            match_state.shop_buffs = ActiveBuffs()
        match_state.shop_buffs.momentum_override = mom
        return f"Next phase starts at ×{mom} momentum!"

    elif item.effect_type == "scout":
        if not hasattr(match_state, "shop_buffs"):
            match_state.shop_buffs = ActiveBuffs()
        match_state.shop_buffs.scout_active = True
        return "You'll see all 6 phase cards this round!"

    elif item.effect_type == "fatigue_penalty_reduction":
        penalty = item.params.get("penalty", 0.8)
        if not hasattr(match_state, "shop_buffs"):
            match_state.shop_buffs = ActiveBuffs()
        match_state.shop_buffs.fatigue_penalty = penalty
        return f"Fatigue penalty reduced to ×{penalty} (was ×0.7)!"

    return "Item applied."
