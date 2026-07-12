"""Match system — phase-based rounds, fatigue tracking, opponent targets.

Each round = 6 random phases of play. Phase = field a few players from your squad.
Players get ×0.7 fatigue per use. Win 2 of 3 rounds = match won.


Campaign: 5 escalating matches (Group → R16 → QF → SF → Final) defined in
CAMPAIGN_MATCHES. Same squad, harder targets each match. Lose one = game over.
"""

import random
from dataclasses import dataclass, field
from src.cards import PlayerCard, SynergyCard, FormationCard
from src.phases import Phase, shuffle_phases, deal_phases
from src.scoring import calculate_round_score


FATIGUE_PENALTY = 0.7  # Each use multiplies stats by 0.7


@dataclass
class MatchState:
    """Tracks the state of an ongoing match."""
    squad: list[PlayerCard]
    synergies: list[SynergyCard]
    synergy_pool: list[SynergyCard] = field(default_factory=list)  # all phase-specific synergies to re-sample from
    formation: FormationCard | None = None
    opponent_name: str = "FC Rivals"
    round_targets: list[int] = field(default_factory=lambda: [700, 1000, 1400])
    current_round: int = 0           # 0-indexed (0, 1, 2)
    rounds_won: int = 0
    rounds_lost: int = 0

    # Phase tracking
    phases: list[Phase] = field(default_factory=list)
    phase_hand: list[Phase] = field(default_factory=list)  # 6 dealt phase cards
    selected_phases: list[Phase] = field(default_factory=list)  # 3 player-selected, in order
    current_phase_idx: int = 0
    phase_results: list[dict] = field(default_factory=list)
    round_score: int = 0

    # Fatigue: player_id → multiplier (starts at 1.0, ×0.7 each use)
    fatigue: dict[str, float] = field(default_factory=dict)

    # Current phase placement
    field: list[tuple[PlayerCard, str]] = field(default_factory=list)

    # Carryover bonus from previous phase (e.g. Double Pivot → next phase attacker)
    carryover: dict | None = None

    # Squad-persistent synergy buffs (computed at match start)
    persistent_buffs: dict | None = None

    # Journeyman: once-per-match fatigue reset
    journeyman_used: bool = False

    # Momentum: chain multiplier that grows across phases (1.0, 1.2, 1.5)
    momentum: float = 1.0

    @property
    def rounds_needed(self) -> int:
        """Win 2 out of 3 rounds."""
        return 2

    @property
    def is_match_over(self) -> bool:
        return self.rounds_won >= self.rounds_needed or self.rounds_lost >= self.rounds_needed

    @property
    def is_match_won(self) -> bool:
        return self.rounds_won >= self.rounds_needed

    @property
    def current_target(self) -> int:
        return self.round_targets[self.current_round] if self.current_round < len(self.round_targets) else 9999

    @property
    def current_phase(self) -> Phase | None:
        if 0 <= self.current_phase_idx < len(self.phases):
            return self.phases[self.current_phase_idx]
        return None

    def get_fatigue(self, player_id: str) -> float:
        return self.fatigue.get(player_id, 1.0)

    def apply_fatigue(self, player_id: str) -> None:
        """Mark a player as used this phase — ×fatigue_penalty for next time."""
        penalty = FATIGUE_PENALTY
        if self.persistent_buffs:
            penalty = self.persistent_buffs.get("fatigue_penalty", FATIGUE_PENALTY)
        current = self.fatigue.get(player_id, 1.0)
        self.fatigue[player_id] = current * penalty


def create_match(
    squad: list[PlayerCard],
    synergies: list[SynergyCard],
    opponent_name: str = "FC Rivals",
    round_targets: list[int] | None = None,
    formation: FormationCard | None = None,
    persistent_buffs: dict | None = None,
    synergy_pool: list[SynergyCard] | None = None,
) -> MatchState:
    """Initialize a new match."""
    if round_targets is None:
        round_targets = _generate_targets()

    ms = MatchState(
        squad=squad,
        synergies=synergies,
        synergy_pool=synergy_pool or [],
        opponent_name=opponent_name,
        round_targets=round_targets,
        formation=formation,
        persistent_buffs=persistent_buffs,
    )
    return ms


def _generate_targets() -> list[int]:
    """Generate 3 round targets for 3-phase rounds.
    
    Baseline per-phase score: ~200-400 with decent squad.
    Best-case per-phase: ~400-600 with optimal picks + persistent buffs.
    3-phase round total: ~600-1200 for good play, ~400-700 for weak play.
    """
    return [
        400,   # Round 1: beatable with good phase picks
        650,   # Round 2: needs synergy stacking + rotation  
        900,   # Round 3: demands near-perfect phase management
    ]


# ─── Round Management ────────────────────────────────────────────────

def start_round(match: MatchState) -> None:
    """Set up a new round — deal 6 phase cards, reset fatigue, re-roll synergies, clear state."""
    match.phase_hand = deal_phases(6)
    match.selected_phases = []
    match.phases = []  # populated when player selects phases
    match.current_phase_idx = 0
    # Recover 50% of lost fatigue between rounds (tension carries over)
    for pid in list(match.fatigue.keys()):
        current = match.fatigue[pid]
        match.fatigue[pid] = 1.0 - (1.0 - current) * 0.5
    match.phase_results = []
    match.round_score = 0
    match.field = []
    match.carryover = None
    match.momentum = 1.0  # Reset momentum for new round
    # All 18 phase-specific synergies available every round (no RNG)
    if match.synergy_pool:
        match.synergies = list(match.synergy_pool)


