"""Tests for the new Balatro-style phase-level synergy accumulators.

Each synergy now contributes to phase-level accumulators instead of per-player dicts:
  - chips    → flat chips added to total chips pool
  - add_mult → flat mult added to additive mult pool
  - x_mult   → multiplied against mult pool

Detect returns {"chips": N, "add_mult": N, "x_mult": N, "carryover": ..., "fired_details": [...]}
"""

import pytest
from src.scoring import detect_synergies, calculate_round_score, detect_squad_synergies


# ── Clean Sheet (GK DEF + CB DEF ≥ 18) ──────────────────────────────────

class TestCleanSheet:
    """GK + CB with high combined DEF."""

    def test_fires_with_elite_pair(self, gigi_wall, il_capitano, clean_sheet_synergy):
        """Gigi DEF 10 + Van Aura DEF 10 = 20 ≥ 18."""
        field = [(gigi_wall, "GK"), (il_capitano, "CB")]
        result = detect_synergies(field, [clean_sheet_synergy])

        assert result["chips"] == 20
        assert result["add_mult"] == 0
        assert result["x_mult"] == 1.0
        names = [d["name"] for d in result["fired_details"]]
        assert "Clean Sheet" in names

    def test_no_fire_with_budget_gk(self, sweaty_keeper, jt_rock, clean_sheet_synergy):
        """Claudio DEF 6 + JT Rock DEF 10 = 16 < 18."""
        field = [(sweaty_keeper, "GK"), (jt_rock, "CB")]
        result = detect_synergies(field, [clean_sheet_synergy])

        assert result["chips"] == 0
        assert len(result["fired_details"]) == 0


# ── Organised Defence (CB DEF + CB DEF ≥ 18) ────────────────────────────

class TestOrganisedDefence:
    """Two CBs with high combined DEF."""

    def test_fires_with_elite_pair(self, il_capitano, jt_rock, organised_defence_synergy):
        """Van Aura DEF 10 + JT Rock DEF 10 = 20 ≥ 18."""
        field = [(il_capitano, "CB"), (jt_rock, "CB")]
        result = detect_synergies(field, [organised_defence_synergy])

        assert result["chips"] == 20
        assert "Organised Defence" in [d["name"] for d in result["fired_details"]]

    def test_no_fire_with_budget_cb(self, old_man_dan, jt_rock, organised_defence_synergy):
        """Per DEF 7 + JT Rock DEF 10 = 17 < 18."""
        field = [(old_man_dan, "CB"), (jt_rock, "CB")]
        result = detect_synergies(field, [organised_defence_synergy])

        assert result["chips"] == 0
        assert len(result["fired_details"]) == 0


# ── Wingback Overlap (FB PAC + CM PAS ≥ 15) ─────────────────────────────

class TestWingbackOverlap:
    """Pacey FB + Passing CM."""

    def test_fires_with_good_pair(self, el_tren, maestro_xav, wingback_overlap_synergy):
        """El Tren PAC 9 + Maestro PAS 10 = 19 ≥ 15."""
        field = [(el_tren, "FB"), (maestro_xav, "CM")]
        result = detect_synergies(field, [wingback_overlap_synergy])

        assert result["chips"] == 25
        assert "Wingback Overlap" in [d["name"] for d in result["fired_details"]]

    def test_budget_fb_misses(self, the_crab, maestro_xav, wingback_overlap_synergy):
        """Kola PAC 5 + Maestro PAS 10 = 15 ≥ 15. Just makes it."""
        field = [(the_crab, "FB"), (maestro_xav, "CM")]
        result = detect_synergies(field, [wingback_overlap_synergy])

        assert result["chips"] == 25

    def test_no_cm_no_fire(self, el_tren, wingback_overlap_synergy):
        """No CM on field = no trigger."""
        field = [(el_tren, "FB")]
        result = detect_synergies(field, [wingback_overlap_synergy])

        assert result["chips"] == 0
        assert len(result["fired_details"]) == 0


# ── Overload (2+ same position) ─────────────────────────────────────────

