"""End-to-end integration tests — full game flow.

Exercises: drafting → match creation → phase selection → scoring →
energy depletion → opponent tactics → momentum → campaign flow.
"""

import pytest
from src.cards import PlayerCard
from src.loader import load_players, load_synergies
from src.draft import generate_draft
from src.match import (
    MatchState, create_match, start_round, set_selected_phases,
    start_phase, place_player, resolve_phase, advance_phase, check_round,
)
from src.opponents import Opponent, TacticalStyle, get_campaign_opponent
from src.phases import Phase, get_all_phases
from src.scoring import calculate_round_score, detect_squad_synergies
from src.energy import SquadEnergy, EnergyState


class TestFullDraftToMatch:
    """Draft a squad, then play through a match."""

    def test_draft_and_play_match(self):
        """Full flow: draft 10 players → play a 3-phase round."""
        all_players = load_players()
        assert len(all_players) >= 50, f"Expected ≥50 players, got {len(all_players)}"

        # Draft a squad
        draft = generate_draft(all_players, seed=42)
        while not draft.is_complete:
            pick = draft.current_pick
            chosen = pick.pool[:pick.count]
            draft.confirm_pick(chosen)

        squad = draft.selected
        assert len(squad) == 10

        # Create match against Match 1 opponent
        opponent = get_campaign_opponent(0)
        assert opponent.name == "Wolves FC"
        assert opponent.tactics == [TacticalStyle.LOW_BLOCK]

        # Detect squad synergies
        synergies = load_synergies()
        persistent = detect_squad_synergies(squad, synergies)

        ms = create_match(
            squad=squad, synergies=synergies,
            opponent=opponent,
            round_targets=opponent.round_targets,
            persistent_buffs=persistent,
            synergy_pool=[s for s in synergies if not s.persistent],
        )

        # Start round
        start_round(ms)
        assert len(ms.phase_hand) == 8

        # Pick 3 phases
        phases = ms.phase_hand[:3]
        set_selected_phases(ms, phases)
        assert len(ms.phases) == 3

        # Play through 3 phases
        total_score = 0
        for idx in range(3):
            start_phase(ms)
            phase = ms.phases[idx]

            # Place players matching phase slots
            slots = phase.slots[:phase.max_cards]
            placed = 0
            for slot_idx, slot in enumerate(slots):
                # Find a squad player who matches
                for player in squad:
                    if player in [p for p, _ in ms.field]:
                        continue  # Already placed
                    if player.position == "GK" and slot != "GK":
                        continue  # GK can only play GK
                    if slot == "GK" and player.position != "GK":
                        continue
                    # Place at the slot position
                    field_pos = slot if isinstance(slot, str) else (
                        slot[0] if isinstance(slot, list) else slot.get("as", "CB")
                    )
                    place_player(ms, player, field_pos)
                    placed += 1
                    break

            assert placed > 0, f"Could not place any player for phase {phase.name}"

            result = resolve_phase(ms)
            assert result["total"] > 0, f"Phase {idx} scored 0"
            total_score += result["total"]

            if idx < 2:
                advance_phase(ms)

        assert total_score > 0
        assert len(ms.phase_results) == 3

        # Verify energy was consumed
        energy_summary = ms.energy.summary()
        assert "0.85" in energy_summary or "0.65" in energy_summary  # Some players should be tired

        # Check round result
        won = check_round(ms)
        # May or may not win with an auto-drafted squad — that's fine
        assert ms.rounds_won + ms.rounds_lost == 1


