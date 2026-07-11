"""Formation definitions — tactical shape with global multipliers and position bonuses.

Each formation gives a global multiplier to all phase scores plus optional
position-specific chip bonuses (positive or negative) to create trade-offs.
"""

from src.cards import FormationCard

FORMATIONS = {
    "4-4-2": FormationCard(
        id="4-4-2",
        name="4-4-2",
        slots=["CB", "CB", "FB", "FB", "CM", "CM", "ST", "ST"],
        hand_size=11,
        global_mult=1.0,
        position_bonus={},
        description="Balanced. No frills. Classic.",
    ),
    "4-3-3": FormationCard(
        id="4-3-3",
        name="4-3-3",
        slots=["CB", "CB", "FB", "FB", "CDM", "CM", "CM", "LW", "RW", "ST"],
        hand_size=12,
        global_mult=1.05,
        position_bonus={"LW": 20, "RW": 20, "ST": -15, "CDM": -10},
        description="Attacking. Wingers thrive (+20). ST and CDM stretched (-15/-10). +5% global.",
    ),
    "5-3-2": FormationCard(
        id="5-3-2",
        name="5-3-2",
        slots=["CB", "CB", "CB", "FB", "FB", "CM", "CM", "CDM", "ST", "ST"],
        hand_size=11,
        global_mult=0.95,
        position_bonus={"CB": 25, "FB": 12, "LW": -20, "RW": -20},
        description="Defence wins. CBs+25, FBs+12. Wingers don't exist (-20). -5% global.",
    ),
    "3-4-3": FormationCard(
        id="3-4-3",
        name="3-4-3",
        slots=["CB", "CB", "FB", "FB", "CM", "CM", "LW", "RW", "ST", "ST"],
        hand_size=12,
        global_mult=1.08,
        position_bonus={"ST": 20, "LW": 15, "RW": 15, "CB": -25},
        description="All-out attack. Attackers +15-20. CBs exposed (-25). +8% global.",
    ),
    "4-2-3-1": FormationCard(
        id="4-2-3-1",
        name="4-2-3-1",
        slots=["CB", "CB", "FB", "FB", "CM", "CM", "CAM", "LW", "RW", "ST"],
        hand_size=12,
        global_mult=1.02,
        position_bonus={"CM": 10, "CAM": 25, "ST": -15},
        description="Possession. CAM+25, CM+10. Lone ST isolated (-15). +2% global.",
    ),
    "4-5-1": FormationCard(
        id="4-5-1",
        name="4-5-1",
        slots=["CB", "CB", "FB", "FB", "CDM", "CM", "CM", "LW", "RW", "ST"],
        hand_size=12,
        global_mult=0.98,
        position_bonus={"CDM": 15, "LW": 20, "RW": 20, "ST": -20, "CB": -5},
        description="Counter. CDM+15, wingers+20. Lone ST isolated (-20). -2% global.",
    ),
}


def get_all_formations() -> list[FormationCard]:
    """Return all formations in display order."""
    return [FORMATIONS[k] for k in ["4-4-2", "4-3-3", "5-3-2", "3-4-3", "4-2-3-1", "4-5-1"]]
