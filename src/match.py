"""Match system — phase-based rounds, energy tracking, opponent targets.

Each round = 6 random phases of play. Phase = field a few players from your squad.
Players have 3 energy uses per match with tiered penalties.
Win 2 of 3 rounds = match won.


Campaign: 5 escalating matches (Group → R16 → QF → SF → Final) defined in
CAMPAIGN_MATCHES. Same squad, harder targets each match. Lose one = game over.
"""

import random
from dataclasses import dataclass, field
from src.cards import PlayerCard, SynergyCard, FormationCard
from src.phases import Phase, shuffle_phases, deal_phases, get_all_phases
from src.scoring import calculate_round_score
from src.energy import SquadEnergy
from src.opponents import Opponent, get_campaign_opponent


PHASE_FATIGUE_DECAY = 0.85  # Phase multiplier decay per use within a match
FATIGUE_PENALTY = 0.7  # Legacy constant — kept for test backward compatibility


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

    # Energy system — tracks per-player energy (3 uses/match, tiered penalties)
    energy: SquadEnergy = field(default_factory=SquadEnergy)

    # Phase fatigue — each phase decays ×0.85 per use within a match
    phase_fatigue: dict[str, float] = field(default_factory=dict)

    # Opponent adjustments — buff/nerf per round from scouting
    opponent_adjustments: dict[str, float] = field(default_factory=dict)

    # Opponent tactical system (v2)
    opponent: Opponent | None = None

    # Players used in the current round (for bench recovery tracking)
    _round_used_players: set[str] = field(default_factory=set)

    # Current phase placement
    field: list[tuple[PlayerCard, str]] = field(default_factory=list)

    # Carryover bonus from previous phase (e.g. Double Pivot → next phase attacker)
    carryover: dict | None = None

    # Squad-persistent synergy buffs (computed at match start)
    persistent_buffs: dict | None = None

    # Journeyman: once-per-match energy reset
    journeyman_used: bool = False

    # Momentum: chain multiplier that grows across phases (1.0, 1.2, 1.5)
    momentum: float = 1.0

    # Morale currency — earned from phase/round wins, spent in shop
    morale: int = 0

    # Shop buffs active for the current round
    shop_buffs: object | None = None  # ActiveBuffs instance or None

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
        """Return the energy/fatigue multiplier for a player."""
        return self.energy.get_multiplier(player_id)

    def apply_fatigue(self, player_id: str) -> None:
        """Mark a player as used this phase — consumes 1 energy with injury risk."""
        injured = self.energy.use_player(player_id)
        if injured:
            # TODO: surface injury event to UI
            pass


def create_match(
    squad: list[PlayerCard],
    synergies: list[SynergyCard],
    opponent_name: str = "FC Rivals",
    round_targets: list[int] | None = None,
    formation: FormationCard | None = None,
    persistent_buffs: dict | None = None,
    synergy_pool: list[SynergyCard] | None = None,
    opponent: Opponent | None = None,
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
        opponent=opponent,
    )
    
    # Initialize energy system for the squad
    ms.energy.init_squad([p.id for p in squad])
    
    # Initialize phase fatigue — all phases start at ×1.0
    ms.phase_fatigue = {p.id: 1.0 for p in get_all_phases()}
    
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
    """Set up a new round — all 8 phases available, pick 3, reset fatigue."""
    match.phase_hand = get_all_phases()  # All 8 phases, no dealing
    match.selected_phases = []
    match.phases = []  # populated when player selects phases
    match.current_phase_idx = 0
    # Opponent tactical modifiers are applied per-phase via match.opponent
    # (replaces the old random opponent_adjustments)
    match.opponent_adjustments = {}
    # Generate a minor scouting buff for one random phase
    if match.opponent:
        import random
        phases = get_all_phases()
        buffed = random.choice(phases) if phases else None
        if buffed:
            match.opponent_adjustments[buffed.id] = 1.15  # minor scouting advantage
    # Recover energy for benched players between rounds
    match.energy.bench_recovery(match._round_used_players)
    match._round_used_players.clear()
    match.phase_results = []
    match.round_score = 0
    match.field = []
    match.carryover = None
    match.momentum = 1.0  # Reset momentum for new round
    # All 18 phase-specific synergies available every round (no RNG)
    if match.synergy_pool:
        match.synergies = list(match.synergy_pool)