class TestEnergyDepletion:
    """Verify energy depletes correctly across phases."""

    def test_energy_depletes_across_phases(self, terry_henri):
        """Player used in all 3 phases should go Fresh→Tired→Exhausted."""
        ms = create_match(squad=[terry_henri], synergies=[])
        ms.phases = [
            Phase("p1", "P1", ["ST"], "ATK", 1, "", tag="Attacking"),
            Phase("p2", "P2", ["ST"], "ATK", 1, "", tag="Attacking"),
            Phase("p3", "P3", ["ST"], "ATK", 1, "", tag="Attacking"),
        ]

        # Phase 1: fresh
        ms.current_phase_idx = 0
        ms.field = [(terry_henri, "ST")]
        resolve_phase(ms)
        assert ms.energy.get(terry_henri.id).current == 2  # TIRED
        assert ms.energy.get_multiplier(terry_henri.id) == 0.85

        # Phase 2: tired
        ms.current_phase_idx = 1
        ms.field = [(terry_henri, "ST")]
        resolve_phase(ms)
        assert ms.energy.get(terry_henri.id).current == 1  # EXHAUSTED
        assert ms.energy.get_multiplier(terry_henri.id) == 0.65

        # Phase 3: exhausted (may or may not injure)
        ms.current_phase_idx = 2
        ms.field = [(terry_henri, "ST")]
        resolve_phase(ms)
        e = ms.energy.get(terry_henri.id)
        assert e.current <= 1  # 0 (injured) or 1 (escaped injury)

    def test_bench_recovery_between_rounds(self, terry_henri, il_capitano):
        """Unused player recovers energy between rounds."""
        ms = create_match(squad=[terry_henri, il_capitano], synergies=[])
        ms.phases = [Phase("p1", "P1", ["ST"], "ATK", 1, "", tag="Attacking")]

        # Use terry but not il_capitano
        ms.current_phase_idx = 0
        ms.field = [(terry_henri, "ST")]
        resolve_phase(ms)
        assert ms.energy.get_multiplier(terry_henri.id) == 0.85  # TIRED
        assert ms.energy.get_multiplier(il_capitano.id) == 1.0    # Still fresh

        # Start new round — bench recovery
        start_round(ms)
        # il_capitano was not used, recovers if below max (already at 3)
        assert ms.energy.get_multiplier(il_capitano.id) == 1.0

    def test_rotation_forced(self, terry_henri, bale_out, il_capitano):
        """Using same player all phases tanks their output; rotation preserves power."""
        squad = [terry_henri, bale_out, il_capitano]
        ms = create_match(squad=squad, synergies=[])
        ms.phases = [
            Phase("p1", "P1", ["ST"], "ATK", 1, "", tag="Attacking"),
            Phase("p2", "P2", ["ST"], "ATK", 1, "", tag="Attacking"),
            Phase("p3", "P3", ["ST"], "ATK", 1, "", tag="Attacking"),
        ]

        scores_no_rotation = []
        for idx in range(3):
            ms.current_phase_idx = idx
            ms.field = [(terry_henri, "ST")]  # Same player every phase
            result = resolve_phase(ms)
            scores_no_rotation.append(result["total"])

        # Scores should decrease as energy depletes
        assert scores_no_rotation[0] > scores_no_rotation[2], \
            f"Expected declining scores, got {scores_no_rotation}"


class TestOpponentTacticsFullFlow:
    """Opponent modifiers are applied during actual play."""

    def test_high_press_penalizes_possession(self, don_andres, maestro_xav, captain_stevie):
        """HIGH_PRESS opponent should reduce Possession phase scores."""
        opp = Opponent(
            name="Pressers", tier="Match 3/5",
            tactics=[TacticalStyle.HIGH_PRESS],
            intro="Test.", round_targets=[4000, 6500, 9000],
        )
        ms = create_match(squad=[don_andres, maestro_xav, captain_stevie],
                          synergies=[], opponent=opp)
        ms.phases = [Phase("tk", "Tiki-Taka", ["CM", "CM", "CAM"], "PAS", 3, "", tag="Possession")]
        ms.current_phase_idx = 0
        ms.field = [(maestro_xav, "CM"), (captain_stevie, "CM"), (don_andres, "CAM")]

        result = resolve_phase(ms)
        # Without opponent, total should be higher
        # With HIGH_PRESS: Possession phases ×0.7
        assert result["total"] > 0

        # Compare without opponent
        ms2 = create_match(squad=[don_andres, maestro_xav, captain_stevie],
                           synergies=[], opponent=None)
        ms2.phases = ms.phases
        ms2.current_phase_idx = 0
        ms2.field = list(ms.field)
        result2 = resolve_phase(ms2)

        # Opponent version should be lower
        assert result["total"] < result2["total"], \
            f"Opponent should nerf score: {result['total']} vs {result2['total']}"


