"""Scoring engine for Squad — chips × mult × fatigue, synergy detection, round calculation.

The heart of the game. Every score flows through here.
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


# ─── Synergy Detection ──────────────────────────────────────────────────

ATTACKER_POSITIONS = {"LW", "RW", "ST"}


def detect_synergies(
    field: list[tuple[PlayerCard, str]],
    synergy_cards: list[SynergyCard],
) -> dict:
    """Detect which synergies fire and return per-player multiplier effects.

    Returns:
        Dict keyed by player.id, each value is a dict with:
          - 'multiply': cumulative multiplier (start at 1.0)
          - 'add_chips': cumulative flat chip bonus (start at 0)
          - 'fired_synergies': list of synergy names that triggered
        Plus '__global__' key with global mult/add.
        Plus '__carryover__' key if a carryover synergy fired.
    """
    players = [p for p, _ in field]
    player_map = {p.id: p for p in players}

    # Per-player results
    results: dict[str, dict] = {
        p.id: {"multiply": 1.0, "add_chips": 0, "fired_synergies": []}
        for p in players
    }

    global_mult = 1.0
    global_add = 0
    next_carryover = None  # For Double Pivot

    for syn in synergy_cards:
        t = syn.trigger_type
        tr = syn.trigger
        eff = syn.effect

        # ── Clean Sheet (GK + CB) ──────────────────────────────────────
        if t == "clean_sheet":
            gk = _best_at(field, tr["pos_a"], tr["stat"])  # "GK"
            cb = _best_at(field, tr["pos_b"], tr["stat"])  # "CB"
            if gk and cb:
                total = getattr(gk, tr["stat"]) + getattr(cb, tr["stat"])
                if total >= tr["threshold"]:
                    for p in (gk, cb):
                        results[p.id]["add_chips"] += eff.get("add_chips", 0)
                        results[p.id]["fired_synergies"].append(syn.name)

        # ── Organised Defence (CB + CB) ────────────────────────────────
        elif t == "organised_defence":
            cbs = _players_at(field, tr["positions"][0])  # "CB"
            if len(cbs) >= 2:
                sorted_cbs = sorted(cbs, key=lambda p: getattr(p, tr["stat"]), reverse=True)
                if getattr(sorted_cbs[0], tr["stat"]) + getattr(sorted_cbs[1], tr["stat"]) >= tr["threshold"]:
                    for p in (sorted_cbs[0], sorted_cbs[1]):
                        results[p.id]["add_chips"] += eff.get("add_chips", 0)
                        results[p.id]["fired_synergies"].append(syn.name)

        # ── Wingback Overlap (FB PAC + CM PAS) ────────────────────────
        elif t == "wingback_overlap":
            fb = _best_at(field, tr["pos_a"], tr["stat_a"])   # FB, pac
            cm = _best_at(field, tr["pos_b"], tr["stat_b"])   # CM, pas
            if fb and cm:
                total = getattr(fb, tr["stat_a"]) + getattr(cm, tr["stat_b"])
                if total >= tr["threshold"]:
                    for p in (fb, cm):
                        results[p.id]["add_chips"] += eff.get("add_chips", 0)
                        results[p.id]["fired_synergies"].append(syn.name)

        # ── Overload (2+ same position) ───────────────────────────────
        elif t == "overload":
            pos_counts = defaultdict(list)
            for p, pos in field:
                pos_counts[pos].append(p)
            for pos, group in pos_counts.items():
                if len(group) >= tr.get("min_duplicates", 2):
                    for p in group:
                        results[p.id]["add_chips"] += eff.get("add_chips", 0)
                        results[p.id]["fired_synergies"].append(syn.name)

        # ── Stretch the Backline (FB PAC + LW PAC) ───────────────────
        elif t == "stretch_backline":
            fb = _best_at(field, tr["pos_a"], tr["stat_a"])   # FB, pac
            lw = _best_at(field, tr["pos_b"], tr["stat_b"])   # LW, pac
            if fb and lw:
                total = getattr(fb, tr["stat_a"]) + getattr(lw, tr["stat_b"])
                if total >= tr["threshold"]:
                    for p in (fb, lw):
                        results[p.id]["multiply"] *= eff.get("multiply", 1.0)
                        results[p.id]["fired_synergies"].append(syn.name)

        # ── Route One (CB PAS + ST PAC → ST gets chips) ──────────────
        elif t == "route_one":
            cb = _best_at(field, tr["pos_a"], tr["stat_a"])   # CB, pas
            st = _best_at(field, tr["pos_b"], tr["stat_b"])   # ST, pac
            if cb and st:
                total = getattr(cb, tr["stat_a"]) + getattr(st, tr["stat_b"])
                if total >= tr["threshold"]:
                    # Only ST gets the bonus
                    target = eff.get("target", "ST")
                    if target == "ST":
                        results[st.id]["add_chips"] += eff.get("add_chips", 0)
                        results[st.id]["fired_synergies"].append(syn.name)
                    results[cb.id]["fired_synergies"].append(syn.name)

        # ── Battering Ram (CB DEF + ST ATK) ─────────────────────────
        elif t == "battering_ram":
            cb = _best_at(field, tr["pos_a"], tr["stat_a"])   # CB, def_
            st = _best_at(field, tr["pos_b"], tr["stat_b"])   # ST, atk
            if cb and st:
                total = getattr(cb, tr["stat_a"]) + getattr(st, tr["stat_b"])
                if total >= tr["threshold"]:
                    for p in (cb, st):
                        results[p.id]["add_chips"] += eff.get("add_chips", 0)
                        results[p.id]["fired_synergies"].append(syn.name)

        # ── Defensive Duo (2 highest DEF on field) ───────────────────
        elif t == "defensive_duo":
            if len(players) >= 2:
                sorted_players = sorted(players, key=lambda p: getattr(p, tr["stat"]), reverse=True)
                total = getattr(sorted_players[0], tr["stat"]) + getattr(sorted_players[1], tr["stat"])
                if total >= tr["threshold"]:
                    for p in players:
                        results[p.id]["add_chips"] += eff.get("add_chips", 0)
                        results[p.id]["fired_synergies"].append(syn.name)

        # ── Back Three (all 3 DEF ≥ 7) ───────────────────────────────
        elif t == "back_three":
            if all(getattr(p, tr["stat"]) >= tr["threshold"] for p in players):
                for p in players:
                    results[p.id]["multiply"] *= eff.get("multiply", 1.0)
                    results[p.id]["fired_synergies"].append(syn.name)

        # ── Midfield Engine (CM PAS + CM DEF) ────────────────────────
        elif t == "midfield_engine":
            cms = _players_at(field, tr["positions"][0])
            if len(cms) >= 2:
                # Find best PAS CM...
                sorted_by_pas = sorted(cms, key=lambda p: getattr(p, tr["stat_a"]), reverse=True)
                best_pas = sorted_by_pas[0]
                # ...and best DEF CM among the REMAINING players (must be different)
                remaining = [p for p in cms if p.id != best_pas.id]
                best_def = max(remaining, key=lambda p: getattr(p, tr["stat_b"]))
                total = getattr(best_pas, tr["stat_a"]) + getattr(best_def, tr["stat_b"])
                if total >= tr["threshold"]:
                    for p in (best_pas, best_def):
                        results[p.id]["add_chips"] += eff.get("add_chips", 0)
                        results[p.id]["fired_synergies"].append(syn.name)

        # ── Double Pivot (2 CMs PAS sum ≥ 17 → next phase carryover) ───
        elif t == "double_pivot":
            cms = _players_at(field, tr["positions"][0])
            if len(cms) >= 2:
                sorted_cms = sorted(cms, key=lambda p: getattr(p, tr["stat"]), reverse=True)
                total = getattr(sorted_cms[0], tr["stat"]) + getattr(sorted_cms[1], tr["stat"])
                if total >= tr["threshold"]:
                    # Set carryover for next phase
                    next_carryover = {
                        "type": "double_pivot",
                        "source_synergy": syn.name,
                        "add_chips": eff.get("add_chips", 40),
                        "target_role": eff.get("target_role", "attacker"),
                    }
                    for p in (sorted_cms[0], sorted_cms[1]):
                        results[p.id]["fired_synergies"].append(syn.name)

        # ── Trio (all 3 CMs PAS ≥ 7, chain mults) ───────────────────
        elif t == "trio":
            cms = _players_at(field, tr["position"])
            if len(cms) >= 3:
                if all(getattr(p, tr["stat"]) >= tr["threshold"] for p in cms):
                    sorted_cms = sorted(cms, key=lambda p: getattr(p, tr["stat"]), reverse=True)
                    mults = eff.get("multipliers", [1.3, 1.5, 1.3])
                    for i, p in enumerate(sorted_cms):
                        mult_idx = min(i, len(mults) - 1)
                        results[p.id]["multiply"] *= mults[mult_idx]
                        results[p.id]["fired_synergies"].append(f"{syn.name} (×{mults[mult_idx]})")

        # ── Covering Defender (CB PAC≥7 + another CB DEF≥9) ───────────
        elif t == "covering_defender":
            cbs = _players_at(field, tr["position"])  # "CB"
            if len(cbs) >= 2:
                pac_cbs = [p for p in cbs if getattr(p, tr["stat_a"]) >= tr["threshold_a"]]  # pac ≥ 7
                def_cbs = [p for p in cbs if getattr(p, tr["stat_b"]) >= tr["threshold_b"]]  # def_ ≥ 9
                if pac_cbs and def_cbs:
                    fired = False
                    for fast_p in pac_cbs:
                        for strong_p in def_cbs:
                            if fast_p.id != strong_p.id:
                                for p in (fast_p, strong_p):
                                    results[p.id]["add_chips"] += eff.get("add_chips", 0)
                                    results[p.id]["fired_synergies"].append(syn.name)
                                fired = True
                                break
                        if fired:
                            break

        # ── Target Man Release (ST ATK + best winger PAC) ────────────
        elif t == "target_man_release":
            st = _best_at(field, tr["pos_a"], tr["stat_a"])  # ST, atk
            winger_positions = tr.get("winger_positions", ["LW", "RW"])
            wingers = []
            for p, pos in field:
                if pos in winger_positions:
                    wingers.append(p)
            if st and wingers:
                best_winger = max(wingers, key=lambda p: getattr(p, tr["stat_b"], 0))
                total = getattr(st, tr["stat_a"]) + getattr(best_winger, tr["stat_b"])
                if total >= tr["threshold"]:
                    results[best_winger.id]["multiply"] *= eff.get("multiply", 1.0)
                    results[best_winger.id]["fired_synergies"].append(syn.name)
                    results[st.id]["fired_synergies"].append(syn.name)

        # ── Near Post Flick (CAM SPC + ST ATK → ST gets mult) ────────
        elif t == "near_post_flick":
            cam = _best_at(field, tr["pos_a"], tr["stat_a"])  # CAM, spc
            st = _best_at(field, tr["pos_b"], tr["stat_b"])   # ST, atk
            if cam and st:
                total = getattr(cam, tr["stat_a"]) + getattr(st, tr["stat_b"])
                if total >= tr["threshold"]:
                    results[st.id]["multiply"] *= eff.get("multiply", 1.0)
                    results[st.id]["fired_synergies"].append(syn.name)
                    results[cam.id]["fired_synergies"].append(syn.name)

        # ── One-Two (CM PAS + ST PAC → both get mult) ─────────────────
        elif t == "one_two":
            cm = _best_at(field, tr["pos_a"], tr["stat_a"])  # CM, pas
            st = _best_at(field, tr["pos_b"], tr["stat_b"])  # ST, pac
            if cm and st:
                total = getattr(cm, tr["stat_a"]) + getattr(st, tr["stat_b"])
                if total >= tr["threshold"]:
                    for p in (cm, st):
                        results[p.id]["multiply"] *= eff.get("multiply", 1.0)
                        results[p.id]["fired_synergies"].append(syn.name)

        # ── Overlap (FB PAC + LW PAS → FB gets mult) ──────────────────
        elif t == "overlap":
            fb = _best_at(field, tr["pos_a"], tr["stat_a"])  # FB, pac
            lw = _best_at(field, tr["pos_b"], tr["stat_b"])  # LW, pas
            if fb and lw:
                total = getattr(fb, tr["stat_a"]) + getattr(lw, tr["stat_b"])
                if total >= tr["threshold"]:
                    results[fb.id]["multiply"] *= eff.get("multiply", 1.0)
                    results[fb.id]["fired_synergies"].append(syn.name)
                    results[lw.id]["fired_synergies"].append(syn.name)

        # ── Set Piece Threat (DEF≥9 + SPC≥8, different) ─────────────
        elif t == "set_piece_threat":
            def_players = [p for p in players if getattr(p, tr["stat_a"]) >= tr["threshold_a"]]
            spc_players = [p for p in players if getattr(p, tr["stat_b"]) >= tr["threshold_b"]]
            if def_players and spc_players:
                # Check they're different players
                if tr.get("different_players", False):
                    if not all(p.id in {pp.id for pp in spc_players} for p in def_players):
                        # There's at least one player who is in def_players but not all def_players are in spc_players
                        # This is too complex. Let me simplify: check if there exists a pair of different players
                        for dp in def_players:
                            for sp in spc_players:
                                if dp.id != sp.id:
                                    global_add += eff.get("add_chips", 0)
                                    for p in players:
                                        results[p.id]["fired_synergies"].append(syn.name)
                                    break
                            else:
                                continue
                            break
                    # If all def_players are in spc_players (i.e. same players qualify for both), don't fire
                else:
                    # If not requiring different players, any single player with both qualifies
                    # But we don't have this case anymore
                    pass

    # Attach global effects
    results["__global__"] = {"global_mult": global_mult, "global_add": global_add}
    if next_carryover:
        results["__carryover__"] = next_carryover

    return results


# ─── Synergy Preview Utilities ──────────────────────────────────────────

def get_fired_synergy_names(result: dict) -> set[str]:
    """Extract unique synergy names from a detect_synergies result, stripping qualifiers."""
    fired = set()
    for pid, stats in result.items():
        if pid in ("__global__", "__carryover__"):
            continue
        for raw_name in stats.get("fired_synergies", []):
            clean = raw_name.split(" (")[0]
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
    return result.get(player.id, {}).get("fired_synergies", [])


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

        # ── Squad trait count (N+ players with a trait) ──────────────
        if t == "squad_trait_count":
            trait = tr["trait"]
            min_count = tr.get("min_count", 1)
            matching = trait_to_players.get(trait, [])
            if len(matching) >= min_count:
                _apply_persistent_effect(buffs, syn, eff, matching, squad)

        # ── Squad trait present (at least 1 player with a trait) ─────
        elif t == "squad_trait_present":
            trait = tr["trait"]
            matching = trait_to_players.get(trait, [])
            if matching:
                _apply_persistent_effect(buffs, syn, eff, matching, squad)

        # ── Squad trait combo (N+ players with ALL specified traits) ─
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

        # Target by trait
        target_trait = eff.get("target_trait")
        if target_trait:
            for p in squad:
                if target_trait in p.traits:
                    current = buffs["player_mult"].get(p.id, 1.0)
                    buffs["player_mult"][p.id] = current * mult

        # Target by trait combo
        target_combo = eff.get("target_trait_combo")
        if target_combo:
            for p in squad:
                if all(t in p.traits for t in target_combo):
                    current = buffs["player_mult"].get(p.id, 1.0)
                    buffs["player_mult"][p.id] = current * mult

        # Target by position
        target_positions = eff.get("target_position", [])
        if target_positions:
            for pos in target_positions:
                current = buffs["position_mult"].get(pos, 1.0)
                buffs["position_mult"][pos] = current * mult

    # ── Per-player add_chips (targeted by position or all) ──
    elif etype == "persistent_add":
        chips = eff.get("add_chips", 0)

        # Target all players
        if eff.get("target") == "all":
            buffs["global_add"] += chips

        # Target by position
        target_positions = eff.get("target_position", [])
        if target_positions:
            for pos in target_positions:
                current = buffs["position_add"].get(pos, 0)
                buffs["position_add"][pos] = current + chips

        # Target by trait combo
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


# ─── Full Round Score ───────────────────────────────────────────────────

def calculate_round_score(
    field: list[tuple[PlayerCard, str]],
    synergy_cards: list[SynergyCard],
    formation: FormationCard | None = None,
    fatigue: dict[str, float] | None = None,
    carryover: dict | None = None,
    persistent_buffs: dict | None = None,
) -> dict:
    """Calculate the phase score: chips × mult × fatigue × formation.

    Args:
        field: List of (player, field_position) for every slot on the pitch.
        synergy_cards: Active synergy/joker cards.
        formation: Optional formation card.
        fatigue: Optional map of player_id → multiplier (e.g. 0.7 for tired).
        carryover: Optional carryover bonus from a previous phase (e.g. Double Pivot).
        persistent_buffs: Optional persistent buffs from squad-persistent synergies.

    Returns:
        Dict with total, breakdown, global effects, fired synergies, next_carryover.
    """
    if fatigue is None:
        fatigue = {}
    if persistent_buffs is None:
        persistent_buffs = {
            "player_mult": {}, "player_add": {},
            "position_mult": {}, "position_add": {},
            "global_mult": 1.0, "global_add": 0,
        }

    synergies = detect_synergies(field, synergy_cards)
    global_meta = synergies.pop("__global__", {"global_mult": 1.0, "global_add": 0})
    next_carryover = synergies.pop("__carryover__", None)

    # ── Apply carryover bonus (e.g. Double Pivot → first attacker) ──
    if carryover:
        target_role = carryover.get("target_role", "attacker")
        source_name = carryover.get("source_synergy", "Carryover")
        bonus_chips = carryover.get("add_chips", 0)

        if target_role == "attacker":
            for player, pos in field:
                if pos in ATTACKER_POSITIONS:
                    if player.id not in synergies:
                        synergies[player.id] = {"multiply": 1.0, "add_chips": 0, "fired_synergies": []}
                    synergies[player.id]["add_chips"] += bonus_chips
                    synergies[player.id]["fired_synergies"].append(f"{source_name} (carryover)")
                    break

    # ── Apply persistent buffs (squad-persistent synergies) ─────────
    pb = persistent_buffs

    # Combine global multipliers
    combined_global_mult = global_meta["global_mult"] * pb.get("global_mult", 1.0)
    combined_global_add = global_meta["global_add"] + pb.get("global_add", 0)

    # Track which persistent synergy names are active
    persistent_names = set()
    for p in field:
        pid = p[0].id
        # Per-player mult from persistent buffs
        if pid in pb.get("player_mult", {}):
            if pid not in synergies:
                synergies[pid] = {"multiply": 1.0, "add_chips": 0, "fired_synergies": []}
            synergies[pid]["multiply"] *= pb["player_mult"][pid]
        # Per-player add_chips from persistent buffs
        if pid in pb.get("player_add", {}):
            if pid not in synergies:
                synergies[pid] = {"multiply": 1.0, "add_chips": 0, "fired_synergies": []}
            synergies[pid]["add_chips"] += pb["player_add"][pid]

    for player, pos in field:
        pid = player.id
        # Position-based persistent buffs
        pos_mult = pb.get("position_mult", {}).get(pos, 1.0)
        pos_add = pb.get("position_add", {}).get(pos, 0)

        if pos_mult != 1.0 or pos_add != 0:
            if pid not in synergies:
                synergies[pid] = {"multiply": 1.0, "add_chips": 0, "fired_synergies": []}
            synergies[pid]["multiply"] *= pos_mult
            synergies[pid]["add_chips"] += pos_add

    # Collect persistent synergy names for the fired listing
    for name in pb.get("fired_synergies", []):
        for pid in synergies:
            if pid in ("__global__", "__carryover__"):
                continue
            synergies[pid]["fired_synergies"].append(f"{name} (persistent)")

    # ── Build synergy → player(s) contributor map ──────────────────
    # Invert the per-player fired_synergies so we know which players
    # contributed to each synergy.
    synergy_contributors: dict[str, list[str]] = {}
    for player, pos in field:
        pid = player.id
        if pid in synergies:
            for raw_name in synergies[pid].get("fired_synergies", []):
                clean_name = raw_name.split(" (")[0]
                entry = f"{player.name} [{pos}]"
                if clean_name not in synergy_contributors:
                    synergy_contributors[clean_name] = []
                if entry not in synergy_contributors[clean_name]:
                    synergy_contributors[clean_name].append(entry)

    # Also include persistent synergy information (which squad traits enabled them)
    persistent_names = pb.get("fired_synergies", [])
    if persistent_names:
        synergy_contributors["__persistent__"] = list(persistent_names)

    # Formation multiplier
    formation_mult = formation.global_mult if formation else 1.0

    breakdown = []
    total = 0
    all_fired: set[str] = set()

    for player, pos in field:
        base_chips = calculate_chips(player, pos)

        # Formation position bonus
        pos_bonus = formation.position_bonus.get(pos, 0) if formation else 0
        base_chips += pos_bonus

        player_syn = synergies.get(player.id, {"multiply": 1.0, "add_chips": 0, "fired_synergies": []})

        # Fatigue
        fatigue_mult = fatigue.get(player.id, 1.0)

        chips_with_bonus = base_chips + player_syn["add_chips"]
        after_mult = chips_with_bonus * player_syn["multiply"] * fatigue_mult

        all_fired.update(player_syn["fired_synergies"])
        breakdown.append({
            "player": player.name,
            "position": pos,
            "base_chips": base_chips,
            "add_chips": player_syn["add_chips"],
            "multiply": round(player_syn["multiply"], 2),
            "fatigue": round(fatigue_mult, 2),
            "subtotal": round(after_mult),
        })
        total += after_mult

    # Store subtotal before global/formation multipliers
    subtotal_before_globals = int(total)

    # ── Build synergy name → description map ──────────────────────
    # So the display can show "what rule" each synergy met.
    synergy_descriptions: dict[str, str] = {}
    for syn in synergy_cards:
        if syn.name in all_fired or syn.name in persistent_names:
            synergy_descriptions[syn.name] = syn.description

    # Global effects (phase-specific × persistent)
    total = total * combined_global_mult + combined_global_add
    total = int(total * formation_mult)

    return {
        "total": total,
        "breakdown": breakdown,
        "subtotal_before_globals": subtotal_before_globals,
        "formation_mult": formation_mult,
        "formation_name": formation.name if formation else "",
        "global_mult": round(combined_global_mult, 3),
        "global_add": combined_global_add,
        "fired_synergies": sorted(all_fired),
        "next_carryover": next_carryover,
        "synergy_contributors": synergy_contributors,
        "synergy_descriptions": synergy_descriptions,
    }
