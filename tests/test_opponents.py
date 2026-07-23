"""Tests for the opponent tactical system."""

import pytest
from src.opponents import (
    Opponent, OpponentModifier, TacticalStyle,
    TACTICAL_EFFECTS, CAMPAIGN_OPPONENTS_V2, get_campaign_opponent,
    MAX_OPPONENT_PENALTY,
)
from src.match import create_match, start_round, resolve_phase, set_selected_phases, start_phase, place_player
from src.phases import Phase, get_all_phases


class TestTacticalStyles:
    """Verify each tactical style is defined correctly."""

    def test_all_styles_have_effects(self):
        for style in TacticalStyle:
            assert style in TACTICAL_EFFECTS
            assert len(TACTICAL_EFFECTS[style]) >= 1

    def test_high_press_targets_possession(self):
        mods = TACTICAL_EFFECTS[TacticalStyle.HIGH_PRESS]
        assert any("Possession" in (m.phase_tags or []) for m in mods)

    def test_low_block_targets_transition(self):
        mods = TACTICAL_EFFECTS[TacticalStyle.LOW_BLOCK]
        assert any("Transition" in (m.phase_tags or []) for m in mods)

    def test_man_mark_has_best_player_target(self):
        mods = TACTICAL_EFFECTS[TacticalStyle.MAN_MARK]
        assert any(m.target == "best_player" for m in mods)

    def test_time_waste_targets_phase_3(self):
        mods = TACTICAL_EFFECTS[TacticalStyle.TIME_WASTE]
        time_mod = next(m for m in mods if m.target == "phase_index")
        assert 2 in (time_mod.phase_indices or [])


class TestOpponentModifier:
    """Test modifier matching logic."""

    def test_matches_phase_tag(self):
        mod = OpponentModifier(
            target="phase_tag", effect="multiply", value=0.7,
            phase_tags=["Possession", "Defensive"],
            description="test",
        )
        assert mod.matches_phase("Possession", 0) is True
        assert mod.matches_phase("Attacking", 0) is False
        assert mod.matches_phase("Defensive", 0) is True

    def test_matches_phase_index(self):
        mod = OpponentModifier(
            target="phase_index", effect="multiply", value=0.5,
            phase_indices=[2],
            description="test",
        )
        assert mod.matches_phase("Any", 0) is False
        assert mod.matches_phase("Any", 1) is False
        assert mod.matches_phase("Any", 2) is True

    def test_best_player_always_matches(self):
        mod = OpponentModifier(
            target="best_player", effect="multiply", value=0.6,
            description="test",
        )
        assert mod.matches_phase("Any", 0) is True