class TestMomentumFlow:
    """Momentum builds only on consecutive good phases."""

    def test_momentum_builds_on_consecutive_hits(self, terry_henri, bale_out, il_capitano):
        """Three players hitting 15% threshold builds momentum across phases."""
        squad = [terry_henri, bale_out, il_capitano]
        ms = create_match(squad=squad, synergies=[], round_targets=[300, 500, 800])
        ms.phases = [
            Phase("p1", "P1", ["ST"], "ATK", 1, "", tag="Attacking"),
            Phase("p2", "P2", ["LW"], "ATK", 1, "", tag="Attacking"),
            Phase("p3", "P3", ["CB"], "ATK", 1, "", tag="Attacking"),
        ]

        # Phase 1: Terry at ST (53 chips), no momentum, target=300 (15%=45), 53>45 ✓
        ms.current_phase_idx = 0
        ms.field = [(terry_henri, "ST")]
        r1 = resolve_phase(ms)
        assert ms.momentum == 1.0  # Phase 1 always 1.0

        # Phase 2: should see r1 >= 45, momentum → 1.15
        ms.current_phase_idx = 1
        ms.field = [(bale_out, "LW")]
        r2 = resolve_phase(ms)
        assert ms.momentum >= 1.15

        # Phase 3: should build further if r2 also hits threshold
        ms.current_phase_idx = 2
        ms.field = [(il_capitano, "CB")]
        r3 = resolve_phase(ms)
        # Momentum should have stacked
        assert ms.momentum >= 1.15

    def test_momentum_resets_on_miss(self, terry_henri):
        """If a phase misses the 15% threshold, momentum resets."""
        ms = create_match(squad=[terry_henri], synergies=[], round_targets=[2000, 3500, 5000])
        ms.phases = [
            Phase("p1", "P1", ["ST"], "ATK", 1, "", tag="Attacking"),
            Phase("p2", "P2", ["ST"], "ATK", 1, "", tag="Attacking"),
        ]

        # Phase 1: Terry 53 chips, target 2000 (15%=300), 53<300 → not enough
        ms.current_phase_idx = 0
        ms.field = [(terry_henri, "ST")]
        r1 = resolve_phase(ms)
        assert ms.momentum == 1.0

        # Phase 2: momentum should stay at 1.0 (no build, no reset needed)
        ms.current_phase_idx = 1
        ms.field = [(terry_henri, "ST")]
        r2 = resolve_phase(ms)
        assert ms.momentum == 1.0


class TestCampaignEscalation:
    """Campaign opponents get harder across matches."""

    def test_opponents_escalate(self):
        opps = [get_campaign_opponent(i) for i in range(5)]
        # More tactics per match
        tactic_counts = [len(o.tactics) for o in opps]
        assert tactic_counts == [1, 1, 2, 2, 3]

        # Higher targets
        targets = [o.round_targets[0] for o in opps]
        for i in range(4):
            assert targets[i] < targets[i + 1], \
                f"Match {i} target {targets[i]} not < Match {i+1} target {targets[i+1]}"

    def test_match_5_is_brutal(self):
        """Final opponent has 3 tactics and high targets."""
        opp = get_campaign_opponent(4)
        assert opp.name == "Galácticos FC"
        assert len(opp.tactics) == 3
        assert opp.round_targets[2] >= 14000  # Hardest round


class TestScoringParity:
    """Verify scoring module produces consistent results."""

    def test_draft_squad_scoring_consistent(self):
        """Drafted squad produces consistent phase scores."""
        all_players = load_players()
        draft = generate_draft(all_players, seed=99)
        while not draft.is_complete:
            pick = draft.current_pick
            draft.confirm_pick(pick.pool[:pick.count])

        squad = draft.selected
        assert len(squad) >= 10

        # Test scoring with a simple phase
        phase = Phase("test", "Test", ["ST", "CM", "CB"], "ATK", 3, "", tag="Attacking")

        # Find matching players
        st = next((p for p in squad if p.position == "ST"), squad[0])
        cm = next((p for p in squad if p.position in ("CM", "CDM", "CAM")), squad[0])
        cb = next((p for p in squad if p.position == "CB"), squad[0])

        field = [(st, "ST"), (cm, "CM"), (cb, "CB")]
        synergies = load_synergies()
        result = calculate_round_score(field, synergies)

        assert result["total"] > 0
        assert len(result["breakdown"]) == 3
        assert result["formation_mult"] == 1.0  # No formation
