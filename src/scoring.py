"""Scoring engine for Squad — Balatro-style chips × mult × x_mult.

PHASE SCORING FORMULA (Balatro-style):

  Player Chip Contribution = base_chips(chips_formula) * fatigue_mult
  Total Chips = SUM(player_chip_contributions) + total_pos_bonuses
              + synergy_chips + persistent_chips + carryover_chips

  Add Mult = 1 + synergy_add_mult   ← flat mult (like Balatro's +Mult jokers)
  X Mult = Π(synergy_x_mult) * Π(persistent_x_mult) * global_mult
                                      ← multiplicative (like Balatro's ×Mult jokers)

  Final = int(Total Chips * Add Mult * X Mult * formation_mult)

Phase-specific synergies are all stats-based, requiring 2+ complementary players.
"""

from collections import defaultdict
from src.cards import PlayerCard, SynergyCard, FormationCard


# ─── Position → Chips Formula ───────────────────────────────────────────
# Each position weights stats differently. ST cares about ATK+PAC,
# CB cares about DEF, CM cares about PAS, etc.

CHIPS_FORMULA = {
    "ST":  lambda p: p.atk * 4 + p.pac * 2 + p.spc * 1,
    "LW":  lambda p: p.atk * 2 + p.pac * 3 + p.pas * 1,
    "RW":  lambda p: p.atk * 2 + p.pac * 3 + p.pas * 1,
    "CM":  lambda p: p.pas * 3 + p.atk * 2 + p.def_ * 1,
    "CAM": lambda p: p.pas * 3 + p.atk * 2 + p.spc * 1,
    "CDM": lambda p: p.def_ * 2 + p.pas * 3 + p.atk * 1,
    "CB":  lambda p: p.def_ * 3 + p.pac * 2 + p.atk * 1,
    "FB":  lambda p: p.def_ * 2 + p.pac * 3 + p.pas * 1,
    "GK":  lambda p: p.def_ * 3 + p.spc * 1,
}


def calculate_chips(player: PlayerCard, field_position: str) -> int:
    """Calculate base chips for a player in a given field position."""
    formula = CHIPS_FORMULA.get(field_position)
    if formula is None:
        raise KeyError(f"Unknown position: {field_position}")
    return formula(player)


# ─── Helpers ─────────────────────────────────────────────────────────────

def _players_at(field, position: str) -> list[PlayerCard]:
    """Return all players fielded at a given position."""
    return [p for p, pos in field if pos == position]


def _best_at(field, position: str, stat: str) -> PlayerCard | None:
    """Return the best player at a position for a given stat, or None."""
    candidates = _players_at(field, position)
    if not candidates:
        return None
    return max(candidates, key=lambda p: getattr(p, stat, 0))


# ─── Synergy Detection (Phase-Level Accumulators) ───────────────────────
#
# Instead of per-player dicts, we now accumulate at the PHASE LEVEL:
#   chips    → added to the total chips pool
#   add_mult → added to the additive mult pool
#   x_mult   → multiplied against the mult pool
#
# This mirrors Balatro where chips and mult are separate pools that
# multiply each other at the end, enabling exponential scaling.

ATTACKER_POSITIONS = {"LW", "RW", "ST"}


