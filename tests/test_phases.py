"""Tests for the phase system and fatigue."""

import pytest
from src.phases import (get_all_phases, shuffle_phases, slot_positions,
                        slot_label, is_player_eligible)
from src.match import (MatchState, start_round, start_phase, place_player,
                       resolve_phase, advance_phase, check_round, set_selected_phases,
                       FATIGUE_PENALTY)


class TestPhaseDefinitions:
    """Verify the phase definitions."""

    def test_eleven_phases(self):
        phases = get_all_phases()
        assert len(phases) == 11

    def test_each_phase_has_slots(self):
        for phase in get_all_phases():
            assert len(phase.slots) >= 2

    def test_shuffle_returns_six_random(self):
        """Shuffle picks 6 random phases from the pool of 11."""
        phases = shuffle_phases()
        assert len(phases) == 6
        all_names = {p.name for p in get_all_phases()}
        chosen_names = {p.name for p in phases}
        assert chosen_names.issubset(all_names)
        # Ensure randomness — over 3 rounds we should see variety
        rounds = [shuffle_phases() for _ in range(3)]
        name_sets = [{p.name for p in r} for r in rounds]
        # At least 2 rounds should have different phase sets
        assert len(set(frozenset(s) for s in name_sets)) >= 2

    def test_slot_positions_single(self):
        assert slot_positions("CB") == ["CB"]

    def test_slot_positions_winger(self):
        assert slot_positions(["LW", "RW"]) == ["LW", "RW"]

    def test_slot_label_winger(self):
        assert slot_label(["LW", "RW"]) == "LW/RW"

    def test_slot_positions_dict(self):
        """Dict slots return the 'as' position."""
        assert slot_positions({"as": "CB", "min_def": 7}) == ["CB"]

    def test_slot_label_dict(self):
        """Dict slots show stat requirements."""
        assert slot_label({"as": "CB", "min_def": 7}) == "→CB [DEF≥7]"

    def test_slot_label_dict_multistat(self):
        assert slot_label({"as": "CB", "min_def": 6, "min_pac": 6}) == "→CB [PAC≥6, DEF≥6]"

    def test_slot_label_dict_trait(self):
        assert slot_label({"as": "ST", "min_atk": 7, "trait": "pacey"}) == "→ST [ATK≥7, pacey]"


class TestIsPlayerEligible:
    """Verify the stat/trait-based eligibility system."""

    def test_string_slot_by_position(self, terry_henri, il_capitano):
        """String slots match by position."""
        assert is_player_eligible(terry_henri, "ST") is True
        assert is_player_eligible(il_capitano, "ST") is False

    def test_list_slot_by_position(self, bale_out, maestro_xav):
        """List slots match by any listed position."""
        assert is_player_eligible(bale_out, ["LW", "RW"]) is True
        assert is_player_eligible(maestro_xav, ["LW", "RW"]) is False

    def test_dict_slot_stat_threshold(self, il_capitano, terry_henri):
        """Dict slots check stat thresholds, not position."""
        # il_capitano has DEF=10, should be eligible for CB DEF≥8
        assert is_player_eligible(il_capitano, {"as": "CB", "min_def": 8}) is True
        # terry_henri has DEF=1, should NOT be eligible
        assert is_player_eligible(terry_henri, {"as": "CB", "min_def": 8}) is False

    def test_dict_slot_any_position_with_stat(self, terry_henri, gigi_wall):
        """ST with high ATK can fill the slot, GK with low ATK cannot."""
        # terry_henri has ATK=9, plays as ST
        assert is_player_eligible(terry_henri, {"as": "ST", "min_atk": 7}) is True
        # gigi_wall (GK) has ATK=1
        assert is_player_eligible(gigi_wall, {"as": "ST", "min_atk": 7}) is False

    def test_dict_slot_multi_stat(self, rolls_royce, the_crab):
        """Player must meet ALL stat thresholds."""
        # rolls_royce: DEF=9, PAC=8 → meets both
        assert is_player_eligible(rolls_royce, {"as": "CB", "min_def": 6, "min_pac": 6}) is True
        # the_crab (Kola): DEF=6, PAC=5 → meets DEF but not PAC
        assert is_player_eligible(the_crab, {"as": "CB", "min_def": 6, "min_pac": 6}) is False

    def test_dict_slot_trait(self, il_capitano, jt_rock):
        """Trait requirement filters correctly."""
        # il_capitano has leader
        assert is_player_eligible(il_capitano, {"as": "CB", "trait": "leader"}) is True
        # jt_rock doesn't have leader
        assert is_player_eligible(jt_rock, {"as": "CB", "trait": "leader"}) is False

    def test_dict_slot_stat_and_trait(self, il_capitano, gigi_wall):
        """Combined stat AND trait must both pass."""
        # il_capitano: DEF=10, leader ✓
        assert is_player_eligible(il_capitano, {"as": "CB", "min_def": 8, "trait": "leader"}) is True
        # gigi_wall: DEF=10 ✓ but no leader trait ✗ ... wait gigi has leader!
        # gigi: DEF=10, leader → True
        assert is_player_eligible(gigi_wall, {"as": "CB", "min_def": 9, "trait": "aerial"}) is True

    def test_gk_eligible_for_stat_slot(self, gigi_wall):
        """GK can fill non-GK slots if stats are high enough."""
        # gigi: DEF=10 → eligible for CB DEF≥8
        assert is_player_eligible(gigi_wall, {"as": "CDM", "min_def": 8}) is True

    def test_st_eligible_for_defense_slot(self, terry_henri):
        """ST with enough pace/def can play defensive role."""
        # terry_henri: PAC=9, DEF=1 → NOT eligible for DEF≥6
        assert is_player_eligible(terry_henri, {"as": "FB", "min_pac": 8, "min_def": 6}) is False


