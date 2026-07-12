"""Tests for main.py — import cleanly and exercise all display functions.

These tests catch missing-import bugs (like the calculate_chips NameError)
by verifying the module loads and every display function runs without error.
"""

import pytest
from src.cards import PlayerCard
from src.phases import Phase


# ═══════════════════════════════════════════════════════════════════════
# Module-level import smoke test
# ═══════════════════════════════════════════════════════════════════════

def test_main_module_imports_cleanly():
    """Import main — catches missing top-level imports at module load time."""
    import main  # noqa: F811
    # If we got here, no ImportError or NameError on module load


# ═══════════════════════════════════════════════════════════════════════
# Display function smoke tests
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_player():
    return PlayerCard(
        id="test_player", name="Test Player", position="ST",
        atk=8, pac=7, pas=6, def_=5, spc=4,
        traits=["pacey", "clinical"],
    )


@pytest.fixture
def sample_field(sample_player):
    return [(sample_player, "ST")]


@pytest.fixture
def sample_fatigue():
    return {}


@pytest.fixture
def sample_phase_result(sample_player):
    """A realistic scoring result dict matching calculate_round_score output (new Balatro format)."""
    return {
        "total": 240,
        "breakdown": [
            {
                "player": sample_player.name,
                "position": "ST",
                "base_chips": 53,
                "pos_bonus": 0,
                "persistent_add": 0,
                "persistent_mult": 1.0,
                "fatigue": 1.0,
                "effective_chips": 53,
            },
        ],
        "player_chip_sum": 53,
        "synergy_chips": 20,
        "carryover_chips": 0,
        "persistent_chips": 0,
        "total_chips": 73,
        "add_mult": 1,
        "x_mult": 1.5,
        "formation_mult": 1.0,
        "formation_name": "4-4-2",
        "subtotal_before_formation": 109,
        "fired_synergies": ["Clean Sheet", "Stretch the Backline"],
        "fired_details": [
            {
                "name": "Clean Sheet",
                "description": "GK DEF + CB DEF ≥ 18: +20 chips",
                "effect_type": "chips",
                "value": 20,
                "contributors": ["Gigi The Wall [GK]", "El Capitán [CB]"],
            },
            {
                "name": "Stretch the Backline",
                "description": "FB PAC + LW PAC ≥ 17: ×1.5 mult",
                "effect_type": "x_mult",
                "value": 1.5,
                "contributors": ["Dani Elvis [FB]", "Bale Out [LW]"],
            },
        ],
        "next_carryover": None,
        "synergy_contributors": {
            "Clean Sheet": ["Gigi The Wall [GK]", "El Capitán [CB]"],
            "Stretch the Backline": ["Dani Elvis [FB]", "Bale Out [LW]"],
        },
        "synergy_descriptions": {
            "Clean Sheet": "GK DEF + CB DEF ≥ 18: +20 chips",
            "Stretch the Backline": "FB PAC + LW PAC ≥ 17: ×1.5 mult",
        },
        "phase_name": "Goal Kick",
        "phase_weight": "DEF",
    }


def test_show_field_no_crash(sample_field, sample_fatigue):
    """show_field should not throw NameError or any exception with valid data."""
    from main import show_field
    show_field(sample_field, sample_fatigue)


def test_show_field_empty(sample_fatigue):
    """Empty field should display a placeholder, not crash."""
    from main import show_field
    show_field([], sample_fatigue)


def test_show_phase_result_no_crash(sample_phase_result):
    """show_phase_result should not crash with a realistic scoring dict."""
    from main import show_phase_result
    show_phase_result(sample_phase_result)


def test_show_phase_result_empty_synergies(sample_phase_result):
    """show_phase_result handles empty synergy lists gracefully."""
    result = dict(sample_phase_result)
    result["fired_synergies"] = []
    from main import show_phase_result
    show_phase_result(result)


def test_show_phase_result_no_synergy_extras(sample_phase_result):
    """show_phase_result handles missing synergy_contributors gracefully."""
    result = dict(sample_phase_result)
    result["synergy_contributors"] = {}
    from main import show_phase_result
    show_phase_result(result)


def test_player_short_is_valid(sample_player):
    """player_short returns a string with the player's key info."""
    from main import player_short
    output = player_short(sample_player)
    assert isinstance(output, str)
    assert sample_player.name in output
    assert sample_player.position in output


def test_player_short_with_fatigue(sample_player):
    """player_short shows fatigue percentage when below 1.0."""
    from main import player_short
    output = player_short(sample_player, fatigue_mult=0.7)
    assert "70" in output or "70%" in output


def test_color_for_fatigue_full():
    """Fresh player shows green."""
    from main import color_for_fatigue
    assert color_for_fatigue(1.0) == "green"


def test_color_for_fatigue_partial():
    """Moderate fatigue shows yellow."""
    from main import color_for_fatigue
    assert color_for_fatigue(0.7) == "yellow"


def test_color_for_fatigue_exhausted():
    """Heavy fatigue shows red."""
    from main import color_for_fatigue
    assert color_for_fatigue(0.3) == "red"


# ═══════════════════════════════════════════════════════════════════════
# Integration: player_short does not crash on any position type
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("position", ["GK", "CB", "FB", "CDM", "CM", "CAM", "LW", "RW", "ST"])
def test_player_short_all_positions(position):
    """player_short works for every possible position."""
    from main import player_short
    p = PlayerCard(
        id=f"p_{position}", name=f"Player {position}", position=position,
        atk=5, pac=5, pas=5, def_=5, spc=5,
        traits=[],
    )
    output = player_short(p)
    assert output.startswith(f"Player {position}")


# ═══════════════════════════════════════════════════════════════════════
# Edge case: show_field with a player in every possible position
# ═══════════════════════════════════════════════════════════════════════

def test_show_field_all_positions():
    """show_field handles players in any field position, matching CHIPS_FORMULA keys."""
    from main import show_field
    p = PlayerCard(
        id="versatile", name="Versa Tile", position="CM",
        atk=5, pac=5, pas=5, def_=5, spc=5,
        traits=[],
    )
    field = [(p, pos) for pos in ["ST", "LW", "RW", "CM", "CAM", "CDM", "CB", "FB", "GK"]]
    show_field(field, {})


def test_show_field_single_entry(sample_player, sample_fatigue):
    """show_field with exactly one player works."""
    from main import show_field
    show_field([(sample_player, "ST")], sample_fatigue)


def test_show_field_mixed_fatigue(sample_player):
    """show_field with players at different fatigue levels."""
    from main import show_field
    p2 = PlayerCard(
        id="tired_guy", name="Tired Guy", position="CM",
        atk=3, pac=3, pas=3, def_=3, spc=3,
        traits=[],
    )
    field = [(sample_player, "ST"), (p2, "CM")]
    fatigue = {sample_player.id: 1.0, p2.id: 0.49}
    show_field(field, fatigue)


# ═══════════════════════════════════════════════════════════════════════
# show_squad_full smoke test
# ═══════════════════════════════════════════════════════════════════════

def test_show_squad_full_no_crash(sample_player):
    """show_squad_full handles a small squad."""
    from main import show_squad_full
    show_squad_full([sample_player], {})


def test_show_squad_full_empty():
    """show_squad_full with empty squad."""
    from main import show_squad_full
    show_squad_full([], {})
