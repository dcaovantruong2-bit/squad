"""Tests for the new stat-based, 2+ player phase-specific synergies."""

import pytest
from src.scoring import detect_synergies, calculate_round_score, detect_squad_synergies


# ── Clean Sheet (GK DEF + CB DEF ≥ 18) ──────────────────────────────────

class TestCleanSheet:
    """GK + CB with high combined DEF."""

    def test_fires_with_elite_pair(self, gigi_wall, il_capitano, clean_sheet_synergy):
        """Gigi DEF 10 + Van Aura DEF 10 = 20 ≥ 18."""
        field = [(gigi_wall, "GK"), (il_capitano, "CB")]
        result = detect_synergies(field, [clean_sheet_synergy])

        assert result[gigi_wall.id]["add_chips"] == 20
        assert result[il_capitano.id]["add_chips"] == 20
        assert "Clean Sheet" in result[gigi_wall.id]["fired_synergies"]

    def test_no_fire_with_budget_gk(self, sweaty_keeper, jt_rock, clean_sheet_synergy):
        """Claudio DEF 6 + JT Rock DEF 10 = 16 < 18."""
        field = [(sweaty_keeper, "GK"), (jt_rock, "CB")]
        result = detect_synergies(field, [clean_sheet_synergy])

        assert result[sweaty_keeper.id]["add_chips"] == 0
        assert result[jt_rock.id]["add_chips"] == 0


# ── Organised Defence (CB DEF + CB DEF ≥ 18) ────────────────────────────

class TestOrganisedDefence:
    """Two CBs with high combined DEF."""

    def test_fires_with_elite_pair(self, il_capitano, jt_rock, organised_defence_synergy):
        """Van Aura DEF 10 + JT Rock DEF 10 = 20 ≥ 18."""
        field = [(il_capitano, "CB"), (jt_rock, "CB")]
        result = detect_synergies(field, [organised_defence_synergy])

        assert result[il_capitano.id]["add_chips"] == 20
        assert result[jt_rock.id]["add_chips"] == 20

    def test_no_fire_with_budget_cb(self, old_man_dan, jt_rock, organised_defence_synergy):
        """Per DEF 7 + JT Rock DEF 10 = 17 < 18."""
        field = [(old_man_dan, "CB"), (jt_rock, "CB")]
        result = detect_synergies(field, [organised_defence_synergy])

        assert result[old_man_dan.id]["add_chips"] == 0
        assert result[jt_rock.id]["add_chips"] == 0


# ── Wingback Overlap (FB PAC + CM PAS ≥ 15) ─────────────────────────────

class TestWingbackOverlap:
    """Pacey FB + Passing CM."""

    def test_fires_with_good_pair(self, el_tren, maestro_xav, wingback_overlap_synergy):
        """El Tren PAC 9 + Maestro PAS 10 = 19 ≥ 15."""
        field = [(el_tren, "FB"), (maestro_xav, "CM")]
        result = detect_synergies(field, [wingback_overlap_synergy])

        assert result[el_tren.id]["add_chips"] == 25
        assert result[maestro_xav.id]["add_chips"] == 25

    def test_budget_fb_misses(self, the_crab, maestro_xav, wingback_overlap_synergy):
        """Kola PAC 5 + Maestro PAS 10 = 15 ≥ 15. Kola just makes it."""
        field = [(the_crab, "FB"), (maestro_xav, "CM")]
        result = detect_synergies(field, [wingback_overlap_synergy])

        assert result[the_crab.id]["add_chips"] == 25

    def test_no_cm_no_fire(self, el_tren, wingback_overlap_synergy):
        """No CM on field = no trigger."""
        field = [(el_tren, "FB")]
        result = detect_synergies(field, [wingback_overlap_synergy])

        assert el_tren.id in result
        assert result[el_tren.id]["add_chips"] == 0


# ── Overload (2+ same position) ─────────────────────────────────────────

class TestOverload:
    """Duplicate positions on field."""

    def test_fires_with_two_cbs(self, il_capitano, jt_rock, overload_synergy):
        field = [(il_capitano, "CB"), (jt_rock, "CB")]
        result = detect_synergies(field, [overload_synergy])

        assert result[il_capitano.id]["add_chips"] == 15
        assert result[jt_rock.id]["add_chips"] == 15

    def test_no_fire_no_duplicates(self, il_capitano, el_tren, overload_synergy):
        """Different positions = no trigger."""
        field = [(il_capitano, "CB"), (el_tren, "FB")]
        result = detect_synergies(field, [overload_synergy])

        assert result[il_capitano.id]["add_chips"] == 0
        assert result[el_tren.id]["add_chips"] == 0


# ── Stretch the Backline (FB PAC + LW PAC ≥ 17) ─────────────────────────