# ─── Opponent Adjustment Generation ────────────────────────────────────
# (Replaced by src/opponents.py — kept for backward compat in tests)


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

    Momentum: Earned by scoring ≥ 60% of round target in previous phase.
    Phase 1 = ×1.0, subsequent phases: +0.15 per consecutive hit, max ×1.3.

    Returns the scoring result dict.
    """
    phase = match.current_phase
    if phase is None:
        return {"total": 0, "breakdown": [], "fired_synergies": []}

    # Calculate momentum: earned by hitting ≥15% of round target in previous phase
    momentum_mult = 1.0
    if match.current_phase_idx > 0 and match.phase_results:
        prev_result = match.phase_results[-1]
        target = match.current_target
        # 15% threshold: roughly half of one phase's expected contribution
        if prev_result["total"] >= target * 0.15:
            momentum_mult = min(match.momentum + 0.15, 1.3)
        else:
            momentum_mult = 1.0  # Reset
    match.momentum = momentum_mult
    if match.shop_buffs and hasattr(match.shop_buffs, 'momentum_override') and match.shop_buffs.momentum_override is not None:
        momentum_mult = match.shop_buffs.momentum_override
    match.momentum = momentum_mult

    # Calculate phase multiplier: fatigue decay × opponent adjustment × tactical modifiers
    phase_id = phase.id
    fatigue_mult = match.phase_fatigue.get(phase_id, 1.0)
    opp_mult = match.opponent_adjustments.get(phase_id, 1.0)
    opp_tactical_mult = 1.0
    opp_mods_applied = []
    if match.opponent:
        opp_tactical_mult = match.opponent.get_phase_multiplier(phase.tag, match.current_phase_idx)
        if opp_tactical_mult < 1.0:
            opp_mods_applied = [
                m.description for m in match.opponent.get_modifiers()
                if m.matches_phase(phase.tag, match.current_phase_idx) and m.effect == "multiply"
            ]
    effective_phase_mult = fatigue_mult * opp_mult * opp_tactical_mult

    result = calculate_round_score(
        match.field, match.synergies, match.formation,
        fatigue=match.energy,
        carryover=match.carryover,
        persistent_buffs=match.persistent_buffs,
        momentum=match.momentum,
        shop_buffs=vars(match.shop_buffs) if match.shop_buffs else None,
        phase_mult=effective_phase_mult,
    )

    # Apply phase fatigue decay for next time this phase is used
    match.phase_fatigue[phase_id] = match.phase_fatigue.get(phase_id, 1.0) * PHASE_FATIGUE_DECAY

    # Consume energy for every player used this phase (with injury risk)
    for player, _ in match.field:
        match.energy.use_player(player.id)
        match._round_used_players.add(player.id)

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
        "targets": [2000, 3500, 5000],
        "tier": "Match 1/5 — Easy",
    },
    {
        "name": "Round of 16",
        "opponent": "Inter Your-Nan",
        "targets": [3000, 5000, 7000],
        "tier": "Match 2/5 — Moderate",
    },
    {
        "name": "Quarter Final",
        "opponent": "Borussia Mönchen-flapjack",
        "targets": [4000, 6500, 9000],
        "tier": "Match 3/5 — Challenging",
    },
    {
        "name": "Semi Final",
        "opponent": "Man City Oilers",
        "targets": [5000, 8000, 11500],
        "tier": "Match 4/5 — Elite",
    },
    {
        "name": "THE FINAL",
        "opponent": "Galácticos FC",
        "targets": [6500, 10000, 14500],
        "tier": "Match 5/5 — Final Boss",
    },
]