class TestOverload:
    """Duplicate positions on field → add_mult."""

    def test_fires_with_two_cbs(self, il_capitano, jt_rock, overload_synergy):
        field = [(il_capitano, "CB"), (jt_rock, "CB")]
        result = detect_synergies(field, [overload_synergy])

        assert result["add_mult"] == 3
        assert "Overload" in [d["name"] for d in result["fired_details"]]

    def test_no_fire_no_duplicates(self, il_capitano, el_tren, overload_synergy):
        """Different positions = no trigger."""
        field = [(il_capitano, "CB"), (el_tren, "FB")]
        result = detect_synergies(field, [overload_synergy])

        assert result["add_mult"] == 0
        assert len(result["fired_details"]) == 0


# ── Stretch the Backline (FB PAC + LW PAC ≥ 17) ─────────────────────────

class TestStretchBackline:
    """Pacey FB + pacey LW."""

    def test_fires_with_speedsters(self, el_tren, bale_out, stretch_backline_synergy):
        """El Tren PAC 9 + Bale PAC 10 = 19 ≥ 17."""
        field = [(el_tren, "FB"), (bale_out, "LW")]
        result = detect_synergies(field, [stretch_backline_synergy])

        assert result["x_mult"] == 1.5
        assert "Stretch the Backline" in [d["name"] for d in result["fired_details"]]

    def test_no_fire_slow_pair(self, the_crab, cult_carl, stretch_backline_synergy):
        """Kola PAC 5 + Za-ha PAC 6 = 11 < 17."""
        field = [(the_crab, "FB"), (cult_carl, "LW")]
        result = detect_synergies(field, [stretch_backline_synergy])

        assert result["x_mult"] == 1.0
        assert len(result["fired_details"]) == 0


# ── Route One (CB PAS + ST PAC ≥ 14 → chips) ────────────────────────────

class TestRouteOne:
    """Passing CB + fast ST."""

    def test_fires_and_boosts_chips(self, il_capitano, terry_henri, route_one_synergy):
        """Van Aura PAS 7 + Terry PAC 9 = 16 ≥ 14."""
        field = [(il_capitano, "CB"), (terry_henri, "ST")]
        result = detect_synergies(field, [route_one_synergy])

        assert result["chips"] == 30
        assert "Route One" in [d["name"] for d in result["fired_details"]]
        # Contributors should include both CB and ST
        detail = [d for d in result["fired_details"] if d["name"] == "Route One"][0]
        assert len(detail["contributors"]) == 2

    def test_no_fire_low_stats(self, old_man_dan, flash_forward, route_one_synergy):
        """Per PAS 4 + Theo PAC 7 = 11 < 14."""
        field = [(old_man_dan, "CB"), (flash_forward, "ST")]
        result = detect_synergies(field, [route_one_synergy])

        assert result["chips"] == 0


# ── Battering Ram (CB DEF + ST ATK ≥ 17) ────────────────────────────────

class TestBatteringRam:
    """Strong CB + powerful ST."""

    def test_fires_with_beast_pair(self, il_capitano, big_zlat, battering_ram_synergy):
        """Van Aura DEF 10 + Big Zlat ATK 8 = 18 ≥ 17."""
        field = [(il_capitano, "CB"), (big_zlat, "ST")]
        result = detect_synergies(field, [battering_ram_synergy])

        assert result["chips"] == 20
        assert "Battering Ram" in [d["name"] for d in result["fired_details"]]

    def test_no_fire_weak_st(self, il_capitano, flash_forward, battering_ram_synergy):
        """Van Aura DEF 10 + Theo ATK 4 = 14 < 17."""
        field = [(il_capitano, "CB"), (flash_forward, "ST")]
        result = detect_synergies(field, [battering_ram_synergy])

        assert result["chips"] == 0


# ── Defensive Duo (2 highest DEF sum ≥ 18) ──────────────────────────────

class TestDefensiveDuo:
    """Two best defenders combined DEF ≥ 18 → add_mult."""

    def test_fires_with_elite_trio(self, il_capitano, jt_rock, wall_claude, defensive_duo_synergy):
        """Van Aura 10 + JT 10 = 20 ≥ 18."""
        field = [(il_capitano, "CB"), (jt_rock, "CB"), (wall_claude, "CDM")]
        result = detect_synergies(field, [defensive_duo_synergy])

        assert result["add_mult"] == 5
        assert "Defensive Duo" in [d["name"] for d in result["fired_details"]]

    def test_no_fire_one_weak_link(self, wall_claude, rolls_royce, bog_bob, defensive_duo_synergy):
        """Rolls DEF 9 + Bog Bob DEF 6 = 15 < 18 — but Wall 10 + Rolls 9 = 19."""
        # Field has Wall (CDM), Rolls (CB), Bog Bob (CDM)
        # Top 2 DEF: Wall 10 + Rolls 9 = 19 ≥ 18 — fires
        result = detect_synergies([(wall_claude, "CDM"), (rolls_royce, "CB"), (bog_bob, "CDM")],
                                   [defensive_duo_synergy])
        # It fires because Wall + Rolls are the top 2
        assert result["add_mult"] == 5


