#!/usr/bin/env python3
"""Playtest all UI display functions — edge cases, empty data, missing keys."""

import sys
import os
import io
from unittest.mock import patch

# Add game to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cards import PlayerCard


import builtins

# ─── Helper: monkey-patch input to avoid blocking ───
_real_input = builtins.input


def _dummy_input(prompt=""):
    return "skip"


builtins.input = _dummy_input

# Import main (which defines all display helpers)
import main


def make_player(id_, name, position="ST", atk=5, pac=5, pas=5, def_=5, spc=5, traits=None):
    traits = traits or []
    return PlayerCard(id=id_, name=name, position=position, atk=atk, pac=pac, pas=pas, def_=def_, spc=spc, traits=traits)


def test_player_short():
    print("\n=== TEST: player_short ===")
    p = make_player("p1", "Messi", position="RW", atk=9, pac=8, pas=9, def_=3, spc=8)

    # Normal
    print(main.player_short(p, fatigue_mult=1.0))
    # Fatigued
    print(main.player_short(p, fatigue_mult=0.7))
    # Very fatigued
    print(main.player_short(p, fatigue_mult=0.49))
    # Long name
    p2 = make_player("p2", "Alexander-Arnold", position="FB", atk=5, pac=8, pas=9, def_=6, spc=7)
    print(main.player_short(p2, fatigue_mult=0.3))


def test_color_for_fatigue():
    print("\n=== TEST: color_for_fatigue ===")
    # Boundary: exactly 1.0
    assert main.color_for_fatigue(1.0) == "green", f"Expected green, got {main.color_for_fatigue(1.0)}"
    # Boundary: exactly 0.7
    assert main.color_for_fatigue(0.7) == "yellow", f"Expected yellow, got {main.color_for_fatigue(0.7)}"
    # Boundary: just below 0.7
    assert main.color_for_fatigue(0.699) == "red", f"Expected red, got {main.color_for_fatigue(0.699)}"
    # Very high
    assert main.color_for_fatigue(2.0) == "green", f"Expected green, got {main.color_for_fatigue(2.0)}"
    # Very low
    assert main.color_for_fatigue(0.0) == "red", f"Expected red, got {main.color_for_fatigue(0.0)}"
    # Negative
    assert main.color_for_fatigue(-1.0) == "red", f"Expected red for negative, got {main.color_for_fatigue(-1.0)}"
    print("All color_for_fatigue tests passed!")


def test_show_squad_full():
    print("\n=== TEST: show_squad_full ===")
    # Empty squad
    print("--- Empty squad ---")
    main.show_squad_full([], {})
    print("--- Single player ---")
    p = make_player("p1", "Neuer", position="GK", atk=2, pac=3, pas=5, def_=9, spc=7)
    main.show_squad_full([p], {"p1": 1.0})
    print("--- Full squad with various fatigue ---")
    squad = [
        make_player("g1", "Alisson", "GK", atk=2, pac=4, pas=4, def_=9, spc=7),
        make_player("cb1", "Van Dijk", "CB", atk=3, pac=5, pas=6, def_=10, spc=5),
        make_player("cb2", "Ramos", "CB", atk=5, pac=6, pas=5, def_=9, spc=6),
        make_player("fb1", "Robertson", "FB", atk=4, pac=8, pas=7, def_=7, spc=5),
        make_player("cdm1", "Casemiro", "CDM", atk=3, pac=4, pas=5, def_=9, spc=4),
        make_player("cm1", "De Bruyne", "CM", atk=7, pac=5, pas=10, def_=4, spc=8),
        make_player("lw1", "Vinicius", "LW", atk=8, pac=10, pas=6, def_=2, spc=8),
        make_player("rw1", "Salah", "RW", atk=9, pac=9, pas=6, def_=3, spc=7),
        make_player("st1", "Haaland", "ST", atk=10, pac=8, pas=3, def_=2, spc=5),
    ]
    fatigue = {
        "g1": 0.7, "cb1": 1.0, "cb2": 0.5, "fb1": 0.9, "cdm1": 0.3,
        "cm1": 1.0, "lw1": 0.7, "rw1": 0.8, "st1": 1.0,
    }
    main.show_squad_full(squad, fatigue)
    print("--- Players with missing fatigue (should default to 1.0) ---")
    main.show_squad_full(squad, {})


