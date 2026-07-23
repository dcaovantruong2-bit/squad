"""Opponent tactical system — boss-blind-style counters.

Each campaign opponent has 1-3 tactical styles that actively counter
specific player strategies, forcing adaptation.

Tactical styles:
  HIGH_PRESS      — Possession & Defensive phases -30%
  LOW_BLOCK       — Transition & Attacking phases -25%  
  MAN_MARK        — Best player's chips ×0.6
  TIME_WASTE      — Phase 3 scores halved
  DIRTY_TEAM      — +15% injury risk
  POSSESSION_HEAVY— Transition phases -30%
  COUNTER_ATTACK  — Attacking phases -30%
"""

from dataclasses import dataclass, field
from enum import Enum


class TacticalStyle(Enum):
    """How the opponent plays — each style counters specific approaches."""
    HIGH_PRESS = "high_press"
    LOW_BLOCK = "low_block"
    MAN_MARK = "man_mark"
    TIME_WASTE = "time_waste"
    DIRTY_TEAM = "dirty_team"
    POSSESSION_HEAVY = "possession_heavy"
    COUNTER_ATTACK = "counter_attack"


@dataclass
class OpponentModifier:
    """A single tactical modifier applied by the opponent."""
    target: str           # "phase_tag", "phase_index", "best_player", "injury"
    effect: str           # "multiply", "add_injury_risk"
    value: float          # multiplier or flat value
    description: str      # human-readable
    # Optional: which phase tags / indices to apply to
    phase_tags: list[str] | None = None
    phase_indices: list[int] | None = None

    def matches_phase(self, phase_tag: str, phase_idx: int) -> bool:
        """Check if this modifier applies to the current phase."""
        if self.target == "phase_tag" and self.phase_tags:
            return phase_tag in self.phase_tags
        if self.target == "phase_index" and self.phase_indices:
            return phase_idx in self.phase_indices
        if self.target == "best_player":
            return True  # Always applies if there are players on field
        if self.target == "injury":
            return True  # Always applies, checked during energy use
        return False


# ─── Tactical Style Definitions ────────────────────────────────────────

TACTICAL_EFFECTS: dict[TacticalStyle, list[OpponentModifier]] = {
    TacticalStyle.HIGH_PRESS: [
        OpponentModifier(
            target="phase_tag", effect="multiply", value=0.7,
            phase_tags=["Possession", "Defensive"],
            description="High press disrupts build-up — Possession & Defensive phases ×0.7",
        ),
    ],
    TacticalStyle.LOW_BLOCK: [
        OpponentModifier(
            target="phase_tag", effect="multiply", value=0.75,
            phase_tags=["Transition", "Attacking"],
            description="Low block — Counter & Attacking phases ×0.75",
        ),
    ],
    TacticalStyle.MAN_MARK: [
        OpponentModifier(
            target="best_player", effect="multiply", value=0.6,
            description="Your best player is man-marked — their contribution ×0.6",
        ),
    ],
    TacticalStyle.TIME_WASTE: [
        OpponentModifier(
            target="phase_index", effect="multiply", value=0.5,
            phase_indices=[2],  # 3rd phase (0-indexed)
            description="Time wasting — Phase 3 scores halved. Score early!",
        ),
    ],
    TacticalStyle.DIRTY_TEAM: [
        OpponentModifier(
            target="injury", effect="add_injury_risk", value=0.15,
            description="Dirty tackles — +15% injury risk on exhausted players",
        ),
    ],
    TacticalStyle.POSSESSION_HEAVY: [
        OpponentModifier(
            target="phase_tag", effect="multiply", value=0.7,
            phase_tags=["Transition"],
            description="They keep the ball — Transition phases ×0.7",
        ),
    ],
    TacticalStyle.COUNTER_ATTACK: [
        OpponentModifier(
            target="phase_tag", effect="multiply", value=0.7,
            phase_tags=["Attacking"],
            description="Sits deep and counters — Attacking phases ×0.7",
        ),
    ],
}

# Prevent stacking too harshly: cap total opponent penalty
MAX_OPPONENT_PENALTY = 0.40  # Never worse than ×0.4


