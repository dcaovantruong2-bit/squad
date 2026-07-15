"""Phase definitions — 8 tactical focuses, position similarity, OOP penalty.

Each phase is a tactical moment in a football match.
Any player can fill any slot (no stat gates), but playing out of position
incurs an OOP penalty based on position similarity.
Only restriction: GK can only play GK.
"""

import random
from dataclasses import dataclass

# SlotSpec: a position string ("CB"), list of positions (["LW", "RW"]),
# or a dict with "as" + optional stat/trait requirements
SlotSpec = str | list[str] | dict


# ─── Position Similarity Tiers ──────────────────────────────────────────
# Determines OOP penalty when a player plays outside their natural position.
#   1.0  = natural position (no penalty)
#   0.9  = similar position (small penalty — adjacent roles)
#   0.7  = different position (real penalty — unfamiliar role)
#   0.0  = impossible (GK outfield / outfield GK)
#
# Position adjacency — natural (1.0), adjacent (0.85), different (0.70)
POSITION_ADJACENCY = {
    "GK": {"natural": ["GK"], "adjacent": [], "different": ["CB", "FB", "CDM", "CM", "CAM", "LW", "RW", "ST"]},
    "CB": {"natural": ["CB"], "adjacent": ["FB", "CDM"], "different": ["CM", "CAM", "LW", "RW", "ST"]},
    "FB": {"natural": ["FB"], "adjacent": ["CB", "CDM", "CM", "LW", "RW"], "different": ["CAM", "ST"]},
    "CDM": {"natural": ["CDM"], "adjacent": ["CB", "FB", "CM", "CAM"], "different": ["LW", "RW", "ST"]},
    "CM": {"natural": ["CM"], "adjacent": ["CDM", "CAM", "FB"], "different": ["CB", "LW", "RW", "ST"]},
    "CAM": {"natural": ["CAM"], "adjacent": ["CM", "ST", "LW", "RW"], "different": ["CDM", "CB", "FB"]},
    "LW": {"natural": ["LW"], "adjacent": ["RW", "ST", "CAM", "FB"], "different": ["CM", "CDM", "CB"]},
    "RW": {"natural": ["RW"], "adjacent": ["LW", "ST", "CAM", "FB"], "different": ["CM", "CDM", "CB"]},
    "ST": {"natural": ["ST"], "adjacent": ["LW", "RW", "CAM"], "different": ["CM", "CDM", "CB", "FB"]},
}

# Trait bonuses — reduce OOP penalty by 0.10 per matching slot role
TRAIT_SLOT_FIT = {
    "pacey": ["LW", "RW", "ST", "FB"],
    "clinical": ["LW", "RW", "ST", "CAM"],
    "technical": ["CM", "CAM", "CDM", "CB"],
    "playmaker": ["CM", "CAM", "LW", "RW"],
    "physical": ["ST", "CB", "CDM", "FB", "CM"],
    "destroyer": ["CDM", "CB", "CM"],
    "aerial": ["CB", "ST", "GK"],
    "poacher": ["ST", "LW", "RW"],
    "leader": ["CB", "CM", "GK"],
}


def get_position_penalty(player, field_position: str) -> float:
    """Return OOP penalty multiplier for a player at field_position."""
    player_position = player.position if hasattr(player, 'position') else player
    if player_position == field_position:
        return 1.0
    if player_position == "GK" or field_position == "GK":
        return 0.0
    adj = POSITION_ADJACENCY.get(player_position)
    if not adj:
        return 0.7
    if field_position in adj["natural"]:
        return 1.0
    base = 0.85 if field_position in adj["adjacent"] else 0.70
    bonus = 0.0
    if hasattr(player, 'traits'):
        for t in player.traits:
            fits = TRAIT_SLOT_FIT.get(t)
            if fits and field_position in fits:
                bonus += 0.10
    high_stats = {'GK':'def_', 'DEF':'def_', 'MID':'pas', 'WNG':'pac', 'FWD':'atk'}
    slot_cat = 'MID'
    if field_position == 'GK':
        slot_cat = 'GK'
    elif field_position in ('CB', 'FB', 'CDM'):
        slot_cat = 'DEF'
    elif field_position in ('LW', 'RW'):
        slot_cat = 'WNG'
    elif field_position == 'ST':
        slot_cat = 'FWD'
    key_stat = high_stats.get(slot_cat)
    if key_stat and hasattr(player, key_stat) and getattr(player, key_stat, 0) >= 9:
        bonus += 0.05
    return min(base + bonus, 0.95)


def get_position_penalty_label(player_position: str, field_position: str) -> str:
    """Return a short label describing the OOP penalty."""
    pm = get_position_penalty(player_position, field_position)
    if pm >= 1.0:
        return "natural"
    elif pm >= 0.9:
        return "similar"
    elif pm >= 0.1:
        return "OOP"
    else:
        return "BLOCKED"


# ─── Phase Definition ───────────────────────────────────────────────────

@dataclass
class Phase:
    """A phase of play in a football match."""
    id: str
    name: str
    slots: list[SlotSpec]  # Positions needed
    weight: str            # Primary stat: DEF, PAS, PAC, ATK, SPC
    max_cards: int         # How many cards from hand to field
    description: str


