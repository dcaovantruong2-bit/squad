"""Phase definitions — the 6 phases of play each round.

Each phase represents a moment in a football match.
You play a small subset of your squad per phase.
Players who play get fatigued (-30% stats) for subsequent phases.

Slot Specs:
  "CB"              -> Must be a CB (original position-based)
  ["LW", "RW"]      -> Must be LW or RW (original multi-position)
  {"as": "CB", "min_def": 7}  -> Play as CB, need DEF>=7 (stat-based, any position)
  {"as": "ST", "min_atk": 7, "trait": "pacey"}  -> Play as ST, need ATK>=7 AND pacy trait
"""

import random
from dataclasses import dataclass

# SlotSpec: a position string ("CB"), list of positions (["LW", "RW"]),
# or a dict with "as" + optional stat/trait requirements
SlotSpec = str | list[str] | dict


@dataclass
class Phase:
    """A phase of play in a football match."""
    id: str
    name: str
    slots: list[SlotSpec]  # Positions / stat requirements needed
    weight: str            # Primary stat: DEF, PAS, PAC, ATK, SPC
    max_cards: int         # How many cards from hand to field
    description: str


def is_player_eligible(player, slot_spec: SlotSpec) -> bool:
    """Check if a player meets a slot's requirements.

    Str spec "CB": player must be that position (original).
    List spec ["LW", "RW"]: player must be one of those positions (original).
    Dict spec {"as": "CB", "min_def": 7}: stat/trait conditions only.
      The "as" field determines scoring position, NOT eligibility.
    """
    if isinstance(slot_spec, str):
        return player.position == slot_spec
    if isinstance(slot_spec, list):
        return player.position in slot_spec

    # Dict spec — stat/trait based eligibility
    spec = slot_spec
    for stat_key, attr in [
        ("min_atk", "atk"),
        ("min_pac", "pac"),
        ("min_pas", "pas"),
        ("min_def", "def_"),
        ("min_spc", "spc"),
    ]:
        if stat_key in spec and getattr(player, attr, 0) < spec[stat_key]:
            return False
    if "trait" in spec and spec["trait"] not in player.traits:
        return False
    return True