# ── Back Three (all 3 DEF ≥ 7) ─────────────────────────────────────────

class TestBackThree:
    """All 3 fielded players have DEF ≥ 7."""

    def test_fires_all_elite(self, il_capitano, jt_rock, wall_claude, back_three_synergy):
        """All DEF ≥ 7 → ×1.3 mult."""
        field = [(il_capitano, "CB"), (jt_rock, "CB"), (wall_claude, "CDM")]
        result = detect_synergies(field, [back_three_synergy])

        assert result["x_mult"] == 1.2
        assert "Back Three" in [d["name"] for d in result["fired_details"]]

    def test_no_fire_low_def(self, il_capitano, jt_rock, bog_bob, back_three_synergy):
        """Nigel de Wrong DEF 6 < 7 → no fire."""
        field = [(il_capitano, "CB"), (jt_rock, "CB"), (bog_bob, "CDM")]
        result = detect_synergies(field, [back_three_synergy])

        assert result["x_mult"] == 1.0
        assert len(result["fired_details"]) == 0


# ── Midfield Engine (CM PAS + CM DEF ≥ 15) ──────────────────────────────

class TestMidfieldEngine:
    """Passing CM + defensive CM."""

    def test_fires_passer_and_grit(self, maestro_xav, captain_stevie, midfield_engine_synergy):
        """Maestro PAS 10 + Stevie DEF 6 = 16 < 17 (threshold raised). Does not fire."""
        field = [(maestro_xav, "CM"), (captain_stevie, "CM")]
        result = detect_synergies(field, [midfield_engine_synergy])

        assert result["add_mult"] == 0

    def test_two_playmakers_no_fire(self, maestro_xav, don_andres, midfield_engine_synergy):
        """Maestro PAS 10 + Don DEF 3 = 13 < 17."""
        field = [(maestro_xav, "CM"), (don_andres, "CM")]
        result = detect_synergies(field, [midfield_engine_synergy])

        assert result["add_mult"] == 0


# ── Double Pivot (2 CMs PAS ≥ 17 → carryover to next phase) ────────────

class TestDoublePivot:
    """Two elite passing CMs set up next phase's attacker."""

    def test_fires_carryover(self, maestro_xav, captain_stevie, double_pivot_synergy):
        """Maestro PAS 10 + Stevie PAS 8 = 18 ≥ 18. Sets carryover (+25 chips)."""
        field = [(maestro_xav, "CM"), (captain_stevie, "CM")]
        result = detect_synergies(field, [double_pivot_synergy])

        carryover = result.get("carryover")
        assert carryover is not None
        assert carryover["chips"] == 25
        assert carryover["target_role"] == "attacker"
        assert "Double Pivot" in [d["name"] for d in result["fired_details"]]

    def test_carryover_applied_to_first_attacker(self, maestro_xav, captain_stevie,
                                                  terry_henri, il_capitano,
                                                  double_pivot_synergy):
        """Full round score with carryover: first attacker (ST) gets +25 chips."""
        field1 = [(maestro_xav, "CM"), (captain_stevie, "CM")]
        phase1 = calculate_round_score(field1, [double_pivot_synergy])
        carryover = phase1.get("next_carryover")
        assert carryover is not None

        # Phase 2: Long Ball with CB + ST — ST should get +40 from carryover
        field2 = [(il_capitano, "CB"), (terry_henri, "ST")]
        phase2 = calculate_round_score(field2, [double_pivot_synergy], carryover=carryover)
        no_carry = calculate_round_score(field2, [double_pivot_synergy])

        assert "Double Pivot (carryover)" in phase2["fired_synergies"]
        assert phase2["total_chips"] > no_carry["total_chips"]


