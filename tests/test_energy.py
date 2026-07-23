"""Tests for the energy system — tiered player energy tracking."""

import pytest
from src.energy import (
    PlayerEnergy, SquadEnergy, EnergyState,
    ENERGY_MULTIPLIERS, INJURY_RISK, STARTING_ENERGY, RECOVERY_PER_ROUND,
)


class TestPlayerEnergy:
    """Test individual player energy tracking."""

    def test_starts_fresh(self):
        pe = PlayerEnergy(player_id="test")
        assert pe.current == 3
        assert pe.state == EnergyState.FRESH
        assert pe.multiplier == 1.0
        assert pe.can_play is True
        assert pe.is_injured is False

    def test_use_reduces_energy(self):
        pe = PlayerEnergy(player_id="test")
        injured = pe.use()
        assert injured is False
        assert pe.current == 2
        assert pe.state == EnergyState.TIRED
        assert pe.multiplier == 0.85

    def test_two_uses_exhausted(self):
        pe = PlayerEnergy(player_id="test")
        pe.use()  # 3→2
        pe.use()  # 2→1
        assert pe.current == 1
        assert pe.state == EnergyState.EXHAUSTED
        assert pe.multiplier == 0.65

    def test_three_uses_depleted(self):
        pe = PlayerEnergy(player_id="test")
        pe.use()  # 3→2
        pe.use()  # 2→1
        pe.use()  # 1→0 (with injury risk)
        assert pe.current <= 1  # either 0 or 1 (depending on injury)
        assert pe.state in (EnergyState.EXHAUSTED, EnergyState.INJURED)

    def test_recover_restores_energy(self):
        pe = PlayerEnergy(player_id="test")
        pe.use()  # 3→2
        pe.use()  # 2→1
        pe.recover()
        assert pe.current == 2  # back to TIRED
        assert pe.multiplier == 0.85

    def test_recover_capped_at_max(self):
        pe = PlayerEnergy(player_id="test")
        pe.use()  # 3→2
        pe.recover()
        assert pe.current == 3  # back to FRESH
        pe.recover()  # No overshoot
        assert pe.current == 3

    def test_injured_does_not_recover(self):
        pe = PlayerEnergy(player_id="test")
        pe.is_injured = True
        pe.current = 0
        pe.recover()
        assert pe.current == 0
        assert pe.is_injured is True

    def test_full_recover_resets_everything(self):
        pe = PlayerEnergy(player_id="test")
        pe.use()
        pe.use()
        pe.is_injured = True
        pe.full_recover()
        assert pe.current == 3
        assert pe.is_injured is False
        assert pe.multiplier == 1.0

    def test_injured_cannot_play(self):
        pe = PlayerEnergy(player_id="test")
        pe.is_injured = True
        assert pe.can_play is False
        assert pe.multiplier == 0.0

    def test_use_while_injured_noop(self):
        pe = PlayerEnergy(player_id="test")
        pe.is_injured = True
        pe.current = 0
        injured = pe.use()
        assert injured is False
        assert pe.current == 0

    def test_serialization_roundtrip(self):
        pe = PlayerEnergy(player_id="test")
        pe.use()
        pe.use()  # exhausted
        data = pe.to_dict()
        restored = PlayerEnergy.from_dict(data)
        assert restored.player_id == "test"
        assert restored.current == pe.current
        assert restored.is_injured == pe.is_injured
        assert restored.multiplier == pe.multiplier

    def test_injury_risk_exists(self):
        """Run many exhausted uses to verify injury can happen."""
        injury_count = 0
        trials = 1000
        for _ in range(trials):
            pe = PlayerEnergy(player_id="test")
            pe.current = 1  # Force to exhausted
            pe.use()
            if pe.is_injured:
                injury_count += 1
        # Should be roughly 25%, allow wide range
        rate = injury_count / trials
        assert 0.15 < rate < 0.35, f"Injury rate {rate:.2f} not in [0.15, 0.35]"