def detect_synergies(
    field: list[tuple[PlayerCard, str]],
    synergy_cards: list[SynergyCard],
) -> dict:
    """Detect which synergies fire and return phase-level accumulators.

    Returns:
        Dict with:
          - chips: int — flat chips added to the total chips pool
          - add_mult: int — flat mult added to the additive mult pool
          - x_mult: float — multiplicative mult (product of all ×mult effects)
          - carryover: dict or None — next-phase carryover (e.g. Double Pivot)
          - fired_details: list[dict] — for UI display:
              [{
                  "name": "Clean Sheet",
                  "description": "...",
                  "effect_type": "chips" | "add_mult" | "x_mult",
                  "value": 20,
                  "contributors": ["Gigi Wall [GK]", "El Capitán [CB]"],
              }, ...]
    """
    players = [p for p, _ in field]

    # Phase-level accumulators
    chips = 0
    add_mult = 0
    x_mult = 1.0
    next_carryover = None
    fired_details = []

    def _add_detail(syn, effect_type: str, value, contrib_players: list):
        """Add a fired synergy to the details list."""
        contributors = [f"{p.name} [{pos}]" for p, pos in field if p in contrib_players]
        fired_details.append({
            "name": syn.name,
            "description": syn.description,
            "effect_type": effect_type,
            "value": value,
            "contributors": list(dict.fromkeys(contributors)),  # dedupe, preserve order
        })

    for syn in synergy_cards:
        if syn.persistent:
            continue  # persistent synergies are handled separately
        t = syn.trigger_type
        tr = syn.trigger
        eff = syn.effect

        # ── Clean Sheet (GK + CB) ──────────────────────────────────────
        if t == "clean_sheet":
            gk = _best_at(field, tr["pos_a"], tr["stat"])
            cb = _best_at(field, tr["pos_b"], tr["stat"])
            if gk and cb:
                total = getattr(gk, tr["stat"]) + getattr(cb, tr["stat"])
                if total >= tr["threshold"]:
                    val = eff.get("chips", eff.get("add_chips", 0))
                    chips += val
                    _add_detail(syn, "chips", val, [gk, cb])

        # ── Organised Defence (CB + CB) ────────────────────────────────
        elif t == "organised_defence":
            cbs = _players_at(field, tr["positions"][0])
            if len(cbs) >= 2:
                sorted_cbs = sorted(cbs, key=lambda p: getattr(p, tr["stat"]), reverse=True)
                if getattr(sorted_cbs[0], tr["stat"]) + getattr(sorted_cbs[1], tr["stat"]) >= tr["threshold"]:
                    val = eff.get("chips", eff.get("add_chips", 0))
                    chips += val
                    _add_detail(syn, "chips", val, [sorted_cbs[0], sorted_cbs[1]])

        # ── Wingback Overlap (FB PAC + CM PAS) ────────────────────────
        elif t == "wingback_overlap":
            fb = _best_at(field, tr["pos_a"], tr["stat_a"])
            cm = _best_at(field, tr["pos_b"], tr["stat_b"])
            if fb and cm:
                total = getattr(fb, tr["stat_a"]) + getattr(cm, tr["stat_b"])
                if total >= tr["threshold"]:
                    val = eff.get("chips", eff.get("add_chips", 0))
                    chips += val
                    _add_detail(syn, "chips", val, [fb, cm])

        # ── Overload (2+ same position) ───────────────────────────────
        elif t == "overload":
            pos_counts = defaultdict(list)
            for p, pos in field:
                pos_counts[pos].append(p)
            for pos, group in pos_counts.items():
                if len(group) >= tr.get("min_duplicates", 2):
                    val = eff.get("add_mult", 0)
                    add_mult += val
                    _add_detail(syn, "add_mult", val, group)

        # ── Stretch the Backline (FB PAC + LW PAC) ───────────────────
        elif t == "stretch_backline":
            fb = _best_at(field, tr["pos_a"], tr["stat_a"])
            lw = _best_at(field, tr["pos_b"], tr["stat_b"])
            if fb and lw:
                total = getattr(fb, tr["stat_a"]) + getattr(lw, tr["stat_b"])
                if total >= tr["threshold"]:
                    val = eff.get("x_mult", eff.get("multiply", 1.0))
                    x_mult *= val
                    _add_detail(syn, "x_mult", val, [fb, lw])

        # ── Route One (CB PAS + ST PAC → chips) ──────────────────────
        elif t == "route_one":
            cb = _best_at(field, tr["pos_a"], tr["stat_a"])
            st = _best_at(field, tr["pos_b"], tr["stat_b"])
            if cb and st:
                total = getattr(cb, tr["stat_a"]) + getattr(st, tr["stat_b"])
                if total >= tr["threshold"]:
                    val = eff.get("chips", eff.get("add_chips", 0))
                    chips += val
                    _add_detail(syn, "chips", val, [cb, st])

        # ── Battering Ram (CB DEF + ST ATK) ─────────────────────────
        elif t == "battering_ram":
            cb = _best_at(field, tr["pos_a"], tr["stat_a"])
            st = _best_at(field, tr["pos_b"], tr["stat_b"])
            if cb and st:
                total = getattr(cb, tr["stat_a"]) + getattr(st, tr["stat_b"])
                if total >= tr["threshold"]:
                    val = eff.get("chips", eff.get("add_chips", 0))
                    chips += val
                    _add_detail(syn, "chips", val, [cb, st])

        # ── Defensive Duo (2 highest DEF on field) ───────────────────
        elif t == "defensive_duo":
            if len(players) >= 2:
                sorted_players = sorted(players, key=lambda p: getattr(p, tr["stat"]), reverse=True)
                total = getattr(sorted_players[0], tr["stat"]) + getattr(sorted_players[1], tr["stat"])
                if total >= tr["threshold"]:
                    val = eff.get("add_mult", 0)
                    add_mult += val
                    _add_detail(syn, "add_mult", val, [sorted_players[0], sorted_players[1]])

        # ── Back Three (all DEF ≥ 7) ───────────────────────────────
        elif t == "back_three":
            if all(getattr(p, tr["stat"]) >= tr["threshold"] for p in players):
                val = eff.get("x_mult", eff.get("multiply", 1.0))
                x_mult *= val
                _add_detail(syn, "x_mult", val, players)

        # ── Midfield Engine (CM PAS + CM DEF) ────────────────────────
        elif t == "midfield_engine":
            cms = _players_at(field, tr["positions"][0])
            if len(cms) >= 2:
                sorted_by_pas = sorted(cms, key=lambda p: getattr(p, tr["stat_a"]), reverse=True)
                best_pas = sorted_by_pas[0]
                remaining = [p for p in cms if p.id != best_pas.id]
                best_def = max(remaining, key=lambda p: getattr(p, tr["stat_b"]))
                total = getattr(best_pas, tr["stat_a"]) + getattr(best_def, tr["stat_b"])
                if total >= tr["threshold"]:
                    val = eff.get("add_mult", 0)
                    add_mult += val
                    _add_detail(syn, "add_mult", val, [best_pas, best_def])

        # ── Double Pivot (2 CMs PAS sum ≥ 17 → next phase carryover) ───
        elif t == "double_pivot":
            cms = _players_at(field, tr["positions"][0])
            if len(cms) >= 2:
                sorted_cms = sorted(cms, key=lambda p: getattr(p, tr["stat"]), reverse=True)
                total = getattr(sorted_cms[0], tr["stat"]) + getattr(sorted_cms[1], tr["stat"])
                if total >= tr["threshold"]:
                    carry_chips = eff.get("chips", eff.get("add_chips", 40))
                    next_carryover = {
                        "type": "double_pivot",
                        "source_synergy": syn.name,
                        "chips": carry_chips,
                        "target_role": eff.get("target_role", "attacker"),
                    }
                    _add_detail(syn, "carryover", carry_chips, [sorted_cms[0], sorted_cms[1]])

        # ── Trio (all 3 CMs PAS ≥ 7, chain mults) ───────────────────
        elif t == "trio":
            cms = _players_at(field, tr["position"])
            if len(cms) >= 3:
                if all(getattr(p, tr["stat"]) >= tr["threshold"] for p in cms):
                    mults = eff.get("multipliers", [1.3, 1.5, 1.3])
                    # At phase level, chain multipliers combine into one ×mult
                    combined = 1.0
                    for m in mults:
                        combined *= m
                    x_mult *= combined
                    _add_detail(syn, "x_mult", combined, cms)

        # ── Covering Defender (CB PAC≥7 + another CB DEF≥9) ───────────
        elif t == "covering_defender":
            cbs = _players_at(field, tr["position"])
            if len(cbs) >= 2:
                pac_cbs = [p for p in cbs if getattr(p, tr["stat_a"]) >= tr["threshold_a"]]
                def_cbs = [p for p in cbs if getattr(p, tr["stat_b"]) >= tr["threshold_b"]]
                if pac_cbs and def_cbs:
                    fired = False
                    for fast_p in pac_cbs:
                        for strong_p in def_cbs:
                            if fast_p.id != strong_p.id:
                                val = eff.get("add_mult", 0)
                                add_mult += val
                                _add_detail(syn, "add_mult", val, [fast_p, strong_p])
                                fired = True
                                break
                        if fired:
                            break

        # ── Target Man Release (ST ATK + best winger PAC) ────────────
        elif t == "target_man_release":
            st = _best_at(field, tr["pos_a"], tr["stat_a"])
            winger_positions = tr.get("winger_positions", ["LW", "RW"])
            wingers = []
            for p, pos in field:
                if pos in winger_positions:
                    wingers.append(p)
            if st and wingers:
                best_winger = max(wingers, key=lambda p: getattr(p, tr["stat_b"], 0))
                total = getattr(st, tr["stat_a"]) + getattr(best_winger, tr["stat_b"])
                if total >= tr["threshold"]:
                    val = eff.get("x_mult", eff.get("multiply", 1.0))
                    x_mult *= val
                    _add_detail(syn, "x_mult", val, [st, best_winger])

        # ── Near Post Flick (CAM SPC + ST ATK) ────────────────────────
        elif t == "near_post_flick":
            cam = _best_at(field, tr["pos_a"], tr["stat_a"])
            st = _best_at(field, tr["pos_b"], tr["stat_b"])
            if cam and st:
                total = getattr(cam, tr["stat_a"]) + getattr(st, tr["stat_b"])
                if total >= tr["threshold"]:
                    val = eff.get("x_mult", eff.get("multiply", 1.0))
                    x_mult *= val
                    _add_detail(syn, "x_mult", val, [cam, st])

        # ── One-Two (CM PAS + ST PAC) ─────────────────────────────────
        elif t == "one_two":
            cm = _best_at(field, tr["pos_a"], tr["stat_a"])
            st = _best_at(field, tr["pos_b"], tr["stat_b"])
            if cm and st:
                total = getattr(cm, tr["stat_a"]) + getattr(st, tr["stat_b"])
                if total >= tr["threshold"]:
                    val = eff.get("x_mult", eff.get("multiply", 1.0))
                    x_mult *= val
                    _add_detail(syn, "x_mult", val, [cm, st])

        # ── Overlap (FB PAC + LW PAS) ──────────────────────────────────
        elif t == "overlap":
            fb = _best_at(field, tr["pos_a"], tr["stat_a"])
            lw = _best_at(field, tr["pos_b"], tr["stat_b"])
            if fb and lw:
                total = getattr(fb, tr["stat_a"]) + getattr(lw, tr["stat_b"])
                if total >= tr["threshold"]:
                    val = eff.get("x_mult", eff.get("multiply", 1.0))
                    x_mult *= val
                    _add_detail(syn, "x_mult", val, [fb, lw])

        # ── Set Piece Threat (DEF≥8 + SPC≥7, different players) ─────
        elif t == "set_piece_threat":
            def_players = [p for p in players if getattr(p, tr["stat_a"]) >= tr["threshold_a"]]
            spc_players = [p for p in players if getattr(p, tr["stat_b"]) >= tr["threshold_b"]]
            if def_players and spc_players:
                if tr.get("different_players", False):
                    for dp in def_players:
                        for sp in spc_players:
                            if dp.id != sp.id:
                                val = eff.get("chips", eff.get("add_chips", 0))
                                chips += val
                                _add_detail(syn, "chips", val, [dp, sp])
                                break
                        else:
                            continue
                        break

    return {
        "chips": chips,
        "add_mult": add_mult,
        "x_mult": x_mult,
        "carryover": next_carryover,
        "fired_details": fired_details,
    }


