#!/usr/bin/env python3
"""Playtest: squad builder edge cases + player/synergy/formation data integrity.

Usage: cd /home/hermes/games/squad && source .venv/bin/activate && python3 tools/playtest_data.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from collections import Counter
from pathlib import Path

# Ensure we can import from src/
sys.path.insert(0, str(Path(__file__).parent))

from src.loader import load_players, load_synergies
from src.squad_builder import BUDGET, MIN_TOTAL, ROLE_GROUPS, check_minimums
from src.formations import FORMATIONS, get_all_formations
from src.cards import PlayerCard, SynergyCard, FormationCard

# ─── Phase-specific trigger types defined in detect_synergies ───
# These must be handled by the scoring engine.
PHASE_TRIGGER_TYPES = {
    "clean_sheet",
    "organised_defence",
    "wingback_overlap",
    "overload",
    "stretch_backline",
    "route_one",
    "battering_ram",
    "defensive_duo",
    "back_three",
    "midfield_engine",
    "double_pivot",
    "trio",
    "covering_defender",
    "target_man_release",
    "near_post_flick",
    "one_two",
    "overlap",
    "set_piece_threat",
}

# ─── Persistent trigger types handled in detect_squad_synergies ───
PERSISTENT_TRIGGER_TYPES = {
    "squad_trait_count",
    "squad_trait_present",
    "squad_trait_combo",
}

VALID_EFFECT_TYPES = {
    # Phase-specific
    "add_chips",
    "multiply",
    "carryover",
    "chain_multiply",
    # Persistent
    "persistent_multiply",
    "persistent_add",
    "persistent_fatigue",
    "persistent_special",
}

VALID_POSITIONS = {"GK", "CB", "FB", "CDM", "CM", "CAM", "LW", "RW", "ST"}
VALID_STATS = {"atk", "pac", "pas", "atk", "pac", "pas"}  # not normalized

# ═══════════════════════════════════════════════════════════════════════════
# Test Harness
# ═══════════════════════════════════════════════════════════════════════════

passed = 0
failed = 0

def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}  — {detail}")

def section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


# ═══════════════════════════════════════════════════════════════════════════
# 1. Squad Builder Edge Cases
# ═══════════════════════════════════════════════════════════════════════════
section("1. SQUAD BUILDER — EDGE CASES")

# 1a. Empty squad
missing = check_minimums([])
check("Empty squad returns 5 missing requirements", len(missing) == 5,
      f"got {len(missing)}: {missing}")
check("Empty squad reports missing GK", any("GK" in m for m in missing))
check("Empty squad reports missing Defenders", any("Defender" in m for m in missing))
check("Empty squad reports missing Midfielders", any("Midfielder" in m for m in missing))
check("Empty squad reports missing Attackers", any("Attacker" in m for m in missing))
check("Empty squad reports < 10 players", any("10 players" in m for m in missing))

# 1b. Squad with only 9 players (all roles met but not 10)
players = load_players()
# Pick 9 valid players that satisfy role groups
nine_squad = []
for p in players:
    pos = p.position
    if pos == "GK" and sum(1 for q in nine_squad if q.position == "GK") < 1:
        nine_squad.append(p)
    elif pos == "ST" and sum(1 for q in nine_squad if q.position == "ST") < 2:
        nine_squad.append(p)
    elif pos == "CM" and sum(1 for q in nine_squad if q.position == "CM") < 3:
        nine_squad.append(p)
    elif pos == "CB" and sum(1 for q in nine_squad if q.position == "CB") < 3:
        nine_squad.append(p)
    if len(nine_squad) >= 9:
        break

check("9-player squad with valid roles still reports under 10",
      len(check_minimums(nine_squad)) == 1 and "10 players" in check_minimums(nine_squad)[0],
      f"got: {check_minimums(nine_squad)}")

# 1c. Squad with wrong positions (e.g., 10 STs, no GK)
all_strikers = [p for p in players if p.position == "ST"][:10]
striker_missing = check_minimums(all_strikers)
check("10 STs — missing GK, Defenders, Midfielders",
      all(phrase in str(striker_missing) for phrase in ["GK", "Defender", "Midfielder"]),
      f"got: {striker_missing}")

# 1d. Minimum boundary: exactly meeting role group minimums
minimal_squad = []
# Find 1 GK
gk = [p for p in players if p.position == "GK"][0]
minimal_squad.append(gk)
# Find 3 CBs (Defenders: CB/FB)
cbs = [p for p in players if p.position == "CB"][:3]
minimal_squad.extend(cbs)
# Find 3 CMs (Midfielders: CM/CDM/CAM)
cms = [p for p in players if p.position == "CM"][:3]
minimal_squad.extend(cms)
# Find 2 STs (Attackers: ST/LW/RW)
sts = [p for p in players if p.position == "ST"][:2]
minimal_squad.extend(sts)
# Now we have 9 — need 1 more to reach 10, any position works
extra = [p for p in players if p not in minimal_squad][0]
minimal_squad.append(extra)

check("Exactly-meeting minimums squad passes check",
      len(check_minimums(minimal_squad)) == 0,
      f"missing: {check_minimums(minimal_squad)}")
check(f"Exactly-meeting squad has {len(minimal_squad)} players (≥ {MIN_TOTAL})",
      len(minimal_squad) >= MIN_TOTAL)

# 1e. Budget constraint check (squad total cost vs BUDGET)
squad_cost = sum(p.cost for p in minimal_squad)
check("Minimal squad cost computed correctly from card costs",
      squad_cost > 0,
      f"cost: {squad_cost}")

# Find the cheapest 10 players and verify budget
sorted_by_cost = sorted(players, key=lambda p: p.cost)
cheapest_10 = sorted_by_cost[:10]
cheapest_cost = sum(p.cost for p in cheapest_10)
check(f"Cheapest 10 players cost ({cheapest_cost}) <= budget ({BUDGET})",
      cheapest_cost <= BUDGET,
      f"cheapest_10 cost: {cheapest_cost}")

# Most expensive 10 players
most_expensive_10 = sorted(players, key=lambda p: p.cost, reverse=True)[:10]
expensive_cost = sum(p.cost for p in most_expensive_10)
check(f"Most expensive 10 players cost ({expensive_cost}) fits within budget ({BUDGET})",
      expensive_cost <= BUDGET,
      f"expensive cost: {expensive_cost} > budget: {BUDGET}")

# 1f. Role group counting accuracy
pos_counts = Counter(p.position for p in minimal_squad)
for group_name, cfg in ROLE_GROUPS.items():
    total = sum(pos_counts.get(pos, 0) for pos in cfg["positions"])
    check(f"Role group '{group_name}' count: {total} >= {cfg['min']}",
          total >= cfg["min"],
          f"count: {total}, min: {cfg['min']}")

# 1g. ROLE_GROUPS structure validation
check("ROLE_GROUPS contains all 4 groups", set(ROLE_GROUPS.keys()) == {"GK", "Defenders", "Midfielders", "Attackers"})
for gn, cfg in ROLE_GROUPS.items():
    check(f"  {gn}: has 'positions' list", "positions" in cfg)
    check(f"  {gn}: has 'min' int", isinstance(cfg.get("min"), int))
    check(f"  {gn}: min > 0", cfg["min"] > 0)
    for pos in cfg["positions"]:
        check(f"  {gn}: position '{pos}' is valid", pos in VALID_POSITIONS, f"unknown: {pos}")


# ═══════════════════════════════════════════════════════════════════════════
# 2. Player Data Integrity
# ═══════════════════════════════════════════════════════════════════════════
section("2. PLAYER DATA INTEGRITY")

players = load_players()
print(f"\n  Loaded {len(players)} players")

# 2a. No duplicate IDs
ids = [p.id for p in players]
dupes = [id_ for id_, count in Counter(ids).items() if count > 1]
check("No duplicate player IDs", len(dupes) == 0,
      f"duplicates: {dupes}")

# 2b. All have valid positions
for p in players:
    check(f"  Player '{p.id}' position '{p.position}' is valid",
          p.position in VALID_POSITIONS,
          f"invalid position: {p.position}")

# 2c. Stats in range 1-10
for p in players:
    for stat_name in ["atk", "pac", "pas", "def_", "spc"]:
        val = getattr(p, stat_name)
        check(f"  {p.id}.{stat_name} = {val} in [1,10]",
              1 <= val <= 10,
              f"out of range: {val}")

# 2d. Cost = sum of stats
for p in players:
    expected_cost = p.atk + p.pac + p.pas + p.def_ + p.spc
    check(f"  {p.id} cost={p.cost} == sum of stats ({expected_cost})",
          p.cost == expected_cost,
          f"got cost={p.cost}, sum={expected_cost}")

# 2e. Each player has traits as a list
for p in players:
    check(f"  {p.id} traits is list ({len(p.traits)} items)",
          isinstance(p.traits, list),
          f"type: {type(p.traits)}")

# 2f. Position distribution
pos_counts = Counter(p.position for p in players)
print(f"\n  Position distribution:")
for pos in sorted(VALID_POSITIONS):
    count = pos_counts.get(pos, 0)
    icon = "✅" if count > 0 else "⬜"
    print(f"    {icon} {pos:4s}: {count} players")
check("Every position has at least 1 player", all(pos_counts.get(p, 0) > 0 for p in VALID_POSITIONS),
      f"missing positions: {[p for p in VALID_POSITIONS if pos_counts.get(p, 0) == 0]}")

# 2g. Unique trait inventory
all_traits = set()
for p in players:
    all_traits.update(p.traits)
print(f"\n  All traits across players: {sorted(all_traits)}")

# 2h. Cost range
min_cost = min(p.cost for p in players)
max_cost = max(p.cost for p in players)
avg_cost = sum(p.cost for p in players) / len(players)
check(f"Player costs in range [{min_cost}, {max_cost}] (avg {avg_cost:.1f})", min_cost >= 5)


# ═══════════════════════════════════════════════════════════════════════════
# 3. Synergy Data Integrity
# ═══════════════════════════════════════════════════════════════════════════
section("3. SYNERGY DATA INTEGRITY")

synergies = load_synergies()
print(f"\n  Loaded {len(synergies)} synergies")

# 3a. No duplicate synergy IDs
syn_ids = [s.id for s in synergies]
syn_dupes = [id_ for id_, count in Counter(syn_ids).items() if count > 1]
check("No duplicate synergy IDs", len(syn_dupes) == 0,
      f"duplicates: {syn_dupes}")

# 3b. All have valid trigger_type
phase_count = 0
persistent_count = 0
unknown_triggers = []
for s in synergies:
    t = s.trigger_type
    if t in PHASE_TRIGGER_TYPES:
        phase_count += 1
    elif t in PERSISTENT_TRIGGER_TYPES:
        persistent_count += 1
    else:
        unknown_triggers.append(t)

check("All trigger_types are known",
      len(unknown_triggers) == 0,
      f"unknown: {unknown_triggers}")
check(f"Phase-specific synergies: {phase_count}", phase_count > 0)
check(f"Persistent synergies: {persistent_count}", persistent_count > 0)

# 3c. persistent flag matches trigger type
for s in synergies:
    is_persistent_trigger = s.trigger_type in PERSISTENT_TRIGGER_TYPES
    check(f"  {s.id}: persistent={s.persistent} matches trigger_type={s.trigger_type}",
          s.persistent == is_persistent_trigger,
          f"mismatch: persistent={s.persistent}, trigger={s.trigger_type}")

# 3d. All have valid effect_type
for s in synergies:
    check(f"  {s.id}: effect_type '{s.effect_type}' valid",
          s.effect_type in VALID_EFFECT_TYPES,
          f"unknown effect_type: {s.effect_type}")

# 3e. All have valid rarity
VALID_RARITIES = {"common", "uncommon", "rare"}
for s in synergies:
    check(f"  {s.id}: rarity '{s.rarity}' valid",
          s.rarity in VALID_RARITIES,
          f"unknown rarity: {s.rarity}")

# 3f. Persistent synergies have effect_type matching pattern
for s in synergies:
    if s.persistent:
        check(f"  {s.id}: persistent effect_type starts with 'persistent_'",
              s.effect_type.startswith("persistent_"),
              f"effect_type: {s.effect_type}")

# 3g. Phase-specific synergies have non-"persistent_" effect_types
for s in synergies:
    if not s.persistent:
        check(f"  {s.id}: non-persistent effect_type is '{s.effect_type}'",
              s.effect_type in ("add_chips", "multiply", "carryover", "chain_multiply"),
              f"unexpected: {s.effect_type}")

# 3h. All have descriptions
for s in synergies:
    check(f"  {s.id}: has description", bool(s.description and s.description.strip()),
          f"empty description")

# 3i. All have trigger dict
for s in synergies:
    check(f"  {s.id}: trigger is dict", isinstance(s.trigger, dict),
          f"type: {type(s.trigger)}")

# 3j. All have effect dict with content
for s in synergies:
    check(f"  {s.id}: effect is dict with keys {list(s.effect.keys())}",
          isinstance(s.effect, dict) and len(s.effect) > 0,
          f"type: {type(s.effect)}, empty: {len(s.effect) == 0}")

# 3k. Rarity distribution
rarity_counts = Counter(s.rarity for s in synergies)
print(f"\n  Synergy rarity distribution:")
for r in ["common", "uncommon", "rare"]:
    print(f"    {r:12s}: {rarity_counts.get(r, 0)}")
total_syn = sum(rarity_counts.values())
check(f"Total synergies: {total_syn}", total_syn > 0)

# 3l. Index synergies by name for uniqueness
syn_name_counts = Counter(s.name for s in synergies)
name_dupes = {n: c for n, c in syn_name_counts.items() if c > 1}
check(f"All synergy names unique", len(name_dupes) == 0,
      f"dupes: {name_dupes}")


# ═══════════════════════════════════════════════════════════════════════════
# 4. Formation Data Integrity
# ═══════════════════════════════════════════════════════════════════════════
section("4. FORMATION DATA INTEGRITY")

formations = get_all_formations()
print(f"\n  Loaded {len(formations)} formations")

# 4a. Each formation has slots that are valid positions
for f in formations:
    check(f"  {f.id}: has slots ({len(f.slots)} slots)", len(f.slots) > 0)
    for slot in f.slots:
        check(f"  {f.id}: slot '{slot}' is valid position",
              slot in VALID_POSITIONS,
              f"unknown: {slot}")

# 4b. Formation names match their IDs
for f in formations:
    check(f"  {f.id}: name matches ID", f.name == f.id,
          f"name: '{f.name}' != id: '{f.id}'")

# 4c. position_bonus references valid positions
for f in formations:
    for pos, bonus in f.position_bonus.items():
        check(f"  {f.id}: position_bonus '{pos}' is valid position",
              pos in VALID_POSITIONS,
              f"unknown: {pos}")
        check(f"  {f.id}: position_bonus '{pos}' = {bonus} (non-zero)",
              bonus != 0,
              f"zero bonus")

# 4d. global_mult is sensible
for f in formations:
    check(f"  {f.id}: global_mult={f.global_mult} is float >= 0.5",
          isinstance(f.global_mult, (int, float)) and f.global_mult >= 0.5,
          f"invalid: {f.global_mult}")

# 4e. Hand size is reasonable
for f in formations:
    check(f"  {f.id}: hand_size={f.hand_size} >= slot count ({len(f.slots)})",
          f.hand_size >= len(f.slots),
          f"hand_size: {f.hand_size}, slots: {len(f.slots)}")

# 4f. No duplicate formation IDs
form_ids = [f.id for f in formations]
form_dupes = [id_ for id_, count in Counter(form_ids).items() if count > 1]
check("No duplicate formation IDs", len(form_dupes) == 0)

# 4g. Each formation has a description
for f in formations:
    check(f"  {f.id}: has description", bool(f.description and f.description.strip()))

# 4h. Formation slot distribution analysis
for f in formations:
    slot_counts = Counter(f.slots)
    print(f"\n    {f.id}: {f.description}")
    for pos in sorted(slot_counts):
        print(f"      {pos}: {slot_counts[pos]}")

# 4i. Check the FORMATIONS dict vs get_all_formations
form_dict_ids = set(FORMATIONS.keys())
form_list_ids = {f.id for f in get_all_formations()}
check("FORAMTIONS dict keys match get_all_formations IDs",
      form_dict_ids == form_list_ids,
      f"dict: {form_dict_ids}, list: {form_list_ids}")

# 4j. Verify each formation's total slots is reasonable (7-12)
for f in formations:
    check(f"  {f.id}: {len(f.slots)} slots in range [7,12]",
          7 <= len(f.slots) <= 12,
          f"slots: {len(f.slots)}")


# ═══════════════════════════════════════════════════════════════════════════
# FINAL REPORT
# ═══════════════════════════════════════════════════════════════════════════
section("FINAL REPORT")
total = passed + failed
print(f"\n  Passed: {passed}/{total}")
print(f"  Failed: {failed}/{total}")
if failed > 0:
    print(f"\n  ⚠️  {failed} CHECK(S) FAILED — see details above.")
else:
    print(f"\n  ✅ ALL CHECKS PASSED — data layer is clean.")
print()

sys.exit(0 if failed == 0 else 1)