def test_show_field():
    print("\n=== TEST: show_field ===")
    # Empty field
    print("--- Empty field ---")
    main.show_field([], {})
    print("--- Single player ---")
    p = make_player("st1", "Haaland", "ST", atk=10, pac=8, pas=3, def_=2, spc=5)
    main.show_field([(p, "ST")], {"st1": 0.7})
    print("--- Full field ---")
    field = [
        (make_player("g1", "Ederson", "GK", atk=2, pac=4, pas=6, def_=8, spc=7), "GK"),
        (make_player("cb1", "Dias", "CB", atk=3, pac=4, pas=5, def_=9, spc=5), "CB"),
        (make_player("cb2", "Stones", "CB", atk=4, pac=5, pas=6, def_=8, spc=6), "CB"),
        (make_player("cm1", "Rodri", "CM", atk=5, pac=4, pas=8, def_=9, spc=6), "CM"),
        (make_player("st1", "Kane", "ST", atk=9, pac=5, pas=7, def_=3, spc=7), "ST"),
    ]
    fatigue = {"g1": 1.0, "cb1": 0.7, "cb2": 0.5, "cm1": 1.0, "st1": 0.3}
    main.show_field(field, fatigue)
    print("--- Players with no fatigue entries ---")
    main.show_field(field, {})