# ─── Synergy Preview Utilities ──────────────────────────────────────────

def get_fired_synergy_names(result: dict) -> set[str]:
    """Extract unique synergy names from a detect_synergies result, stripping qualifiers."""
    fired = set()
    for detail in result.get("fired_details", []):
        clean = detail["name"].split(" (")[0]
        fired.add(clean)
    return fired


def compute_synergy_preview(
    player, field_position: str,
    current_field: list, synergies: list,
) -> set[str]:
    """Return set of synergy names that would *additionally* fire if player
    were placed at field_position, compared to current_field alone."""
    from copy import deepcopy

    current_result = detect_synergies(list(current_field), synergies)
    current_fired = get_fired_synergy_names(current_result)

    new_field = list(current_field) + [(player, field_position)]
    new_result = detect_synergies(new_field, synergies)
    new_fired = get_fired_synergy_names(new_result)

    return new_fired - current_fired


def compute_synergy_potential(
    player, squad: list, synergies: list,
) -> list[str]:
    """Return synergy names this player can participate in, assuming all
    squad members were on the field at their natural positions."""
    field = [(p, p.position) for p in squad]
    result = detect_synergies(field, synergies)
    # A player contributes if they appear in any fired_detail's contributors
    involved = set()
    for detail in result.get("fired_details", []):
        for contrib in detail["contributors"]:
            if player.name in contrib:
                involved.add(detail["name"])
    return list(involved)