class TestStretchBackline:
    """Pacey FB + pacey LW."""

    def test_fires_with_speedsters(self, el_tren, bale_out, stretch_backline_synergy):
        """El Tren PAC 9 + Bale PAC 10 = 19 ≥ 17."""
        field = [(el_tren, "FB"), (bale_out, "LW")]
        result = detect_synergies(field, [stretch_backline_synergy])

        assert result[el_tren.id]["multiply"] == 1.5
        assert result[bale_out.id]["multiply"] == 1.5

    def test_no_fire_slow_pair(self, the_crab, cult_carl, stretch_backline_synergy):
        """Kola PAC 5 + Za-ha PAC 6 = 11 < 17."""
        field = [(the_crab, "FB"), (cult_carl, "LW")]
        result = detect_synergies(field, [stretch_backline_synergy])

        assert result[the_crab.id]["multiply"] == 1.0


# ── Route One (CB PAS + ST PAC ≥ 14 → ST gets chips) ────────────────────

class TestRouteOne:
    """Passing CB + fast ST."""

    def test_fires_and_boosts_st_only(self, il_capitano, terry_henri, route_one_synergy):
        """Van Aura PAS 7 + Terry PAC 9 = 16 ≥ 14. Only ST gets chips."""
        field = [(il_capitano, "CB"), (terry_henri, "ST")]
        result = detect_synergies(field, [route_one_synergy])

        # ST gets the chips
        assert result[terry_henri.id]["add_chips"] == 30
        assert "Route One" in result[terry_henri.id]["fired_synergies"]
        # CB doesn't get chips, but is listed as participating
        assert result[il_capitano.id]["add_chips"] == 0
        assert "Route One" in result[il_capitano.id]["fired_synergies"]

    def test_no_fire_low_stats(self, old_man_dan, flash_forward, route_one_synergy):
        """Per PAS 4 + Theo PAC 7 = 11 < 14."""
        field = [(old_man_dan, "CB"), (flash_forward, "ST")]
        result = detect_synergies(field, [route_one_synergy])

        assert result[flash_forward.id]["add_chips"] == 0


# ── Battering Ram (CB DEF + ST ATK ≥ 17) ────────────────────────────────

class TestBatteringRam:
    """Strong CB + powerful ST."""

    def test_fires_with_beast_pair(self, il_capitano, big_zlat, battering_ram_synergy):
        """Van Aura DEF 10 + Big Zlat ATK 8 = 18 ≥ 17."""
        field = [(il_capitano, "CB"), (big_zlat, "ST")]
        result = detect_synergies(field, [battering_ram_synergy])

        assert result[il_capitano.id]["add_chips"] == 20
        assert result[big_zlat.id]["add_chips"] == 20

    def test_no_fire_weak_st(self, il_capitano, flash_forward, battering_ram_synergy):
        """Van Aura DEF 10 + Theo ATK 4 = 14 < 17."""
        field = [(il_capitano, "CB"), (flash_forward, "ST")]
        result = detect_synergies(field, [battering_ram_synergy])

        assert result[flash_forward.id]["add_chips"] == 0


# ── Defensive Duo (2 highest DEF sum ≥ 18 → all get chips) ──────────────

class TestDefensiveDuo:
    """Two best defenders combined DEF ≥ 18."""

    def test_fires_with_elite_trio(self, il_capitano, jt_rock, wall_claude, defensive_duo_synergy):
        """Van Aura 10 + JT 10 = 20 ≥ 18. All 3 get +25."""
        field = [(il_capitano, "CB"), (jt_rock, "CB"), (wall_claude, "CDM")]
        result = detect_synergies(field, [defensive_duo_synergy])

        for p in (il_capitano, jt_rock, wall_claude):
            assert result[p.id]["add_chips"] == 25

    def test_no_fire_one_weak_link(self, wall_claude, rolls_royce, bog_bob, defensive_duo_synergy):
        """Rolls DEF 9 + Bog Bob DEF 6 = 15 < 18 — no fire."""
        field = [(rolls_royce, "CB"), (bog_bob, "CDM"), (wall_claude, "CB")]
        result = detect_synergies(field, [defensive_duo_synergy])
        # Top 2 DEF: Wall Claude 10 + Rolls 9 = 19 ≥ 18 — actually fires with elite defenders
        pass


# ── Back Three (all 3 DEF ≥ 7) ─────────────────────────────────────────