def test_show_phase_result():
    print("\n=== TEST: show_phase_result ===")

    # 1. Normal result
    print("--- Normal result ---")
    result = {
        "phase_name": "Counter Attack",
        "breakdown": [
            {"player": "Haaland", "position": "ST", "base_chips": 50, "add_chips": 10,
             "multiply": 1.3, "fatigue": 1.0, "subtotal": 78},
            {"player": "Vinicius", "position": "LW", "base_chips": 40, "add_chips": 5,
             "multiply": 1.0, "fatigue": 0.7, "subtotal": 31},
        ],
        "subtotal_before_globals": 109,
        "global_mult": 1.0,
        "global_add": 0,
        "formation_mult": 1.0,
        "formation_name": "4-3-3",
        "total": 109,
        "fired_synergies": ["Route One", "Wingback Overlap"],
        "synergy_contributors": {
            "Route One": ["Haaland [ST]", "Dias [CB]"],
            "Wingback Overlap": ["Robertson [FB]", "De Bruyne [CM]"],
        },
        "synergy_descriptions": {
            "Route One": "CB+ST combo for extra chips",
            "Wingback Overlap": "FB+CM combo for extra chips",
        },
    }
    main.show_phase_result(result)

    # 2. No synergies
    print("--- No synergies ---")
    result2 = {
        "phase_name": "Set Piece",
        "breakdown": [
            {"player": "Ronaldo", "position": "ST", "base_chips": 45, "add_chips": 0,
             "multiply": 1.0, "fatigue": 1.0, "subtotal": 45},
        ],
        "subtotal_before_globals": 45,
        "total": 45,
    }
    main.show_phase_result(result2)

    # 3. Missing keys (minimal result)
    print("--- Minimal result (missing keys) ---")
    result3 = {
        "phase_name": "Minimal Phase",
        "breakdown": [],
        "subtotal_before_globals": 0,
        "total": 0,
    }
    main.show_phase_result(result3)

    # 4. With global_mult and global_add
    print("--- With global multipliers and adds ---")
    result4 = {
        "phase_name": "Global Effects Phase",
        "breakdown": [
            {"player": "Messi", "position": "RW", "base_chips": 55, "add_chips": 15,
             "multiply": 1.5, "fatigue": 1.0, "subtotal": 105},
        ],
        "subtotal_before_globals": 105,
        "global_mult": 1.2,
        "global_add": 20,
        "formation_mult": 1.1,
        "formation_name": "4-3-3 Attack",
        "total": 138,
    }
    main.show_phase_result(result4)

    # 5. Fired synergies with "(persistent)" — should be filtered out
    print("--- Synergies with '(persistent)' tags ---")
    result5 = {
        "phase_name": "Persistent Test",
        "breakdown": [
            {"player": "Kane", "position": "ST", "base_chips": 60, "add_chips": 0,
             "multiply": 1.0, "fatigue": 0.7, "subtotal": 42},
        ],
        "subtotal_before_globals": 42,
        "total": 42,
        "fired_synergies": ["Iron Will (persistent)", "Double Pivot (carryover)"],
        "synergy_contributors": {},
        "synergy_descriptions": {},
    }
    main.show_phase_result(result5)

    # 6. Only persistent synergies (all filtered)
    print("--- Only persistent synergies (all filtered out) ---")
    result6 = {
        "phase_name": "All Persistent",
        "breakdown": [
            {"player": "Son", "position": "LW", "base_chips": 48, "add_chips": 0,
             "multiply": 1.0, "fatigue": 1.0, "subtotal": 48},
        ],
        "subtotal_before_globals": 48,
        "total": 48,
        "fired_synergies": ["Iron Will (persistent)"],
    }
    main.show_phase_result(result6)

    # 7. Empty contributors dict
    print("--- Empty contributors with synergies ---")
    result7 = {
        "phase_name": "No Contributors",
        "breakdown": [
            {"player": "Neymar", "position": "LW", "base_chips": 50, "add_chips": 10,
             "multiply": 1.2, "fatigue": 1.0, "subtotal": 72},
        ],
        "subtotal_before_globals": 72,
        "total": 72,
        "fired_synergies": ["Stretch Backline"],
        "synergy_contributors": {},
        "synergy_descriptions": {"Stretch Backline": "FB+Lw pace combo"},
    }
    main.show_phase_result(result7)

    # 8. Negative values
    print("--- Negative values ---")
    result8 = {
        "phase_name": "Negative Test",
        "breakdown": [
            {"player": "Own Goal", "position": "CB", "base_chips": -10, "add_chips": -5,
             "multiply": 1.0, "fatigue": 1.0, "subtotal": -15},
        ],
        "subtotal_before_globals": -15,
        "global_add": -10,
        "total": -25,
    }
    main.show_phase_result(result8)

    # 9. Synergy with parenthesis in name (not persistent/carryover, but with qualifier e.g. "Trio (×1.3)")
    print("--- Synergies with qualifiers like 'Trio (×1.3)' ---")
    result9 = {
        "phase_name": "Qualified Synergies",
        "breakdown": [
            {"player": "Pedri", "position": "CM", "base_chips": 35, "add_chips": 5,
             "multiply": 1.3, "fatigue": 1.0, "subtotal": 52},
        ],
        "subtotal_before_globals": 52,
        "total": 52,
        "fired_synergies": ["Trio (×1.3)", "Back Three"],
        "synergy_contributors": {
            "Trio": ["Pedri [CM]", "Gavi [CM]", "FDJ [CM]"],
            "Back Three": ["Dias [CB]", "Stones [CB]", "Ake [CB]"],
        },
        "synergy_descriptions": {
            "Trio": "Three CMs with high passing",
            "Back Three": "Three CBs with high defense",
        },
    }
    main.show_phase_result(result9)

    # 10. Multipliers of exactly 1.0 and 0.0 (edge)
    print("--- Multiplier edge cases ---")
    result10 = {
        "phase_name": "Multiplier Edge",
        "breakdown": [
            {"player": "Zero", "position": "ST", "base_chips": 100, "add_chips": 0,
             "multiply": 0.0, "fatigue": 0.5, "subtotal": 0},
        ],
        "subtotal_before_globals": 0,
        "total": 0,
    }
    main.show_phase_result(result10)

    print("\nAll show_phase_result tests completed!")