# ─── Squad-Persistent Synergy Detection ─────────────────────────────────

ATTACKER_POSITIONS = {"LW", "RW", "ST"}
MIDFIELDER_POSITIONS = {"CM", "CDM", "CAM"}
DEFENDER_POSITIONS = {"CB", "FB", "CDM"}


def detect_squad_synergies(
    squad: list[PlayerCard],
    synergy_cards: list[SynergyCard],
) -> dict:
    """Detect squad-persistent (trait-based) synergies and return buff dict.

    Checks the entire squad composition at match start.
    Effects persist for the whole match.

    Returns:
        dict with:
          - fatigue_penalty: float (default 0.7)
          - player_mult: dict[str, float] — player_id → multiplier
          - player_add: dict[str, int] — player_id → add_chips per phase
          - position_mult: dict[str, float] — position → multiplier
          - position_add: dict[str, int] — position → add_chips per phase
          - global_mult: float
          - global_add: int
          - journeyman_available: bool
          - fired_synergies: list[str]
    """
    buffs = {
        "fatigue_penalty": 0.7,
        "player_mult": {},
        "player_add": {},
        "position_mult": {},
        "position_add": {},
        "global_mult": 1.0,
        "global_add": 0,
        "journeyman_available": False,
        "fired_synergies": [],
    }

    # Index players by trait for quick lookup
    trait_to_players = defaultdict(list)
    for p in squad:
        for t in p.traits:
            trait_to_players[t].append(p)

    for syn in synergy_cards:
        if not syn.persistent:
            continue

        t = syn.trigger_type
        tr = syn.trigger
        eff = syn.effect

        if t == "squad_trait_count":
            trait = tr["trait"]
            min_count = tr.get("min_count", 1)
            matching = trait_to_players.get(trait, [])
            if len(matching) >= min_count:
                _apply_persistent_effect(buffs, syn, eff, matching, squad)

        elif t == "squad_trait_present":
            trait = tr["trait"]
            matching = trait_to_players.get(trait, [])
            if matching:
                _apply_persistent_effect(buffs, syn, eff, matching, squad)

        elif t == "squad_trait_combo":
            required_traits = tr["traits"]
            min_count = tr.get("min_count", 1)
            matching = [p for p in squad if all(t in p.traits for t in required_traits)]
            if len(matching) >= min_count:
                _apply_persistent_effect(buffs, syn, eff, matching, squad)

    return buffs


