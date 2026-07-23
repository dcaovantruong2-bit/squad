"""Tests for the flexible formation-first drafting system."""

import pytest
from src.draft import (
    DraftPick, DraftState, generate_draft, generate_reward_cards,
    DRAFT_ROUNDS, POSITION_GROUPS,
)
from src.cards import PlayerCard
from src.loader import load_players


def _mk(id_, name, pos, atk=5, pac=5, pas=5, def_=5, spc=5, traits=None):
    return PlayerCard(id=id_, name=name, position=pos,
                      atk=atk, pac=pac, pas=pas, def_=def_, spc=spc,
                      traits=traits or [])


class TestDraftPick:
    def test_basic_pick(self):
        pool = [_mk("a", "A", "ST"), _mk("b", "B", "ST"), _mk("c", "C", "ST")]
        pick = DraftPick(group="ATK", count=2, pool=pool, label="Pick 2 Attackers")
        assert pick.can_pick_multiple is True
        assert pick.count == 2
        assert len(pick.pool) == 3

    def test_select_removes_from_pool(self):
        pool = [_mk("a", "A", "ST"), _mk("b", "B", "ST")]
        pick = DraftPick(group="ATK", count=1, pool=list(pool), label="Pick")
        assert pick.select(pool[0]) is True
        assert len(pick.pool) == 1

    def test_single_pick_flag(self):
        pick = DraftPick(group="GK", count=1, pool=[_mk("g", "G", "GK")], label="Pick GK")
        assert pick.can_pick_multiple is False


class TestDraftState:
    def test_empty_state(self):
        ds = DraftState()
        assert ds.current_pick is None
        assert ds.is_complete is True

    def test_confirm_pick_advances(self):
        pool = [_mk("a", "A", "GK"), _mk("b", "B", "GK")]
        picks = [DraftPick(group="GK", count=1, pool=list(pool), label="Pick GK")]
        ds = DraftState(picks=picks)
        done = ds.confirm_pick([pool[0]])
        assert done is True
        assert len(ds.selected) == 1

    def test_confirm_wrong_count_fails(self):
        pool = [_mk("a", "A", "CB"), _mk("b", "B", "CB"), _mk("c", "C", "CB")]
        picks = [DraftPick(group="DEF", count=4, pool=list(pool), label="Pick 4 Defenders")]
        ds = DraftState(picks=picks)
        assert ds.confirm_pick([pool[0]]) is False  # Only 1 of 4

    def test_progress_tracking(self):
        p1 = DraftPick(group="GK", count=1, pool=[_mk("g", "G", "GK")], label="Pick GK")
        p2 = DraftPick(group="DEF", count=1, pool=[_mk("c", "C", "CB")], label="Pick DEF")
        ds = DraftState(picks=[p1, p2])
        assert ds.progress_pct == 0.0
        ds.confirm_pick([p1.pool[0]])
        assert ds.progress_pct == 50.0

    def test_squad_summary(self):
        players = [
            _mk("g", "Gigi", "GK", traits=["leader"]),
            _mk("c1", "CB1", "CB", traits=["physical"]),
            _mk("c2", "CB2", "CB", traits=["aerial"]),
        ]
        ds = DraftState(selected=players)
        summary = ds.get_squad_summary()
        assert "Gigi" in summary
        assert "leader: 1" in summary


class TestGenerateDraft:
    def test_generates_four_picks(self):
        players = load_players()
        draft = generate_draft(players)
        assert len(draft.picks) == 4  # GK, DEF, MID, ATK

    def test_draft_order(self):
        players = load_players()
        draft = generate_draft(players)
        groups = [p.group for p in draft.picks]
        assert groups == ["GK", "DEF", "MID", "ATK"]

    def test_all_players_shown_in_each_group(self):
        """Full pools — every player in each position group should appear."""
        players = load_players()
        draft = generate_draft(players)
        for pick in draft.picks:
            # All players in this group should be in the pool
            expected_in_group = [p for p in players if POSITION_GROUPS.get(p.position) == pick.group]
            assert len(pick.pool) == len(expected_in_group), \
                f"Pool for {pick.group} has {len(pick.pool)}, expected {len(expected_in_group)}"

    def test_no_duplicates_in_pool(self):
        players = load_players()
        draft = generate_draft(players)
        for pick in draft.picks:
            ids = [p.id for p in pick.pool]
            assert len(ids) == len(set(ids))

    def test_complete_draft_flow(self):
        """Run through a full draft, picking valid players."""
        players = load_players()
        draft = generate_draft(players, seed=42)
        while not draft.is_complete:
            pick = draft.current_pick
            chosen = pick.pool[:pick.count]
            done = draft.confirm_pick(chosen)
        assert len(draft.selected) == 10  # 1+4+3+2 = 10

    def test_defender_flexibility(self):
        """Player can pick any mix of CBs and FBs in the defender round."""
        players = load_players()
        draft = generate_draft(players, seed=42)

        # First complete the GK pick
        gk_pick = draft.picks[0]
        draft.confirm_pick([gk_pick.pool[0]])

        # Now at the DEF round
        def_pick = draft.picks[1]
        assert def_pick.group == "DEF"
        assert def_pick.count == 4

        # Pick 3 CBs + 1 FB
        cbs = [p for p in def_pick.pool if p.position == "CB"][:3]
        fbs = [p for p in def_pick.pool if p.position == "FB"][:1]
        chosen = cbs + fbs
        assert len(chosen) == 4
        is_done = draft.confirm_pick(chosen)
        # confirm_pick returns is_complete (False = more picks remain)
        # After GK + DEF, we've done 2 of 4 picks
        assert draft.current_pick_idx == 2

        positions = [p.position for p in draft.selected if p.position in ("CB", "FB")]
        assert positions.count("CB") == 3
        assert positions.count("FB") == 1

    def test_seeded_draft_reproducible(self):
        players = load_players()
        d1 = generate_draft(players, seed=42)
        d2 = generate_draft(players, seed=42)
        for p1, p2 in zip(d1.picks, d2.picks):
            assert [x.id for x in p1.pool] == [x.id for x in p2.pool]


class TestGenerateRewards:
    def test_returns_correct_count(self):
        players = [_mk(chr(ord("a") + i), chr(ord("A") + i), "ST") for i in range(5)]
        rewards = generate_reward_cards(players, count=3)
        assert len(rewards) == 3

    def test_all_player_type(self):
        players = [_mk("a", "A", "ST"), _mk("b", "B", "LW"), _mk("c", "C", "RW")]
        rewards = generate_reward_cards(players, count=3)
        for r in rewards:
            assert r["type"] == "player"

    def test_empty_pool_fallback(self):
        rewards = generate_reward_cards([], count=3)
        assert len(rewards) == 3
        assert all(r["type"] == "shop" for r in rewards)


class TestPositionGroups:
    def test_all_positions_mapped(self):
        for pos in ["GK", "CB", "FB", "CM", "CDM", "CAM", "ST", "LW", "RW"]:
            assert pos in POSITION_GROUPS, f"Position {pos} not mapped"

    def test_defenders_grouped(self):
        for pos in ["CB", "FB"]:
            assert POSITION_GROUPS[pos] == "DEF"

    def test_midfielders_grouped(self):
        for pos in ["CM", "CDM", "CAM"]:
            assert POSITION_GROUPS[pos] == "MID"

    def test_attackers_grouped(self):
        for pos in ["ST", "LW", "RW"]:
            assert POSITION_GROUPS[pos] == "ATK"