def test_show_round_result():
    print("\n=== TEST: show_round_result ===")
    print("--- Won ---")
    main.show_round_result(750, 650, True)
    print("--- Lost ---")
    main.show_round_result(600, 650, False)
    print("--- Exact tie (lost) ---")
    main.show_round_result(650, 650, False)
    print("--- Tiny margin ---")
    main.show_round_result(651, 650, True)


def test_show_campaign_bracket():
    print("\n=== TEST: _show_campaign_bracket ===")
    for idx in range(-1, 7):
        print(f"--- Index {idx} ---")
        main._show_campaign_bracket(idx)


def test_cprint():
    print("\n=== TEST: cprint ===")

    # Test with rich available (should be True in our venv)
    print(f"HAS_RICH = {main.HAS_RICH}")

    # Basic
    main.cprint("Hello World")
    main.cprint("Bold text", style="bold")
    main.cprint("Red text", style="red")
    main.cprint("No newline", end="")
    print(" (inline)")

    # Test fallback without rich
    print("\n--- Testing cprint fallback (simulate no rich) ---")
    original_has_rich = main.HAS_RICH
    original_console = main.console
    main.HAS_RICH = False
    try:
        main.cprint("Fallback text")
        main.cprint("Fallback bold (ignored)", style="bold")
        main.cprint("Fallback no end", end="")
        print(" (inline)")
    finally:
        main.HAS_RICH = original_has_rich
        main.console = original_console

    print("cprint tests passed!")


def test_show_phase_header():
    """Quick test of show_phase_header (not explicitly requested but for completeness)."""
    print("\n=== TEST: show_phase_header ===")
    from src.phases import Phase

    phase = Phase(
        id="counter_attack",
        name="Counter Attack",
        description="Break fast after winning possession",
        weight="PAC",
        slots=["ST", "LW", "RW"],
        max_cards=3,
    )
    print("--- Without carryover ---")
    main.show_phase_header(phase, 0, 1, 650, 200, 1, 0, carryover=None)
    print("--- With carryover ---")
    main.show_phase_header(phase, 2, 2, 700, 450, 1, 0, carryover={
        "add_chips": 40,
        "source_synergy": "Double Pivot",
    })
    print("--- Edge: carryover with zero chips ---")
    main.show_phase_header(phase, 4, 3, 850, 700, 2, 0, carryover={
        "add_chips": 0,
        "source_synergy": "Empty Carryover",
    })


def test_show_phase_result_missing_phase_name():
    """Test missing phase_name key should raise KeyError."""
    print("\n=== TEST: show_phase_result missing phase_name (expected KeyError) ===")
    result = {
        "breakdown": [],
        "subtotal_before_globals": 0,
        "total": 0,
    }
    try:
        main.show_phase_result(result)
        print("ERROR: Should have raised KeyError for missing 'phase_name'!")
    except KeyError as e:
        print(f"Correctly raised KeyError: {e}")


def test_show_phase_result_missing_breakdown():
    """Test missing breakdown key."""
    print("\n=== TEST: show_phase_result missing breakdown (expected KeyError) ===")
    result = {
        "phase_name": "Missing Breakdown",
        "subtotal_before_globals": 0,
        "total": 0,
    }
    try:
        main.show_phase_result(result)
        print("ERROR: Should have raised KeyError for missing 'breakdown'!")
    except KeyError as e:
        print(f"Correctly raised KeyError: {e}")