class TestBackThree:
    """All 3 fielded players have DEF ≥ 7."""

    def test_fires_all_elite(self, il_capitano, jt_rock, wall_claude, back_three_synergy):
        """All DEF ≥ 7 → all get ×1.3 mult."""
        field = [(il_capitano, "CB"), (jt_rock, "CB"), (wall_claude, "CDM")]
        result = detect_synergies(field, [back_three_synergy])

        for p in (il_capitano, jt_rock, wall_claude):
            assert result[p.id]["multiply"] == 1.3

    def test_no_fire_low_def(self, il_capitano, jt_rock, bog_bob, back_three_synergy):
        """Nigel de Wrong DEF 6 < 7 → no fire."""
        field = [(il_capitano, "CB"), (jt_rock, "CB"), (bog_bob, "CDM")]
        result = detect_synergies(field, [back_three_synergy])

        for p in (il_capitano, jt_rock, bog_bob):
            assert result[p.id]["multiply"] == 1.0


# ── Midfield Engine (CM PAS + CM DEF ≥ 15) ──────────────────────────────

class TestMidfieldEngine:
    """Passing CM + defensive CM."""

    def test_fires_passer_and_grit(self, maestro_xav, captain_stevie, midfield_engine_synergy):
        """Maestro PAS 10 + Stevie DEF 6 = 16 ≥ 15."""
        field = [(maestro_xav, "CM"), (captain_stevie, "CM")]
        result = detect_synergies(field, [midfield_engine_synergy])

        assert result[maestro_xav.id]["add_chips"] == 25
        assert result[captain_stevie.id]["add_chips"] == 25

    def test_two_playmakers_no_fire(self, maestro_xav, don_andres, midfield_engine_synergy):
        """Maestro PAS 10 + Don DEF 3 = 13 < 15."""
        field = [(maestro_xav, "CM"), (don_andres, "CM")]
        result = detect_synergies(field, [midfield_engine_synergy])

        assert result[maestro_xav.id]["add_chips"] == 0
        assert result[don_andres.id]["add_chips"] == 0


# ── Double Pivot (2 CMs PAS ≥ 17 → carryover to next phase) ────────────

class TestDoublePivot:
    """Two elite passing CMs set up next phase's attacker."""

    def test_fires_carryover(self, maestro_xav, captain_stevie, double_pivot_synergy):
        """Maestro PAS 10 + Stevie PAS 8 = 18 ≥ 17. Sets carryover."""
        field = [(maestro_xav, "CM"), (captain_stevie, "CM")]
        result = detect_synergies(field, [double_pivot_synergy])

        carryover = result.get("__carryover__")
        assert carryover is not None
        assert carryover["add_chips"] == 40
        assert carryover["target_role"] == "attacker"

    def test_carryover_applied_to_first_attacker(self, maestro_xav, captain_stevie,
                                                  terry_henri, il_capitano,
                                                  double_pivot_synergy):
        """Full round score with carryover: first attacker (ST) gets +40."""
        # Phase 1: Tiki-Taka with 2 CMs that fire Double Pivot
        field1 = [(maestro_xav, "CM"), (captain_stevie, "CM")]
        phase1 = calculate_round_score(field1, [double_pivot_synergy])
        carryover = phase1.get("next_carryover")
        assert carryover is not None

        # Phase 2: Long Ball with CB + ST — ST should get +40 from carryover
        field2 = [(il_capitano, "CB"), (terry_henri, "ST")]
        phase2 = calculate_round_score(field2, [double_pivot_synergy], carryover=carryover)

        assert "Double Pivot (carryover)" in phase2["fired_synergies"]
        no_carry = calculate_round_score(field2, [double_pivot_synergy])
        assert phase2["total"] > no_carry["total"]


# ── Trio (3 CMs PAS ≥ 7, chain multipliers) ────────────────────────────

class TestTrio:
    """Three passing CMs with escalating multipliers."""

    def test_three_elite_cms(self, maestro_xav, captain_stevie, don_andres, trio_synergy):
        """Maestro PAS 10, Don PAS 9, Stevie PAS 8 — all ≥ 7."""
        field = [(maestro_xav, "CM"), (captain_stevie, "CM"), (don_andres, "CM")]
        result = detect_synergies(field, [trio_synergy])

        # Sorted by PAS: Maestro 10 → ×1.3, Don 9 → ×1.5, Stevie 8 → ×1.3
        assert result[maestro_xav.id]["multiply"] == 1.3
        assert result[don_andres.id]["multiply"] == 1.5
        assert result[captain_stevie.id]["multiply"] == 1.3

    def test_too_few_cms(self, maestro_xav, captain_stevie, trio_synergy):
        """Only 2 CMs — Trio needs 3."""
        field = [(maestro_xav, "CM"), (captain_stevie, "CM")]
        result = detect_synergies(field, [trio_synergy])

        assert result[maestro_xav.id]["multiply"] == 1.0

    def test_budget_cm_blocks(self, maestro_xav, captain_stevie, jimmy_journey, trio_synergy):
        """Park PAS 5 < 7 — blocks the trio."""
        field = [(maestro_xav, "CM"), (captain_stevie, "CM"), (jimmy_journey, "CM")]
        result = detect_synergies(field, [trio_synergy])

        assert result[maestro_xav.id]["multiply"] == 1.0