def slot_positions(slot: SlotSpec) -> list[str]:
    """Return the position(s) a player will play on the field for this slot.

    For str specs: [{slot}]
    For list specs: the list itself (player picks the position)
    For dict specs: [{"as"}] — everyone plays this position regardless of
                    their natural position.
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


PHASE_DEFS = {
    "goal_kick": Phase(
        id="goal_kick",
        name="Goal Kick",
        slots=[
            "GK",                             # Must be a GK
            {"as": "CB", "min_def": 7},        # Any player with DEF≥7 plays CB
            {"as": "CB", "min_def": 6},        # Any player with DEF≥6 plays CB
        ],
        weight="DEF",
        max_cards=3,
        description="Keeper launches long — your best defenders win the header",
    ),
    "build_up": Phase(
        id="build_up",
        name="Build-Up",
        slots=[
            {"as": "FB", "min_pas": 6},        # Any passer plays FB
            {"as": "FB", "min_pas": 6},        # Another passer at FB
            {"as": "CM", "min_pas": 7},        # Any good passer plays CM
        ],
        weight="PAS",
        max_cards=3,
        description="Play out from the back — any good passer can step up",
    ),
    "wing_attack": Phase(
        id="wing_attack",
        name="Wing Attack",
        slots=[
            {"as": "FB", "min_pac": 7},        # Any fast player as FB
            {"as": "LW", "min_pac": 7},        # Any pacy player as winger
        ],
        weight="PAC",
        max_cards=2,
        description="Overlap and cross — pace wins, position doesn't matter",
    ),
    "long_ball": Phase(
        id="long_ball",
        name="Long Ball",
        slots=[
            {"as": "CB", "min_def": 6, "min_pac": 5},  # Athletic defender
            {"as": "ST", "min_atk": 6},                  # Any clinical attacker
        ],
        weight="ATK",
        max_cards=2,
        description="Bypass midfield — your best attackers chase it down",
    ),
    "defensive_block": Phase(
        id="defensive_block",
        name="Defensive Block",
        slots=[
            {"as": "CB", "min_def": 8},         # Elite defender (any position)
            {"as": "CB", "min_def": 7},         # Good defender
            {"as": "CDM", "min_def": 6},        # Decent defender
        ],
        weight="DEF",
        max_cards=3,
        description="Park the bus — your toughest players, any position",
    ),
    "tiki_taka": Phase(
        id="tiki_taka",
        name="Tiki-Taka",
        slots=[
            {"as": "CM", "min_pas": 8},         # Elite passer
            {"as": "CM", "min_pas": 7},         # Good passer
            {"as": "CM", "min_pas": 6},         # Decent passer
        ],
        weight="PAS",
        max_cards=3,
        description="Pass, pass, pass — best passers control the game",
    ),
    "counter_attack": Phase(
        id="counter_attack",
        name="Counter-Attack",
        slots=[
            {"as": "LW", "min_pac": 7},         # Pacy left winger
            {"as": "ST", "min_atk": 7},          # Clinical finisher
            {"as": "RW", "min_pac": 7},         # Pacy right winger
        ],
        weight="PAC",
        max_cards=3,
        description="Explosive break — pacey wingers stretch the defence for a finisher",
    ),
    "set_piece": Phase(
        id="set_piece",
        name="Set Piece",
        slots=[
            {"as": "CAM", "min_spc": 7},         # Specialist kick taker
            {"as": "ST", "min_atk": 7, "trait": "physical"},  # Big target
            {"as": "CB", "min_def": 7},          # Extra aerial threat
        ],
        weight="SPC",
        max_cards=3,
        description="Corner or free kick — specialist delivery meets a physical target with CB support",
    ),
    "flair_moment": Phase(
        id="flair_moment",
        name="Flair Moment",
        slots=[
            {"as": "CAM", "min_spc": 7},         # Creative spark
            {"as": "ST", "min_atk": 6},           # Finisher
        ],
        weight="SPC",
        max_cards=2,
        description="Individual brilliance — your most creative player makes something from nothing",
    ),
    "second_ball": Phase(
        id="second_ball",
        name="Second Ball",
        slots=[
            {"as": "CM", "min_atk": 6},           # Box-crashing midfielder
            {"as": "ST", "min_atk": 7},           # Target man
        ],
        weight="ATK",
        max_cards=2,
        description="Keeper parries — your midfielder attacks the loose ball before defenders react",
    ),
    "high_press": Phase(
        id="high_press",
        name="High Press",
        slots=[
            {"as": "ST", "min_pac": 7},         # Pace up front
            {"as": "RW", "min_pac": 7},         # Pace on the wing
            {"as": "CM", "min_pac": 6},         # Energetic midfielder
        ],
        weight="PAC",
        max_cards=3,
        description="Suffocate the opponent — all three need pace to press high",
    ),
    "through_ball": Phase(
        id="through_ball",
        name="Through Ball",
        slots=[
            {"as": "CM", "min_pas": 7},         # Visionary passer
            {"as": "ST", "min_pac": 7},         # Quick runner in behind
        ],
        weight="ATK",
        max_cards=2,
        description="One pass unlocks the defence — passer meets pace",
    ),
    "wingback_push": Phase(
        id="wingback_push",
        name="Wingback Push",
        slots=[
            {"as": "FB", "min_pac": 7},         # Overlapping fullback
            {"as": "LW", "min_pas": 6},         # Winger who can combine
        ],
        weight="PAC",
        max_cards=2,
        description="Fullback bombs forward to combine with the winger",
    ),
}


def get_all_phases() -> list[Phase]:
    """Return all phase definitions (13 total)."""
    return list(PHASE_DEFS.values())


def shuffle_phases() -> list[Phase]:
    """Return 6 random phases from the pool (shuffled order) for a round."""
    phases = get_all_phases()
    chosen = random.sample(phases, min(6, len(phases)))
    random.shuffle(chosen)
    return chosen


def deal_phases(hand_size: int = 6) -> list[Phase]:
    """Deal `hand_size` random phase cards (no duplicates) from the 13-phase pool. Player picks which to play."""
    phases = get_all_phases()
    return random.sample(phases, min(hand_size, len(phases)))