def start_phase(match: MatchState) -> None:
    """Set up the current phase — clear field for placement."""
    match.field = []


def set_selected_phases(match: MatchState, selected: list[Phase]) -> None:
    """Set the player's chosen 3 phases (in order) from the dealt hand."""
    match.selected_phases = list(selected)
    match.phases = list(selected)
    match.current_phase_idx = 0


def place_player(match: MatchState, player: PlayerCard, slot_position: str) -> bool:
    """Place a player on the field for the current phase.

    The slot_position is the position they occupy this phase
    (determines chips formula via CHIPS_FORMULA).
    """
    match.field.append((player, slot_position))
    return True


def remove_from_field(match: MatchState, index: int) -> PlayerCard | None:
    """Remove a player from the current phase field."""
    if 0 <= index < len(match.field):
        player, _ = match.field.pop(index)
        return player
    return None


def resolve_phase(match: MatchState) -> dict:
    """Score the current phase, apply fatigue to used players.

    Also consumes any carryover bonus (e.g. Double Pivot) and captures
    the next phase's carryover from this phase's synergies.

    Momentum grows across phases: Phase 1 = ×1.0, Phase 2 = ×1.2, Phase 3 = ×1.5

    Returns the scoring result dict.
    """
    phase = match.current_phase
    if phase is None:
        return {"total": 0, "breakdown": [], "fired_synergies": []}

    # Calculate momentum based on phase index (0, 1, 2)
    momentum_mult = {0: 1.0, 1: 1.2, 2: 1.5}.get(match.current_phase_idx, 1.5)
    match.momentum = momentum_mult

    result = calculate_round_score(
        match.field, match.synergies, match.formation,
        fatigue=match.fatigue,
        carryover=match.carryover,
        persistent_buffs=match.persistent_buffs,
        momentum=match.momentum,
    )

    # Apply fatigue to every player used this phase
    for player, _ in match.field:
        match.apply_fatigue(player.id)

    # Handle carryover: consume current, capture next
    match.carryover = result.get("next_carryover")

    result["phase_name"] = phase.name
    result["phase_weight"] = phase.weight
    match.phase_results.append(result)
    match.round_score += result["total"]

    return result


def advance_phase(match: MatchState) -> bool:
    """Move to the next phase. Returns True if round is over (all 6 phases done)."""
    match.current_phase_idx += 1
    return match.current_phase_idx >= len(match.phases)


def check_round(match: MatchState) -> bool:
    """Check if the round target was beat. Returns True if won."""
    won = match.round_score >= match.current_target
    if won:
        match.rounds_won += 1
    else:
        match.rounds_lost += 1
    return won


# ─── Opponent Presets ────────────────────────────────────────────────

OPPONENTS = {
    "easy": [
        {"name": "FC Relegation", "targets": [300, 400, 550]},
        {"name": "Athletico Average", "targets": [350, 450, 600]},
        {"name": "Real Socie-dad Jokes", "targets": [400, 500, 650]},
    ],
    "normal": [
        {"name": "Inter Your-Nan", "targets": [400, 550, 750]},
        {"name": "Borussia Mönchen-flapjack", "targets": [450, 600, 800]},
        {"name": "AC Eezy", "targets": [500, 650, 850]},
    ],
    "elite": [
        {"name": "Bayern Never-losing", "targets": [600, 750, 1000]},
        {"name": "Man City Oilers", "targets": [700, 850, 1100]},
    ],
    "boss": [
        {"name": "Real Madrid Galácticos", "targets": [800, 950, 1250]},
        {"name": "Final Boss FC", "targets": [900, 1050, 1400]},
    ],
}


def get_opponent(difficulty: str = "normal") -> dict:
    """Get a random opponent preset by difficulty."""
    presets = OPPONENTS.get(difficulty, OPPONENTS["normal"])
    return random.choice(presets)


# ─── Campaign Mode ────────────────────────────────────────────────────

CAMPAIGN_MATCHES = [
    {
        "name": "Group Stage",
        "opponent": "Wolves FC",
        "targets": [700, 900, 1200],
        "tier": "Match 1/5 — Easy",
    },
    {
        "name": "Round of 16",
        "opponent": "Inter Your-Nan",
        "targets": [900, 1100, 1500],
        "tier": "Match 2/5 — Moderate",
    },
    {
        "name": "Quarter Final",
        "opponent": "Borussia Mönchen-flapjack",
        "targets": [1100, 1400, 1700],
        "tier": "Match 3/5 — Challenging",
    },
    {
        "name": "Semi Final",
        "opponent": "Man City Oilers",
        "targets": [1400, 1700, 2100],
        "tier": "Match 4/5 — Elite",
    },
    {
        "name": "THE FINAL",
        "opponent": "Galácticos FC",
        "targets": [1700, 2100, 2500],
        "tier": "Match 5/5 — Final Boss",
    },
]