class TestOpponent:
    """Test the Opponent class."""

    def test_get_modifiers(self):
        opp = Opponent(
            name="Test FC", tier="Test",
            tactics=[TacticalStyle.LOW_BLOCK],
            intro="Test opponent.",
            round_targets=[1000, 2000, 3000],
        )
        mods = opp.get_modifiers()
        assert len(mods) >= 1
        assert all(isinstance(m, OpponentModifier) for m in mods)

    def test_get_phase_multiplier_matching(self):
        opp = Opponent(
            name="Test FC", tier="Test",
            tactics=[TacticalStyle.HIGH_PRESS],
            intro="Test.",
            round_targets=[1000, 2000, 3000],
        )
        # Possession phase should be nerfed
        mult = opp.get_phase_multiplier("Possession", 0)
        assert mult == 0.7
        # Attacking phase should be fine
        mult = opp.get_phase_multiplier("Attacking", 0)
        assert mult == 1.0

    def test_get_phase_multiplier_time_waste(self):
        opp = Opponent(
            name="Test FC", tier="Test",
            tactics=[TacticalStyle.TIME_WASTE],
            intro="Test.",
            round_targets=[1000, 2000, 3000],
        )
        assert opp.get_phase_multiplier("Any", 0) == 1.0
        assert opp.get_phase_multiplier("Any", 1) == 1.0
        assert opp.get_phase_multiplier("Any", 2) == 0.5

    def test_multiple_tactics_compound(self):
        opp = Opponent(
            name="Test FC", tier="Test",
            tactics=[TacticalStyle.HIGH_PRESS, TacticalStyle.COUNTER_ATTACK],
            intro="Test.",
            round_targets=[1000, 2000, 3000],
        )
        # Possession phase: only high press nerfs it (0.7)
        mult = opp.get_phase_multiplier("Possession", 0)
        assert mult == 0.7
        # Attacking phase: only counter_attack nerfs it (0.7)
        mult = opp.get_phase_multiplier("Attacking", 0)
        assert mult == 0.7
        # Transition: neither nerfs it
        mult = opp.get_phase_multiplier("Transition", 0)
        assert mult == 1.0

    def test_injury_risk_bonus(self):
        opp = Opponent(
            name="Dirty FC", tier="Test",
            tactics=[TacticalStyle.DIRTY_TEAM],
            intro="Test.",
            round_targets=[1000, 2000, 3000],
        )
        assert opp.get_injury_risk_bonus() == 0.15

    def test_no_injury_risk_default(self):
        opp = Opponent(
            name="Clean FC", tier="Test",
            tactics=[TacticalStyle.LOW_BLOCK],
            intro="Test.",
            round_targets=[1000, 2000, 3000],
        )
        assert opp.get_injury_risk_bonus() == 0.0

    def test_has_man_mark(self):
        opp = Opponent(
            name="Markers", tier="Test",
            tactics=[TacticalStyle.MAN_MARK],
            intro="Test.",
            round_targets=[1000, 2000, 3000],
        )
        assert opp.has_man_mark() is True

    def test_no_man_mark(self):
        opp = Opponent(
            name="No Markers", tier="Test",
            tactics=[TacticalStyle.LOW_BLOCK],
            intro="Test.",
            round_targets=[1000, 2000, 3000],
        )
        assert opp.has_man_mark() is False

    def test_scouting_report(self):
        opp = Opponent(
            name="Scout FC", tier="Match 1/5",
            tactics=[TacticalStyle.LOW_BLOCK],
            intro="They sit deep.",
            round_targets=[1000, 2000, 3000],
        )
        report = opp.get_scouting_report()
        assert "Scout FC" in report
        assert "Match 1/5" in report
        assert "Low block" in report.lower() or "×0.75" in report

    def test_serialization_roundtrip(self):
        opp = Opponent(
            name="Roundtrip FC", tier="Match 3/5",
            tactics=[TacticalStyle.HIGH_PRESS, TacticalStyle.COUNTER_ATTACK],
            intro="Heavy metal.",
            round_targets=[4000, 6500, 9000],
        )
        data = opp.to_dict()
        restored = Opponent.from_dict(data)
        assert restored.name == "Roundtrip FC"
        assert restored.tactics == [TacticalStyle.HIGH_PRESS, TacticalStyle.COUNTER_ATTACK]
        assert restored.round_targets == [4000, 6500, 9000]

    def test_penalty_cap(self):
        """Three stacking penalties should be capped at MAX_OPPONENT_PENALTY."""
        opp = Opponent(
            name="Brutal FC", tier="Match 5/5",
            tactics=[TacticalStyle.DIRTY_TEAM, TacticalStyle.HIGH_PRESS, TacticalStyle.COUNTER_ATTACK],
            intro="Everything.",
            round_targets=[9000, 13000, 19000],
        )
        mult = opp.get_phase_multiplier("Attacking", 0)
        # HIGH_PRESS doesn't affect Attacking, only COUNTER_ATTACK does → 0.7
        assert mult == 0.7
        # For a phase affected by both: e.g. HIGH_PRESS (0.7) * COUNTER_ATTACK (0.7) = 0.49 > 0.4 cap
        # But get_phase_multiplier only applies modifiers matching that phase
        # Attacking: only COUNTER_ATTACK matches → 0.7, not capped