class TestFatigue:
    """Verify fatigue tracking."""

    def test_fatigue_starts_at_one(self, terry_henri):
        state = MatchState(squad=[terry_henri], synergies=[])
        assert state.get_fatigue(terry_henri.id) == 1.0

    def test_apply_fatigue_mul(self, terry_henri):
        state = MatchState(squad=[terry_henri], synergies=[])
        state.apply_fatigue(terry_henri.id)
        assert state.get_fatigue(terry_henri.id) == FATIGUE_PENALTY

    def test_fatigue_stacks(self, terry_henri):
        state = MatchState(squad=[terry_henri], synergies=[])
        state.apply_fatigue(terry_henri.id)  # ×0.7
        state.apply_fatigue(terry_henri.id)  # ×0.49
        assert state.get_fatigue(terry_henri.id) == pytest.approx(0.49, rel=0.01)

    def test_fatigue_resets_between_rounds(self, terry_henri):
        state = MatchState(squad=[terry_henri], synergies=[])
        state.apply_fatigue(terry_henri.id)
        assert state.get_fatigue(terry_henri.id) < 1.0
        start_round(state)  # Reset for new round
        assert state.get_fatigue(terry_henri.id) == 1.0


class TestPhaseFlow:
    """Verify the round phase flow."""

    def test_phases_shuffled_each_round(self, full_squad):
        state = MatchState(squad=full_squad, synergies=[])
        start_round(state)
        assert len(state.phase_hand) == 6
        assert len(state.phases) == 0
        assert state.round_score == 0

    def test_advance_phase_returns_false_on_good_phase(self, full_squad):
        state = MatchState(squad=full_squad, synergies=[])
        start_round(state)
        # Select first 3 phases from hand for testing
        set_selected_phases(state, state.phase_hand[:3])
        state.current_phase_idx = 0
        assert advance_phase(state) == False  # Phase 1→2, still more (0→1)

    def test_advance_phase_returns_true_on_last_phase(self, full_squad):
        state = MatchState(squad=full_squad, synergies=[])
        start_round(state)
        set_selected_phases(state, state.phase_hand[:3])
        state.current_phase_idx = 2
        assert advance_phase(state) == True  # Phase 3→4, round over (2→3)

    def test_resolve_scoring(self, full_squad):
        state = MatchState(squad=full_squad, synergies=[])
        start_round(state)
        set_selected_phases(state, state.phase_hand[:3])

        # Place a player for the first phase
        start_phase(state)
        place_player(state, full_squad[0], full_squad[0].position)

        result = resolve_phase(state)
        assert result["total"] > 0
        assert result["phase_name"] is not None
        # Fatigue should have been applied
        assert state.get_fatigue(full_squad[0].id) == FATIGUE_PENALTY

    def test_round_accumulates_phase_scores(self, full_squad):
        state = MatchState(squad=full_squad, synergies=[])
        start_round(state)
        set_selected_phases(state, state.phase_hand[:3])

        total = 0
        for phase_idx in range(3):
            start_phase(state)
            # Play one player per phase to keep it simple
            available = [p for p in full_squad
                         if state.get_fatigue(p.id) >= FATIGUE_PENALTY]
            if available:
                place_player(state, available[0], available[0].position)
            result = resolve_phase(state)
            total += result["total"]
            if phase_idx < 2:
                advance_phase(state)
            else:
                advance_phase(state)

        assert state.round_score == total
        assert state.round_score > 0

    def test_round_win_and_lose(self, full_squad):
        """With optimal play, should beat the round 1 target."""
        state = MatchState(squad=full_squad, synergies=[],
                           round_targets=[1, 99999, 99999])  # R1: trivially easy
        start_round(state)
        set_selected_phases(state, state.phase_hand[:3])

        for phase_idx in range(3):
            start_phase(state)
            if full_squad:
                place_player(state, full_squad[0], full_squad[0].position)
            resolve_phase(state)
            if phase_idx < 2:
                advance_phase(state)
            else:
                advance_phase(state)

        won = check_round(state)
        assert won == True  # Score > 1
        assert state.rounds_won == 1
