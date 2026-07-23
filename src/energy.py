"""Energy system — finite player uses per match, injury risk, forced rotation.

Replaces the flat 0.7× fatigue multiplier with a tiered energy system:
  - FRESH (3 energy):   1.0× multiplier — full power
  - TIRED (2 energy):   0.85× multiplier — slight penalty  
  - EXHAUSTED (1 energy): 0.65× multiplier — significant penalty
  - INJURED (0 energy):  cannot play

Each use costs 1 energy. Using at EXHAUSTED has 25% injury risk.
Benched players recover 1 energy per round.
"""

import random
from dataclasses import dataclass, field
from enum import IntEnum


class EnergyState(IntEnum):
    """Player energy states and their stat multipliers."""
    FRESH = 3
    TIRED = 2
    EXHAUSTED = 1
    INJURED = 0


ENERGY_MULTIPLIERS = {
    EnergyState.FRESH: 1.0,
    EnergyState.TIRED: 0.85,
    EnergyState.EXHAUSTED: 0.65,
    EnergyState.INJURED: 0.0,
}

# Chance of injury when used at EXHAUSTED energy
INJURY_RISK = 0.25

# Energy recovered per round spent on bench
RECOVERY_PER_ROUND = 1

# Starting energy for all players
STARTING_ENERGY = 3


@dataclass
class PlayerEnergy:
    """Tracks a single player's energy across a match."""
    player_id: str
    current: int = STARTING_ENERGY  # 0-3
    is_injured: bool = False

    @property
    def state(self) -> EnergyState:
        if self.is_injured:
            return EnergyState.INJURED
        return EnergyState(self.current)

    @property
    def multiplier(self) -> float:
        """Return the stat multiplier for this player's current energy."""
        return ENERGY_MULTIPLIERS[self.state]

    @property
    def can_play(self) -> bool:
        return self.state != EnergyState.INJURED and self.current > 0

    def use(self) -> bool:
        """Consume 1 energy. Returns True if the player got injured from this use."""
        if self.is_injured:
            return False

        if self.current <= 1:
            # Risk injury when using at EXHAUSTED
            if random.random() < INJURY_RISK:
                self.is_injured = True
                self.current = 0
                return True

        self.current = max(0, self.current - 1)
        return False

    def recover(self, amount: int = RECOVERY_PER_ROUND) -> None:
        """Recover energy while on bench (between rounds)."""
        if self.is_injured:
            return  # injured players don't recover mid-match
        self.current = min(STARTING_ENERGY, self.current + amount)

    def full_recover(self) -> None:
        """Full recovery — match reset or journeyman ability."""
        self.current = STARTING_ENERGY
        self.is_injured = False

    def to_dict(self) -> dict:
        return {
            "player_id": self.player_id,
            "current": self.current,
            "is_injured": self.is_injured,
            "multiplier": self.multiplier,
            "state": self.state.name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerEnergy":
        pe = cls(player_id=data["player_id"])
        pe.current = data.get("current", STARTING_ENERGY)
        pe.is_injured = data.get("is_injured", False)
        return pe


@dataclass
class SquadEnergy:
    """Tracks energy for all squad members during a match.

    Provides a dict-like interface for backward compatibility
    (can be used like a dict[str, float] for multiplier lookups).
    """
    players: dict[str, PlayerEnergy] = field(default_factory=dict)

    # ── Initialization ────────────────────────────────────────────────

    def init_squad(self, player_ids: list[str]) -> None:
        """Initialize or reset energy for a squad."""
        self.players = {
            pid: PlayerEnergy(player_id=pid)
            for pid in player_ids
        }

    def get(self, player_id: str) -> PlayerEnergy:
        """Get or create a PlayerEnergy for a player."""
        if player_id not in self.players:
            self.players[player_id] = PlayerEnergy(player_id=player_id)
        return self.players[player_id]

    # ── Multiplier access (dict-compatible) ───────────────────────────

    def get_multiplier(self, player_id: str) -> float:
        """Return the fatigue/energy multiplier for a player. 
        Compatible with old fatigue.get(player_id, 1.0) pattern."""
        if player_id not in self.players:
            return 1.0
        return self.players[player_id].multiplier

    def __getitem__(self, player_id: str) -> float:
        """Dict-style access: energy[player_id] → multiplier."""
        return self.get_multiplier(player_id)

    def __contains__(self, player_id: str) -> bool:
        return player_id in self.players

    # ── Actions ───────────────────────────────────────────────────────

    def use_player(self, player_id: str) -> bool:
        """Mark a player as used this phase. Returns True if injured."""
        return self.get(player_id).use()

    def use_players(self, player_ids: list[str]) -> list[str]:
        """Use multiple players. Returns list of newly injured player IDs."""
        injured = []
        for pid in player_ids:
            if self.use_player(pid):
                injured.append(pid)
        return injured

    def bench_recovery(self, used_ids: set[str] | None = None) -> None:
        """Recover energy for players not used this round.
        If used_ids is None, recover all non-injured players."""
        for pid, energy in self.players.items():
            if used_ids is None or pid not in used_ids:
                energy.recover()

    def reset_all(self) -> None:
        """Full recovery — between matches or via journeyman."""
        for energy in self.players.values():
            energy.full_recover()

    def reset_player(self, player_id: str) -> None:
        """Full recovery for one player (journeyman ability)."""
        self.get(player_id).full_recover()

    # ── Utility ───────────────────────────────────────────────────────

    def get_state(self, player_id: str) -> EnergyState:
        return self.get(player_id).state

    def can_play(self, player_id: str) -> bool:
        return self.get(player_id).can_play

    def to_dict(self) -> dict:
        return {pid: pe.to_dict() for pid, pe in self.players.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "SquadEnergy":
        se = cls()
        se.players = {pid: PlayerEnergy.from_dict(pd) for pid, pd in data.items()}
        return se

    def summary(self) -> str:
        """Human-readable energy summary."""
        lines = []
        for pid, pe in self.players.items():
            dots = "•" * pe.current + "○" * (STARTING_ENERGY - pe.current)
            if pe.is_injured:
                dots = "⚠ INJURED"
            lines.append(f"  {pid:20s} [{dots}] ×{pe.multiplier:.2f}")
        return "\n".join(lines)