def is_player_eligible(player, slot_spec: SlotSpec) -> bool:
    """Check if a player can fill a slot.
    
    Rules:
    - Only GK is position-locked: GK can only play GK, non-GK can't play GK
    - All outfield players can play any outfield position (OOP penalty applies)
    - Dict specs with stat requirements still work if present
    """
    # Determine the field position for this slot
    if isinstance(slot_spec, str):
        field_pos = slot_spec
    elif isinstance(slot_spec, list):
        # Multi-position slot — any of these, anyone can fill
        return player.position != "GK"
    elif isinstance(slot_spec, dict):
        field_pos = slot_spec.get("as", "CB")
    else:
        return True
    
    # GK can only play GK
    if field_pos == "GK":
        return player.position == "GK"
    # Non-GK can't play GK
    if player.position == "GK" and field_pos != "GK":
        return False
    
    # For dict specs with stat thresholds, check them too
    if isinstance(slot_spec, dict):
        for stat_key, attr in [
            ("min_atk", "atk"),
            ("min_pac", "pac"),
            ("min_pas", "pas"),
            ("min_def", "def_"),
            ("min_spc", "spc"),
        ]:
            if stat_key in slot_spec and getattr(player, attr, 0) < slot_spec[stat_key]:
                return False
        if "trait" in slot_spec and slot_spec["trait"] not in player.traits:
            return False
    
    return True


def slot_positions(slot: SlotSpec) -> list[str]:
    """Return the position(s) a player will play on the field for this slot.
    
    For str specs: [slot]
    For list specs: the list itself (player picks the position)
    For dict specs: ["as"] — everyone plays this position
    """
    if isinstance(slot, str):
        return [slot]
    if isinstance(slot, dict):
        return [slot["as"]]
    return list(slot)


def slot_label(slot: SlotSpec) -> str:
    """Human-readable label for a slot shown in the UI."""
    if isinstance(slot, str):
        return slot
    if isinstance(slot, dict):
        pos = slot["as"]
        parts = []
        for stat_key, label in [
            ("min_atk", "ATK≥"),
            ("min_pac", "PAC≥"),
            ("min_pas", "PAS≥"),
            ("min_def", "DEF≥"),
            ("min_spc", "SPC≥"),
        ]:
            if stat_key in slot:
                parts.append(f"{label}{slot[stat_key]}")
        if "trait" in slot:
            parts.append(slot["trait"])
        if parts:
            return f"→{pos} [{', '.join(parts)}]"
        return f"→{pos}"
    return "/".join(slot)


# ─── The 8 Phases ──────────────────────────────────────────────────────
# All phases always available. Player picks 3 per round.
# Clean, position-based slots with no stat gates.

PHASE_DEFS = {
    "goal_kick": Phase(
        id="goal_kick",
        name="Goal Kick",
        slots=["GK", "CB", "CB"],
        weight="DEF",
        max_cards=3,
        description="Keeper launches long — defenders win the header",
    ),
    "build_up": Phase(
        id="build_up",
        name="Build-Up",
        slots=["FB", "FB", "CM"],
        weight="PAS",
        max_cards=3,
        description="Play out from the back — fullbacks push up, midfield controls tempo",
    ),
    "wide_attack": Phase(
        id="wide_attack",
        name="Wide Attack",
        slots=["FB", "LW", "RW"],
        weight="PAC",
        max_cards=3,
        description="Overload the flanks — pacey wingers stretch the defence",
    ),
    "direct_play": Phase(
        id="direct_play",
        name="Direct Play",
        slots=[["LW", "RW"], "ST", "CM"],
        weight="ATK",
        max_cards=3,
        description="Quick transition — bypass midfield, hit the attackers",
    ),
    "defensive_block": Phase(
        id="defensive_block",
        name="Defensive Block",
        slots=["CB", "CB", "CDM"],
        weight="DEF",
        max_cards=3,
        description="Compact defensive shape — tough to break down",
    ),
    "tiki_taka": Phase(
        id="tiki_taka",
        name="Tiki-Taka",
        slots=["CM", "CM", "CAM"],
        weight="PAS",
        max_cards=3,
        description="Pass, move, repeat — creative midfielders control the game",
    ),
    "counter": Phase(
        id="counter",
        name="Counter",
        slots=["LW", "ST", "RW"],
        weight="PAC",
        max_cards=3,
        description="Explosive break — pacey attackers in behind",
    ),
    "set_piece": Phase(
        id="set_piece",
        name="Set Piece",
        slots=["CAM", "CB", "ST"],
        weight="SPC",
        max_cards=3,
        description="Dead ball specialist meets aerial threat — CAM, CB, ST",
    ),
}


def get_all_phases() -> list[Phase]:
    """Return all 8 phase definitions."""
    return list(PHASE_DEFS.values())


def shuffle_phases() -> list[Phase]:
    """Return all 8 phases in random order."""
    phases = get_all_phases()
    random.shuffle(phases)
    return phases


def deal_phases() -> list[Phase]:
    """Return all 8 phases — no dealing, all always available."""
    phases = get_all_phases()
    random.shuffle(phases)
    return phases