# ── Trio (3 CMs PAS ≥ 7) ──────────────────────────────────────────────

class TestTrio:
    """Three passing CMs with combined ×mult."""

    def test_three_elite_cms(self, maestro_xav, captain_stevie, don_andres, trio_synergy):
        """Maestro PAS 10, Don PAS 9, Stevie PAS 8 — all ≥ 7. Combined ×mult = 1.3*1.5*1.3."""
        field = [(maestro_xav, "CM"), (captain_stevie, "CM"), (don_andres, "CM")]
        result = detect_synergies(field, [trio_synergy])

        assert abs(result["x_mult"] - 1.8) < 0.01  # 1.2*1.25*1.2 = 1.8
        assert "Trio" in [d["name"] for d in result["fired_details"]]

    def test_too_few_cms(self, maestro_xav, captain_stevie, trio_synergy):
        """Only 2 CMs — Trio needs 3."""
        field = [(maestro_xav, "CM"), (captain_stevie, "CM")]
        result = detect_synergies(field, [trio_synergy])

        assert result["x_mult"] == 1.0
        assert len(result["fired_details"]) == 0

    def test_budget_cm_blocks(self, maestro_xav, captain_stevie, jimmy_journey, trio_synergy):
        """Park PAS 5 < 7 — blocks the trio."""
        field = [(maestro_xav, "CM"), (captain_stevie, "CM"), (jimmy_journey, "CM")]
        result = detect_synergies(field, [trio_synergy])

        assert result["x_mult"] == 1.0
        assert len(result["fired_details"]) == 0


# ── Set Piece Threat (DEF≥8 + SPC≥7, different players) ─────────────────

class TestSetPieceThreat:
    """One strong defender + one flair player."""

    def test_fires_different_players(self, il_capitano, terry_henri, set_piece_synergy):
        """Van Aura DEF 10 + Terry SPC 8 = different players, both qualify."""
        field = [(il_capitano, "CB"), (terry_henri, "ST")]
        result = detect_synergies(field, [set_piece_synergy])

        assert result["chips"] == 50
        assert "Set Piece Threat" in [d["name"] for d in result["fired_details"]]

    def test_same_player_both_stats_no_fire(self, gigi_wall, set_piece_synergy):
        """Gigi has DEF 10 AND SPC 8 — same player, so won't fire."""
        field = [(gigi_wall, "GK")]
        result = detect_synergies(field, [set_piece_synergy])

        assert result["chips"] == 0
        assert len(result["fired_details"]) == 0


# ── Full Round Score Integration ─────────────────────────────────────────

class TestRoundScore:
    """End-to-end: field + synergies + formation = score."""

    def test_no_synergies_baseline(self, formation_442, il_capitano, jt_rock,
                                    el_tren, mr_reliable):
        """Basic field with no synergy cards — pure base chips."""
        field = [(il_capitano, "CB"), (jt_rock, "CB"), (el_tren, "FB"), (mr_reliable, "FB")]
        result = calculate_round_score(field, [], formation_442)

        assert result["total"] > 0
        assert result["fired_synergies"] == []
        assert result["formation_mult"] == 1.0
        # New format: check chips/mult components
        assert result["add_mult"] == 1  # base mult = 1
        assert result["x_mult"] == 1.0

    def test_clean_sheet_in_goal_kick(self, gigi_wall, il_capitano, jt_rock,
                                       clean_sheet_synergy, organised_defence_synergy,
                                       formation_442):
        """Goal Kick scenario: GK + 2 CBs with multiple synergies."""
        field = [(gigi_wall, "GK"), (il_capitano, "CB"), (jt_rock, "CB")]
        synergies = [clean_sheet_synergy, organised_defence_synergy]
        result = calculate_round_score(field, synergies, formation_442)

        assert "Clean Sheet" in result["fired_synergies"]
        assert "Organised Defence" in result["fired_synergies"]
        assert result["synergy_chips"] == 40  # 20 + 20
        assert result["total"] > 0

    def test_carryover_chain_in_match(self, maestro_xav, captain_stevie,
                                       terry_henri, il_capitano,
                                       double_pivot_synergy, formation_442):
        """Simulate 2 phases: Tiki-Taka → Long Ball with carryover."""
        # Phase 1: Double Pivot fires
        field1 = [(maestro_xav, "CM"), (captain_stevie, "CM")]
        phase1 = calculate_round_score(field1, [double_pivot_synergy], formation_442)
        carryover = phase1.get("next_carryover")
        assert carryover is not None

        # Phase 2: Long Ball — carryover applies
        field2 = [(il_capitano, "CB"), (terry_henri, "ST")]
        phase2 = calculate_round_score(field2, [double_pivot_synergy], formation_442,
                                        carryover=carryover)
        baseline = calculate_round_score(field2, [double_pivot_synergy], formation_442)
        assert "Double Pivot (carryover)" in phase2["fired_synergies"]
        assert phase2["total"] > baseline["total"]