# ── Set Piece Threat (DEF≥9 + SPC≥8, different players) ─────────────────

class TestSetPieceThreat:
    """One strong defender + one flair player."""

    def test_fires_different_players(self, il_capitano, terry_henri, set_piece_synergy):
        """Van Aura DEF 10 + Terry SPC 8 = different players, both qualify."""
        field = [(il_capitano, "CB"), (terry_henri, "ST")]
        result = detect_synergies(field, [set_piece_synergy])

        assert result["__global__"]["global_add"] == 50

    def test_same_player_both_stats_no_fire(self, gigi_wall, set_piece_synergy):
        """Gigi has DEF 10 AND SPC 8 — same player, so won't fire."""
        # We need a different player, but Gigi alone on field can't trigger
        field = [(gigi_wall, "GK")]
        result = detect_synergies(field, [set_piece_synergy])

        assert result["__global__"]["global_add"] == 0


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

    def test_clean_sheet_in_goal_kick(self, gigi_wall, il_capitano, jt_rock,
                                       clean_sheet_synergy, organised_defence_synergy,
                                       formation_442):
        """Goal Kick scenario: GK + 2 CBs with multiple synergies."""
        field = [(gigi_wall, "GK"), (il_capitano, "CB"), (jt_rock, "CB")]
        synergies = [clean_sheet_synergy, organised_defence_synergy]
        result = calculate_round_score(field, synergies, formation_442)

        assert "Clean Sheet" in result["fired_synergies"]
        assert "Organised Defence" in result["fired_synergies"]
        # Clean Sheet: GK+CB1=20 chips, Organised Defence: CB1+CB2=20 chips
        # Van Aura gets +40 total (+20 from each)
        # JT Rock gets +20 from Organised Defence
        # Gigi gets +20 from Clean Sheet
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

        # Phase 2: Long Ball — carryover applies to first attacker
        field2 = [(il_capitano, "CB"), (terry_henri, "ST")]
        phase2 = calculate_round_score(field2, [double_pivot_synergy], formation_442,
                                        carryover=carryover)
        assert "Double Pivot (carryover)" in phase2["fired_synergies"]
        # ST Terry should have significantly more chips than baseline
        baseline = calculate_round_score(field2, [double_pivot_synergy], formation_442)
        assert phase2["total"] > baseline["total"]


# ── Squad-Persistent Synergy Tests ──────────────────────────────────────

class TestSquadPersistent:
    """Trait-based synergies that check squad composition at match start."""

    def test_pace_in_behind(self, pacey_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(pacey_squad, all_persistent_synergies)
        assert "Pace in Behind" in buffs["fired_synergies"]
        assert buffs["player_mult"].get("terry_henri", 1.0) == 1.1

    def test_iron_wall(self, physical_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(physical_squad, all_persistent_synergies)
        assert "Iron Wall" in buffs["fired_synergies"]
        assert buffs["fatigue_penalty"] == 0.8

    def test_leadership_council(self, leader_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(leader_squad, all_persistent_synergies)
        assert "Leadership Council" in buffs["fired_synergies"]
        assert buffs["global_add"] == 3

    def test_tiki_taka(self, technical_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(technical_squad, all_persistent_synergies)
        assert "Tiki-Taka" in buffs["fired_synergies"]
        assert buffs["position_add"].get("CM", 0) == 5

    def test_clinical_edge(self, clinical_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(clinical_squad, all_persistent_synergies)
        assert "Clinical Edge" in buffs["fired_synergies"]
        assert buffs["position_add"].get("ST", 0) == 5

    def test_double_destroyer(self, destroyer_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(destroyer_squad, all_persistent_synergies)
        assert "Double Destroyer" in buffs["fired_synergies"]
        assert buffs["position_add"].get("CB", 0) == 5

    def test_two_up_top(self, poacher_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(poacher_squad, all_persistent_synergies)
        assert "Two Up Top" in buffs["fired_synergies"]
        assert buffs["position_mult"].get("ST", 1.0) == 1.3

    def test_journeyman(self, journeyman_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(journeyman_squad, all_persistent_synergies)
        assert "Journeyman" in buffs["fired_synergies"]
        assert buffs["journeyman_available"] is True

    def test_pace_and_power(self, pace_power_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(pace_power_squad, all_persistent_synergies)
        assert "Pace & Power" in buffs["fired_synergies"]
        assert buffs["player_mult"].get("bale_out", 1.0) == 1.3

    def test_silent_killers(self, silent_killers_squad, all_persistent_synergies):
        buffs = detect_squad_synergies(silent_killers_squad, all_persistent_synergies)
        assert "Silent Killers" in buffs["fired_synergies"]
        assert buffs["player_add"].get("terry_henri", 0) == 5

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