@dataclass
class Opponent:
    """An opponent team with tactical traits for a match."""
    name: str
    tier: str              # "Match 1/5" etc.
    tactics: list[TacticalStyle]
    intro: str             # scouting report flavor text
    round_targets: list[int]

    def get_modifiers(self) -> list[OpponentModifier]:
        """Get all active modifiers from this opponent's tactical styles."""
        mods = []
        for style in self.tactics:
            mods.extend(TACTICAL_EFFECTS.get(style, []))
        return mods

    def get_scouting_report(self) -> str:
        """Human-readable scouting report."""
        lines = [f"🕵 {self.name} — {self.tier}", f"   {self.intro}", ""]
        for mod in self.get_modifiers():
            lines.append(f"   ⚠ {mod.description}")
        return "\n".join(lines)

    def apply_modifiers(
        self,
        score: float,
        phase_tag: str,
        phase_idx: int,
        field: list | None = None,
    ) -> tuple[float, list[str]]:
        """Apply all matching modifiers to a phase score.

        Returns (adjusted_score, list of modifier descriptions applied).
        """
        applied = []
        result = score

        for mod in self.get_modifiers():
            if not mod.matches_phase(phase_tag, phase_idx):
                continue

            if mod.target == "best_player" and mod.effect == "multiply":
                # Apply to the best player's contribution, not the total.
                # Simplified: apply a milder global penalty since we can't
                # isolate one player's contribution here.
                # Actual per-player application is done in calculate_round_score.
                applied.append(mod.description)
                continue  # handled per-player in scoring

            if mod.effect == "multiply":
                result *= mod.value
                applied.append(mod.description)

            # Injury risk is handled by energy system, not scoring
            if mod.target == "injury":
                applied.append(mod.description)

        # Enforce minimum penalty cap
        if result < score * MAX_OPPONENT_PENALTY and len(applied) >= 2:
            result = score * MAX_OPPONENT_PENALTY
            applied.append(f"⚠ Penalty capped at ×{MAX_OPPONENT_PENALTY} (maximum)")

        return result, applied

    def get_phase_multiplier(self, phase_tag: str, phase_idx: int) -> float:
        """Get the combined phase multiplier from all matching modifiers.
        Used for the phase_mult parameter in scoring.
        """
        mult = 1.0
        for mod in self.get_modifiers():
            if mod.matches_phase(phase_tag, phase_idx) and mod.effect == "multiply":
                mult *= mod.value
        return max(mult, MAX_OPPONENT_PENALTY)

    def get_injury_risk_bonus(self) -> float:
        """Additional injury risk from dirty_team tactics."""
        bonus = 0.0
        for mod in self.get_modifiers():
            if mod.target == "injury" and mod.effect == "add_injury_risk":
                bonus += mod.value
        return bonus

    def has_man_mark(self) -> bool:
        """Check if opponent man-marks the best player."""
        return any(
            mod.target == "best_player"
            for mod in self.get_modifiers()
        )

    def get_man_mark_multiplier(self) -> float:
        """Get the man-mark multiplier (applied to best player)."""
        for mod in self.get_modifiers():
            if mod.target == "best_player":
                return mod.value
        return 1.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "tier": self.tier,
            "tactics": [t.value for t in self.tactics],
            "intro": self.intro,
            "round_targets": self.round_targets,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Opponent":
        return cls(
            name=data["name"],
            tier=data["tier"],
            tactics=[TacticalStyle(t) for t in data["tactics"]],
            intro=data["intro"],
            round_targets=data["round_targets"],
        )


# ─── Campaign Opponents ────────────────────────────────────────────────

CAMPAIGN_OPPONENTS_V2 = [
    Opponent(
        name="Wolves FC",
        tier="Match 1/5",
        tactics=[TacticalStyle.LOW_BLOCK],
        intro="Relegation battlers. Sit deep — hard to break down. Avoid Transition and Attacking phases.",
        round_targets=[2000, 3500, 5000],
    ),
    Opponent(
        name="Inter Your-Nan",
        tier="Match 2/5",
        tactics=[TacticalStyle.POSSESSION_HEAVY],
        intro="Mid-table side. They keep the ball forever — Transition phases are stifled.",
        round_targets=[3000, 5000, 7000],
    ),
    Opponent(
        name="Borussia Mönchen-flapjack",
        tier="Match 3/5",
        tactics=[TacticalStyle.HIGH_PRESS, TacticalStyle.COUNTER_ATTACK],
        intro="Heavy metal football. Press relentlessly AND hit on the break. Possession and Attacking phases will suffer.",
        round_targets=[4000, 6500, 9000],
    ),
    Opponent(
        name="Man City Oilers",
        tier="Match 4/5",
        tactics=[TacticalStyle.MAN_MARK, TacticalStyle.TIME_WASTE],
        intro="Elite man-marking. Your best player is neutralised. Score early or the clock kills you.",
        round_targets=[5000, 8000, 11500],
    ),
    Opponent(
        name="Galácticos FC",
        tier="Match 5/5",
        tactics=[TacticalStyle.DIRTY_TEAM, TacticalStyle.MAN_MARK, TacticalStyle.HIGH_PRESS],
        intro="The best in the world. Three tactical threats at once: dirty tackles, man-marking, and relentless pressing.",
        round_targets=[6500, 10000, 14500],
    ),
]


def get_campaign_opponent(match_idx: int) -> Opponent:
    """Get the opponent for a given campaign match index (0-4)."""
    if 0 <= match_idx < len(CAMPAIGN_OPPONENTS_V2):
        return CAMPAIGN_OPPONENTS_V2[match_idx]
    return CAMPAIGN_OPPONENTS_V2[-1]