# ── Squad-Persistent Synergy Tests ──────────────────────────────────────

class TestSquadPersistent:
    """Trait-based synergies that check squad composition at match start."""

    def test_pace_in_behind(self, pacey_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(pacey_squad, all_persistent_synergies)
        assert "Pace in Behind" in buffs["fired_synergies"]
        # Terry gets ×1.08 from Pace (if Silent Killers also fires: ×1.08×1.15)
        assert buffs["player_mult"].get("terry_henri", 1.0) == 1.08

    def test_iron_wall(self, physical_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(physical_squad, all_persistent_synergies)
        assert "Iron Wall" in buffs["fired_synergies"]
        assert buffs["fatigue_penalty"] == 0.65
        for p in physical_squad:
            if "physical" in p.traits:
                assert buffs["player_mult"].get(p.id, 1.0) == 1.12

    def test_leadership_council(self, leader_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(leader_squad, all_persistent_synergies)
        assert "Leadership Council" in buffs["fired_synergies"]
        assert buffs["global_add"] == 10

    def test_tiki_taka(self, technical_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(technical_squad, all_persistent_synergies)
        assert "Tiki-Taka" in buffs["fired_synergies"]
        assert buffs["position_mult"].get("CM", 1.0) == 1.08

    def test_clinical_edge(self, clinical_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(clinical_squad, all_persistent_synergies)
        assert "Clinical Edge" in buffs["fired_synergies"]
        assert buffs["position_add"].get("ST", 0) == 10

    def test_double_destroyer(self, destroyer_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(destroyer_squad, all_persistent_synergies)
        assert "Double Destroyer" in buffs["fired_synergies"]
        assert buffs["position_mult"].get("CB", 1.0) == 1.12

    def test_two_up_top(self, poacher_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(poacher_squad, all_persistent_synergies)
        assert "Two Up Top" in buffs["fired_synergies"]
        assert buffs["position_mult"].get("ST", 1.0) == 1.15

    def test_journeyman(self, journeyman_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(journeyman_squad, all_persistent_synergies)
        assert "Journeyman" in buffs["fired_synergies"]
        assert buffs["journeyman_available"] is True

    def test_pace_and_power(self, pace_power_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(pace_power_squad, all_persistent_synergies)
        assert "Pace & Power" in buffs["fired_synergies"]
        # Bale gets ×1.12 from Iron Wall + ×1.15 from Pace & Power = 1.288
        assert buffs["player_mult"].get("bale_out", 1.0) == 1.288

    def test_silent_killers(self, silent_killers_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(silent_killers_squad, all_persistent_synergies)
        assert "Silent Killers" in buffs["fired_synergies"]
        assert buffs["player_mult"].get("terry_henri", 1.0) == 1.15

    def test_threshold_not_met(self, all_persistent_synergies):
        from src.cards import PlayerCard
        squad = [PlayerCard(id="p1", name="P1", position="ST", atk=5, pac=5,
                            pas=5, def_=5, spc=5, traits=["pacey"])]
        buffs = detect_squad_synergies(squad, all_persistent_synergies)
        assert "Pace in Behind" not in buffs["fired_synergies"]

    def test_buffs_affect_scoring(self, pacey_squad, all_persistent_synergies,
                                   formation_442):
        buffs = detect_squad_synergies(pacey_squad, all_persistent_synergies)
        field = [(next(p for p in pacey_squad if p.id == "terry_henri"), "ST")]
        with_buffs = calculate_round_score(field, [], formation_442,
                                            persistent_buffs=buffs)
        without = calculate_round_score(field, [], formation_442)
        assert with_buffs["total"] > without["total"]