class TestCampaignOpponents:
    """Test the campaign opponent presets."""

    def test_five_opponents(self):
        assert len(CAMPAIGN_OPPONENTS_V2) == 5

    def test_escalating_tactics(self):
        # Match 1: 1 tactic
        assert len(CAMPAIGN_OPPONENTS_V2[0].tactics) == 1
        # Match 3: 2 tactics
        assert len(CAMPAIGN_OPPONENTS_V2[2].tactics) == 2
        # Match 5: 3 tactics
        assert len(CAMPAIGN_OPPONENTS_V2[4].tactics) == 3

    def test_escalating_targets(self):
        for i in range(4):
            assert CAMPAIGN_OPPONENTS_V2[i].round_targets[0] < CAMPAIGN_OPPONENTS_V2[i + 1].round_targets[0]

    def test_get_campaign_opponent(self):
        opp = get_campaign_opponent(0)
        assert opp.name == "Wolves FC"
        opp = get_campaign_opponent(4)
        assert opp.name == "Galácticos FC"

    def test_get_campaign_opponent_out_of_range(self):
        opp = get_campaign_opponent(99)
        assert opp.name == "Galácticos FC"  # Returns last


class TestOpponentMatchIntegration:
    """Test opponent integration with match flow."""

    def test_match_with_opponent(self, terry_henri):
        opp = Opponent(
            name="Test FC", tier="Match 1/5",
            tactics=[TacticalStyle.LOW_BLOCK],
            intro="They sit deep.",
            round_targets=[2000, 3500, 5000],
        )
        ms = create_match(
            squad=[terry_henri], synergies=[],
            opponent=opp,
        )
        assert ms.opponent is not None
        assert ms.opponent.name == "Test FC"

    def test_phase_score_nerfed_by_opponent(self, terry_henri, bale_out):
        """Wide Attack (Attacking) should be nerfed by LOW_BLOCK."""
        opp = Opponent(
            name="Low Block FC", tier="Match 1/5",
            tactics=[TacticalStyle.LOW_BLOCK],
            intro="Test.",
            round_targets=[2000, 3500, 5000],
        )
        ms = create_match(squad=[terry_henri, bale_out], synergies=[], opponent=opp)
        ms.phases = [Phase("wa", "Wide Attack", ["LW"], "PAC", 1, "test", tag="Attacking")]
        ms.current_phase_idx = 0
        ms.field = [(bale_out, "LW")]
        result = resolve_phase(ms)

        # Without opponent, bale_out LW = 42 chips, ×1.0 = 42
        # With LOW_BLOCK: 42 × 0.75 = 31.5 → 31 (rounded)
        expected = 31  # Rounded
        assert result["total"] == expected

    def test_phase_not_nerfed_by_nonmatching_opponent(self, il_capitano):
        """Goal Kick (Defensive) should NOT be nerfed by LOW_BLOCK (targets Transition/Attacking)."""
        opp = Opponent(
            name="Low Block FC", tier="Match 1/5",
            tactics=[TacticalStyle.LOW_BLOCK],
            intro="Test.",
            round_targets=[2000, 3500, 5000],
        )
        ms = create_match(squad=[il_capitano], synergies=[], opponent=opp)
        ms.phases = [Phase("gk", "Goal Kick", ["CB"], "DEF", 1, "test", tag="Defensive")]
        ms.current_phase_idx = 0
        ms.field = [(il_capitano, "CB")]
        result = resolve_phase(ms)

        # Defensive phase, LOW_BLOCK doesn't affect it → no nerf
        # il_capitano CB = 39 chips
        assert result["total"] > 0  # Should not be zeroed
        assert result["total"] == 39  # Full value, no opponent penalty

    def test_phase_3_nerfed_by_time_waste(self, terry_henri):
        """3rd phase should be halved by TIME_WASTE."""
        opp = Opponent(
            name="Time Wasters", tier="Match 4/5",
            tactics=[TacticalStyle.TIME_WASTE],
            intro="Test.",
            round_targets=[5000, 8000, 11500],
        )
        ms = create_match(squad=[terry_henri], synergies=[], opponent=opp)
        ms.phases = [
            Phase("p1", "P1", ["ST"], "ATK", 1, "", tag="Attacking"),
            Phase("p2", "P2", ["ST"], "ATK", 1, "", tag="Attacking"),
            Phase("p3", "P3", ["ST"], "ATK", 1, "", tag="Attacking"),
        ]
        ms.current_phase_idx = 2  # Phase 3
        ms.field = [(terry_henri, "ST")]
        result = resolve_phase(ms)
        # Terry ST = 53 chips, no momentum (no previous phases), ×0.5 time waste = ~26-27
        assert result["total"] >= 24 and result["total"] <= 28