def _apply_persistent_effect(buffs: dict, syn, eff: dict,
                              matching_players: list, squad: list) -> None:
    """Apply a persistent synergy's effect to the buffs dict."""
    buffs["fired_synergies"].append(syn.name)
    etype = syn.effect_type

    # ── Fatigue penalty override ──
    if etype == "persistent_fatigue":
        penalty = eff.get("fatigue_penalty")
        if penalty is not None:
            buffs["fatigue_penalty"] = penalty

    # ── Per-player multiplier (targeted by trait) ──
    elif etype == "persistent_multiply":
        mult = eff.get("multiply", 1.0)

        target_trait = eff.get("target_trait")
        if target_trait:
            for p in squad:
                if target_trait in p.traits:
                    current = buffs["player_mult"].get(p.id, 1.0)
                    buffs["player_mult"][p.id] = current * mult

        target_combo = eff.get("target_trait_combo")
        if target_combo:
            for p in squad:
                if all(t in p.traits for t in target_combo):
                    current = buffs["player_mult"].get(p.id, 1.0)
                    buffs["player_mult"][p.id] = current * mult

        target_positions = eff.get("target_position", [])
        if target_positions:
            for pos in target_positions:
                current = buffs["position_mult"].get(pos, 1.0)
                buffs["position_mult"][pos] = current * mult

        fatigue = eff.get("fatigue_penalty")
        if fatigue is not None:
            buffs["fatigue_penalty"] = fatigue

    # ── Per-player add_chips (targeted by position or all) ──
    elif etype == "persistent_add":
        chips = eff.get("add_chips", 0)

        if eff.get("target") == "all":
            buffs["global_add"] += chips

        target_positions = eff.get("target_position", [])
        if target_positions:
            for pos in target_positions:
                current = buffs["position_add"].get(pos, 0)
                buffs["position_add"][pos] = current + chips

        target_combo = eff.get("target_trait_combo")
        if target_combo:
            for p in squad:
                if all(t in p.traits for t in target_combo):
                    current = buffs["player_add"].get(p.id, 0)
                    buffs["player_add"][p.id] = current + chips

    # ── Special effects ──
    elif etype == "persistent_special":
        special = eff.get("special")
        if special == "fatigue_reset":
            buffs["journeyman_available"] = True