class TestSquadEnergy:
    """Test squad-level energy management."""

    def test_init_squad(self):
        se = SquadEnergy()
        se.init_squad(["a", "b", "c"])
        assert len(se.players) == 3
        for pid in ["a", "b", "c"]:
            assert se.get(pid).current == 3
            assert se.get_multiplier(pid) == 1.0

    def test_get_creates_on_fly(self):
        se = SquadEnergy()
        pe = se.get("new_player")
        assert pe.player_id == "new_player"
        assert pe.current == 3

    def test_get_multiplier_default(self):
        se = SquadEnergy()
        assert se.get_multiplier("unknown") == 1.0

    def test_dict_style_access(self):
        se = SquadEnergy()
        se.init_squad(["a"])
        assert se["a"] == 1.0
        assert "a" in se
        assert "b" not in se

    def test_use_player(self):
        se = SquadEnergy()
        se.init_squad(["a"])
        injured = se.use_player("a")
        assert injured is False
        assert se.get_multiplier("a") == 0.85  # TIRED

    def test_use_players_batch(self):
        se = SquadEnergy()
        se.init_squad(["a", "b", "c"])
        injured = se.use_players(["a", "b"])
        assert injured == []
        assert se.get_multiplier("a") == 0.85
        assert se.get_multiplier("b") == 0.85
        assert se.get_multiplier("c") == 1.0  # unused

    def test_bench_recovery_excludes_used(self):
        se = SquadEnergy()
        se.init_squad(["a", "b"])
        se.use_player("a")  # a: 3→2
        se.use_player("a")  # a: 2→1
        se.use_player("b")  # b: 3→2
        se.bench_recovery(used_ids={"a"})  # Only b recovers
        assert se.get_multiplier("a") == 0.65  # still exhausted
        assert se.get_multiplier("b") == 1.0    # recovered to fresh

    def test_bench_recovery_all(self):
        se = SquadEnergy()
        se.init_squad(["a", "b"])
        se.use_player("a")
        se.use_player("b")
        se.bench_recovery()  # No used_ids = recover all
        assert se.get_multiplier("a") == 1.0
        assert se.get_multiplier("b") == 1.0

    def test_reset_all(self):
        se = SquadEnergy()
        se.init_squad(["a"])
        se.use_player("a")
        se.use_player("a")
        assert se.get_multiplier("a") == 0.65
        se.reset_all()
        assert se.get_multiplier("a") == 1.0

    def test_reset_player(self):
        se = SquadEnergy()
        se.init_squad(["a", "b"])
        se.use_player("a")
        se.use_player("b")
        se.reset_player("a")
        assert se.get_multiplier("a") == 1.0
        assert se.get_multiplier("b") == 0.85

    def test_can_play(self):
        se = SquadEnergy()
        se.init_squad(["a"])
        assert se.can_play("a") is True
        se.get("a").is_injured = True
        assert se.can_play("a") is False

    def test_serialization_roundtrip(self):
        se = SquadEnergy()
        se.init_squad(["a", "b"])
        se.use_player("a")
        data = se.to_dict()
        restored = SquadEnergy.from_dict(data)
        assert len(restored.players) == 2
        assert restored.get_multiplier("a") == 0.85
        assert restored.get_multiplier("b") == 1.0

    def test_summary_string(self):
        se = SquadEnergy()
        se.init_squad(["a", "b"])
        se.use_player("a")
        summary = se.summary()
        assert "a" in summary
        assert "0.85" in summary


class TestEnergyMultipliers:
    """Verify multiplier values for each energy state."""

    def test_fresh_multiplier(self):
        assert ENERGY_MULTIPLIERS[EnergyState.FRESH] == 1.0

    def test_tired_multiplier(self):
        assert ENERGY_MULTIPLIERS[EnergyState.TIRED] == 0.85

    def test_exhausted_multiplier(self):
        assert ENERGY_MULTIPLIERS[EnergyState.EXHAUSTED] == 0.65

    def test_injured_multiplier(self):
        assert ENERGY_MULTIPLIERS[EnergyState.INJURED] == 0.0

    def test_fresh_is_strongest(self):
        mults = list(ENERGY_MULTIPLIERS.values())
        assert max(mults) == 1.0

    def test_injured_is_weakest(self):
        mults = list(ENERGY_MULTIPLIERS.values())
        assert min(mults) == 0.0