def test_show_phase_result_missing_subtotal():
    """Test missing subtotal_before_globals."""
    print("\n=== TEST: show_phase_result missing subtotal (expected KeyError) ===")
    result = {
        "phase_name": "Missing Subtotal",
        "breakdown": [],
        "total": 0,
    }
    try:
        main.show_phase_result(result)
        print("ERROR: Should have raised KeyError for missing 'subtotal_before_globals'!")
    except KeyError as e:
        print(f"Correctly raised KeyError: {e}")


def test_show_phase_result_missing_total():
    """Test missing total key."""
    print("\n=== TEST: show_phase_result missing total (expected KeyError) ===")
    result = {
        "phase_name": "Missing Total",
        "breakdown": [],
        "subtotal_before_globals": 0,
    }
    try:
        main.show_phase_result(result)
        print("ERROR: Should have raised KeyError for missing 'total'!")
    except KeyError as e:
        print(f"Correctly raised KeyError: {e}")


def test_show_phase_result_missing_breakdown_keys():
    """Test missing keys inside breakdown entries."""
    print("\n=== TEST: show_phase_result missing breakdown entry keys ===")
    # Missing 'fatigue'
    print("--- Missing 'fatigue' in breakdown entry (expected KeyError) ---")
    result = {
        "phase_name": "Bad Breakdown",
        "breakdown": [
            {"player": "Test", "position": "ST", "base_chips": 50, "add_chips": 0,
             "multiply": 1.0, "subtotal": 50},  # missing 'fatigue'
        ],
        "subtotal_before_globals": 50,
        "total": 50,
    }
    try:
        main.show_phase_result(result)
        print("ERROR: Should have raised KeyError for missing 'fatigue'!")
    except KeyError as e:
        print(f"Correctly raised KeyError: {e}")

    # Missing 'player'
    print("--- Missing 'player' in breakdown entry (expected KeyError) ---")
    result2 = {
        "phase_name": "No Player Name",
        "breakdown": [
            {"position": "ST", "base_chips": 50, "add_chips": 0,
             "multiply": 1.0, "fatigue": 1.0, "subtotal": 50},  # missing 'player'
        ],
        "subtotal_before_globals": 50,
        "total": 50,
    }
    try:
        main.show_phase_result(result2)
        print("ERROR: Should have raised KeyError for missing 'player'!")
    except KeyError as e:
        print(f"Correctly raised KeyError: {e}")


def test_show_phase_result_zero_breakdown():
    """Breakdown entry with zero values."""
    print("\n=== TEST: show_phase_result with zero everything ===")
    result = {
        "phase_name": "All Zero",
        "breakdown": [
            {"player": "Ghost", "position": "GK", "base_chips": 0, "add_chips": 0,
             "multiply": 1.0, "fatigue": 1.0, "subtotal": 0},
        ],
        "subtotal_before_globals": 0,
        "total": 0,
        "fired_synergies": [],
        "synergy_contributors": {"__persistent__": ["Iron Will"]},
        "synergy_descriptions": {"Iron Will": "Trait-based boost"},
    }
    main.show_phase_result(result)


if __name__ == "__main__":
    print("=" * 60)
    print("UI DISPLAY PLAYTEST")
    print("=" * 60)

    tests = [
        test_player_short,
        test_color_for_fatigue,
        test_show_squad_full,
        test_show_field,
        test_show_phase_result,
        test_show_phase_result_missing_phase_name,
        test_show_phase_result_missing_breakdown,
        test_show_phase_result_missing_subtotal,
        test_show_phase_result_missing_total,
        test_show_phase_result_missing_breakdown_keys,
        test_show_phase_result_zero_breakdown,
        test_show_round_result,
        test_show_campaign_bracket,
        test_cprint,
        test_show_phase_header,
    ]

    failed = 0
    for test_fn in tests:
        try:
            test_fn()
        except Exception as e:
            print(f"\n*** FAILED: {test_fn.__name__}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {len(tests) - failed}/{len(tests)} passed, {failed} failed")
    print("=" * 60)

    if failed:
        sys.exit(1)