# ─── Full Phase Score (Balatro-Style) ───────────────────────────────────
#
#   Total Chips = Σ(player_chips * fatigue) + Σ(position_bonus)
#               + synergy_chips + persistent_chips + carryover_chips
#
#   Add Mult  = 1 + synergy_add_mult
#   X Mult    = Π(synergy_x_mult) * Π(persistent_x_mult) * global_mult
#
#   Final = int(Total Chips * Add Mult * X Mult * formation_mult)
#

def calculate_round_score(
    field: list[tuple[PlayerCard, str]],
    synergy_cards: list[SynergyCard],
    formation: FormationCard | None = None,
    fatigue: dict[str, float] | None = None,
    carryover: dict | None = None,
    persistent_buffs: dict | None = None,
    momentum: float = 1.0,
    shop_buffs: dict | None = None,
) -> dict:
    """Calculate the phase score using Balatro-style chips × mult formula.

    Args:
        field: List of (player, field_position) for every slot on the pitch.
        synergy_cards: Active synergy/joker cards.
        formation: Optional formation card.
        fatigue: Optional map of player_id → multiplier (e.g. 0.7 for tired).
        carryover: Optional carryover bonus from previous phase.
        persistent_buffs: Persistent buffs from detect_squad_synergies.

    Returns:
        Dict with total, breakdown, synergy info, next_carryover.
    """
    if fatigue is None:
        fatigue = {}
    if persistent_buffs is None:
        persistent_buffs = {
            "player_mult": {}, "player_add": {},
            "position_mult": {}, "position_add": {},
            "global_mult": 1.0, "global_add": 0,
            "fired_synergies": [],
        }

    pb = persistent_buffs

    # ── Step 1: Player-level chip contributions (with fatigue + per-player buffs) ──
    player_chip_sum = 0
    breakdown = []
    all_fired: set[str] = set()

    for player, pos in field:
        base_chips = calculate_chips(player, pos)

        # Formation position bonus
        pos_bonus = formation.position_bonus.get(pos, 0) if formation else 0

        # Fatigue
        fatigue_mult = fatigue.get(player.id, 1.0)

        # Per-player persistent buffs
        pp_mult = pb.get("player_mult", {}).get(player.id, 1.0)
        pp_add = pb.get("player_add", {}).get(player.id, 0)

        # Position-based persistent buffs
        pos_mult = pb.get("position_mult", {}).get(pos, 1.0)
        pos_add = pb.get("position_add", {}).get(pos, 0)

        # Super Sub: fresh (100%) players get ×1.3 from shop item
        super_sub_mult = 1.0
        if shop_buffs and shop_buffs.get("super_sub_active") and fatigue_mult >= 1.0:
            super_sub_mult = 1.3

        # Player's effective chip contribution (fatigue, per-player buffs)
        effective_chips = (base_chips + pos_bonus + pos_add + pp_add) * fatigue_mult * pp_mult * pos_mult * super_sub_mult

        player_chip_sum += int(effective_chips)

        breakdown.append({
            "player": player.name,
            "position": pos,
            "base_chips": base_chips,
            "pos_bonus": pos_bonus,
            "persistent_add": pos_add + pp_add,
            "persistent_mult": round(pp_mult * pos_mult, 3),
            "fatigue": round(fatigue_mult, 2),
            "effective_chips": int(effective_chips),
        })

    # ── Step 2: Phase-level synergy detection ──
    syn_result = detect_synergies(field, synergy_cards)

    # Extract phase-level accumulators
    synergy_chips = syn_result["chips"]
    synergy_add_mult = syn_result["add_mult"]
    synergy_x_mult = syn_result["x_mult"]
    next_carryover = syn_result["carryover"]
    fired_details = syn_result["fired_details"]

    # ── Apply carryover bonus (e.g. Double Pivot → first attacker) ──
    carryover_chips = 0
    if carryover:
        target_role = carryover.get("target_role", "attacker")
        source_name = carryover.get("source_synergy", "Carryover")
        carryover_chips = carryover.get("chips", carryover.get("add_chips", 0))

        if target_role == "attacker":
            # Apply to first attacker on the field
            attacker_found = False
            for player, pos in field:
                if pos in ATTACKER_POSITIONS:
                    attacker_found = True
                    break
            if attacker_found:
                fired_details.append({
                    "name": f"{source_name} (carryover)",
                    "description": f"Carryover from previous phase: +{carryover_chips} chips",
                    "effect_type": "chips",
                    "value": carryover_chips,
                    "contributors": ["Previous phase"],
                })
            else:
                # No attacker on field — carryover doesn't apply
                carryover_chips = 0

    # ── Step 4: Apply persistent global effects ──
    persistent_chips = pb.get("global_add", 0)
    persistent_x_mult = pb.get("global_mult", 1.0)

    # ── Step 4b: Apply shop buffs ──
    shop_chips = 0
    shop_add_mult = 0
    if shop_buffs:
        shop_chips = shop_buffs.get("extra_chips", 0)
        shop_add_mult = shop_buffs.get("extra_add_mult", 0)

    # ── Step 5: Bask in glory — Balatro-style formula ──
    total_chips = player_chip_sum + synergy_chips + carryover_chips + persistent_chips + shop_chips
    add_mult = 1 + synergy_add_mult + shop_add_mult
    x_mult = synergy_x_mult * persistent_x_mult
    formation_mult = formation.global_mult if formation else 1.0

    # Subtotal for display
    subtotal_before_formation = int(total_chips * add_mult * x_mult)
    final_total = int(total_chips * add_mult * x_mult * formation_mult * momentum)

    # ── Step 6: Build synergy tracking ──
    # Collect all fired synergy names for the summary
    for detail in fired_details:
        all_fired.add(detail["name"])
    for name in pb.get("fired_synergies", []):
        all_fired.add(name)

    # Invert fired_details into synergy_contributors for display
    synergy_contributors: dict[str, list[str]] = {}
    for detail in fired_details:
        name = detail["name"]
        if detail["contributors"]:
            synergy_contributors[name] = detail["contributors"]

    # Add persistent synergy info
    persistent_names = pb.get("fired_synergies", [])
    if persistent_names:
        synergy_contributors["__persistent__"] = list(persistent_names)

    # Build synergy name → description map
    synergy_descriptions: dict[str, str] = {}
    for syn in synergy_cards:
        if syn.name in all_fired:
            synergy_descriptions[syn.name] = syn.description
    for detail in fired_details:
        if detail["name"] not in synergy_descriptions and "(carryover)" not in detail["name"]:
            synergy_descriptions[detail["name"]] = detail["description"]

    return {
        "total": final_total,
        "breakdown": breakdown,
        "player_chip_sum": player_chip_sum,
        "synergy_chips": synergy_chips,
        "carryover_chips": carryover_chips,
        "persistent_chips": persistent_chips,
        "total_chips": total_chips,
        "add_mult": add_mult,
        "x_mult": round(x_mult, 3),
        "formation_mult": formation_mult,
        "formation_name": formation.name if formation else "",
        "subtotal_before_formation": subtotal_before_formation,
        "fired_synergies": sorted(all_fired),
        "fired_details": fired_details,
        "next_carryover": next_carryover,
        "synergy_contributors": synergy_contributors,
        "synergy_descriptions": synergy_descriptions,
        "momentum": momentum,
        "shop_chips": shop_chips,
        "shop_add_mult": shop_add_mult,
    }
