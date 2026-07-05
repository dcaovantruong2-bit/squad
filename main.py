#!/usr/bin/env python3
"""Squad — Football Card Roguelike (Phase-Based Terminal MVP)

5-match tournament campaign. Each match = 3 rounds × 6 random phases of play.
Per phase: field 2-5 players from your squad. Wrong position? Stats gate players instead.
Fatigue ×0.7 per use. 28 synergies: 18 phase-specific (stats-based) + 10 squad-persistent (trait-based).
Difficulty escalates: Group Stage → Round of 16 → QF → SF → Final. Win all 5 = champion.
"""

from src.loader import load_all
from src.squad_builder import build_squad
from src.formations import get_all_formations
from src.match import (MatchState, create_match, start_round, start_phase,
                       place_player, resolve_phase,
                       advance_phase, check_round,
                       CAMPAIGN_MATCHES)
from src.phases import (slot_positions, slot_label, is_player_eligible)
from src.scoring import (detect_squad_synergies, calculate_chips,
                         compute_synergy_preview, calculate_round_score)


# ─── Rich formatting (optional) ──────────────────────────────────────
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def cprint(text: str, style: str = "", end: str = "\n") -> None:
    if HAS_RICH:
        console.print(text, style=style, end=end)
    else:
        print(text, end=end)


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


# ─── Display Helpers ─────────────────────────────────────────────────

def player_short(p, fatigue_mult: float = 1.0) -> str:
    """Compact player display with optional fatigue indicator."""
    line = f"{p.name:18s} [{p.position:3s}] ATK:{p.atk} PAC:{p.pac} PAS:{p.pas} DEF:{p.def_} SPC:{p.spc}"
    if fatigue_mult < 1.0:
        line += f" [dim]({int(fatigue_mult*100)}%)[/dim]"
    return line


def color_for_fatigue(mult: float) -> str:
    if mult >= 1.0:
        return "green"
    elif mult >= 0.7:
        return "yellow"
    else:
        return "red"


# ─── Squad Display ────────────────────────────────────────────────────

def show_squad_full(squad: list, fatigue: dict) -> None:
    """Show full squad with fatigue levels."""
    cprint(f"\n  [bold]SQUAD ({len(squad)}):[/bold]", style="bold")
    from collections import defaultdict
    by_pos = defaultdict(list)
    for p in squad:
        by_pos[p.position].append(p)

    for label in ["GK", "CB", "FB", "CDM", "CM", "LW", "RW", "ST"]:
        players = by_pos.get(label, [])
        if players:
            cprint(f"  [bold underline]{label}[/bold underline]", style="cyan")
            for p in players:
                fm = fatigue.get(p.id, 1.0)
                color = color_for_fatigue(fm)
                status = " [FRESH]" if fm >= 1.0 else f" [{int(fm*100)}%]"
                cprint(f"    {p.name:20s}  {status}", style=color)


# ─── Phase Display ────────────────────────────────────────────────────

def show_phase_header(phase, phase_idx: int, round_num: int, target: int,
                       round_score: int, round_won: int, round_lost: int,
                       carryover: dict | None = None) -> None:
    """Show the current phase header."""
    clear_screen()
    weight_icons = {"DEF": "🛡️", "PAS": "🔄", "PAC": "⚡", "ATK": "🎯", "SPC": "✨"}
    icon = weight_icons.get(phase.weight, "⚽")
    slots_str = " → ".join(slot_label(s) for s in phase.slots)
    cprint(f"\n  ╔═══════════════════════════════════════════════════╗", style="bold cyan")
    cprint(f"  ║  ROUND {round_num}/3  —  Phase {phase_idx+1}/6                ║", style="bold cyan")
    cprint(f"  ║  Target: {target:4d}  |  Score: {round_score:4d}  ({round_won}-{round_lost})  ║", style="bold cyan")
    cprint(f"  ╚═══════════════════════════════════════════════════╝", style="bold cyan")
    cprint(f"\n  {icon} [bold]{phase.name}[/bold] — {phase.description}", style="bold yellow")
    cprint(f"  Slots needed: {slots_str}  |  Cards: {len(phase.slots)}", style="dim")
    # Show carryover bonus from previous phase
    if carryover:
        bonus = carryover.get("add_chips", 0)
        source = carryover.get("source_synergy", "Previous phase")
        cprint(f"\n  ⚡ [bold yellow]CARRYOVER:[/bold yellow] {source} — "
               f"first attacker gets +{bonus} chips!", style="bold yellow")


def show_field(field: list[tuple], fatigue: dict) -> None:
    """Show current field placements."""
    if not field:
        cprint("\n  [No players placed yet]", style="dim")
        return

    cprint("\n  [bold]ON THE PITCH:[/bold]", style="bold green")
    for i, (player, pos) in enumerate(field):
        chips = calculate_chips(player, pos)
        fm = fatigue.get(player.id, 1.0)
        fatigue_str = f" {int(fm*100)}%" if fm < 1.0 else " fresh"
        line = (f"    [{i}] {pos:4s} | {player.name:18s} | {chips:3d} chips"
                f" | fatigue:{fatigue_str}")
        cprint(line)


# ─── Phase Score Display ──────────────────────────────────────────────

def show_phase_result(result: dict) -> None:
    """Show detailed scoring result for a phase with full math breakdown."""
    cprint(f"\n  ═══ [bold]{result['phase_name']}[/bold] RESULT ═══", style="bold yellow")

    for entry in result["breakdown"]:
        # Build formula string showing every component
        base = entry['base_chips']
        add = entry['add_chips']
        mult = entry['multiply']
        fat = entry['fatigue']

        parts = [f"  {base:3d} base"]
        if add:
            parts.append(f"+{add:2d} syn")
        else:
            parts.append(f" +0 syn")
        if mult != 1.0:
            parts.append(f"×{mult:.2f} mult")
        else:
            parts.append(f"×1.00 mult")
        if fat != 1.0:
            parts.append(f"×{fat:.2f} fat")
        else:
            parts.append(f"×1.00 fat")
        parts.append(f"= {entry['subtotal']:4d}")

        line = (f"  {entry['player']:20s} →{entry['position']:3s}: "
                + "  ".join(parts))
        cprint(line, style="cyan" if entry['fatigue'] >= 1.0 else "yellow")

    cprint(f"  {'─' * 58}", style="dim")
    cprint(f"  {'Sum':20s} {'':13s} {result['subtotal_before_globals']:4d}",
           style="bold")

    if result.get("global_mult", 1.0) != 1.0:
        cprint(f"  × {'Global mult':20s} {'':13s} ×{result['global_mult']}",
               style="magenta")
    if result.get("global_add", 0) != 0:
        cprint(f"  + {'Global bonus':20s} {'':13s} +{result['global_add']}",
               style="magenta")
    if result.get("formation_mult", 1.0) != 1.0:
        cprint(f"  × {'Formation':20s} ({result.get('formation_name', '')})  "
               f"{'':13s} ×{result['formation_mult']}",
               style="cyan")

    cprint(f"  {'═' * 58}", style="bold yellow")
    cprint(f"  [bold]PHASE TOTAL:[/bold] {result['total']:4d}",
           style="bold green")
    if result.get("fired_synergies"):
        # Only show phase-specific synergies (filter out persistent ones)
        phase_syns = [s for s in result["fired_synergies"] if "(persistent)" not in s]
        if not phase_syns:
            return

        cprint(f"  ⚡ {'Synergies:':20s} {', '.join(phase_syns)}",
               style="yellow")
        # Show which players enabled each synergy and the rule met
        contributors = result.get("synergy_contributors", {})
        descriptions = result.get("synergy_descriptions", {})
        for syn_name in phase_syns:
            clean_name = syn_name.split(" (")[0]
            if clean_name in contributors and clean_name != "__persistent__":
                players = contributors[clean_name]
                desc = descriptions.get(clean_name, "")
                cprint(f"      {clean_name:22s} → {', '.join(players)}",
                       style="dim")
                if desc:
                    cprint(f"      {'':22s}   {desc}", style="dim")


def show_round_result(score: int, target: int, won: bool) -> None:
    """Show round result."""
    if won:
        cprint(f"\n  🎉 [bold green]ROUND WON![/bold green] {score} / {target}", style="bold green")
    else:
        cprint(f"\n  💔 [bold red]ROUND LOST[/bold red] {score} / {target}", style="bold red")


# ─── Phase Placement UI ───────────────────────────────────────────────

def select_slot_player(squad, fatigue, phase_slot, used_ids, current_field, synergies,
                        carryover: dict | None = None,
                        journeyman_available: bool = False,
                        journeyman_used_ref: list = None) -> object | None:
    """Let user pick a player from squad to fill one phase slot.

    Shows eligible players with chip preview and synergy tags for this slot.
    Uses a loop so invalid input loops back instead of crashing.
    """
    eligible = [p for p in squad
                if p.id not in used_ids and is_player_eligible(p, phase_slot)]

    if not eligible:
        cprint(f"\n  [red]No eligible players for {slot_label(phase_slot)}![/red]", style="red")
        cprint(f"  Need: {slot_label(phase_slot)}", style="dim")
        return None

    while True:
        cprint(f"\n  [bold]Fill: {slot_label(phase_slot)}[/bold]", style="bold")
        for i, p in enumerate(eligible):
            fm = fatigue.get(p.id, 1.0)
            status = "FRESH" if fm >= 1.0 else f"{int(fm*100)}%"

            # Determine field position for chip calculation
            slot_positions_list = slot_positions(phase_slot)
            if isinstance(phase_slot, dict):
                # Stat-based slot: always play as the "as" position
                slot_pos = phase_slot["as"]
            else:
                # Position-based slot: use natural position if valid
                slot_pos = p.position if p.position in slot_positions_list else slot_positions_list[0]

            chips = calculate_chips(p, slot_pos)
            effective = int(chips * fm)  # After fatigue

            # Check which synergies this player would unlock
            new_syns = compute_synergy_preview(p, slot_pos, current_field, synergies)
            syn_tag = ""
            if new_syns:
                syn_str = ", ".join(sorted(new_syns)[:2])
                syn_tag = f" ⚡{syn_str}"
                if len(new_syns) > 2:
                    syn_tag += f"+{len(new_syns)-2}"

            # Carryover tag — show if this player would benefit from carryover bonus
            carry_tag = ""
            if carryover and slot_pos in ("LW", "RW", "ST"):
                bonus = carryover.get("add_chips", 0)
                carry_tag = f" 📦+{bonus}"

            cprint(f"    [{i}] {p.name:20s} [{p.position}]→{slot_pos:3s}  {status:5s}  "
                   f"→ {effective:3d} chips{' (ø) ' if fm < 1.0 else '     '}"
                   f"ATK:{p.atk} PAC:{p.pac} PAS:{p.pas} DEF:{p.def_} SPC:{p.spc}"
                   f"{syn_tag}{carry_tag}",
                   style=color_for_fatigue(fm))

        # Show journeyman availability hint
        if journeyman_available and journeyman_used_ref is not None and not journeyman_used_ref[0]:
            cprint("  (type 'reset <#>' to fully restore a tired player -- once per match)", style="dim")

        try:
            raw = input("  Pick # (or 'skip' to pass this slot): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if raw == 'skip':
            return None

        # Journeyman: reset a player's fatigue
        if raw.startswith('reset '):
            if not journeyman_available or journeyman_used_ref is None or journeyman_used_ref[0]:
                cprint("  Journeyman already used or not available!", style="red")
                continue
            try:
                reset_idx = int(raw.split()[1])
            except (ValueError, IndexError):
                cprint("  Usage: reset <#>, e.g. 'reset 3'", style="red")
                continue
            if 0 <= reset_idx < len(squad):
                reset_p = squad[reset_idx]
                fatigue[reset_p.id] = 1.0
                journeyman_used_ref[0] = True
                cprint(f"  ✅ [bold]Journeyman:[/bold] {reset_p.name} fully restored!", style="bold green")
                continue
            else:
                cprint(f"  Invalid squad index. Pick 0-{len(squad)-1}.", style="red")
                continue

        try:
            idx = int(raw)
        except ValueError:
            cprint(f"  Type a number (0-{len(eligible)-1}) or 'skip'. Got '{raw}'.",
                   style="red")
            continue

        if 0 <= idx < len(eligible):
            return eligible[idx]
        else:
            cprint(f"  Number out of range. Pick 0-{len(eligible)-1}.", style="red")
            # Loop continues — user gets another try


def run_phase_placement(match: MatchState) -> None:
    """Run the placement phase — fill each slot one by one."""
    phase = match.current_phase
    if phase is None:
        return

    for slot_def in phase.slots:
        # Show current state
        show_phase_header(phase, match.current_phase_idx,
                          match.current_round + 1, match.current_target,
                          match.round_score, match.rounds_won, match.rounds_lost,
                          carryover=match.carryover)
        show_field(match.field, match.fatigue)

        # If this slot already filled (shouldn't happen but guard)
        if len(match.field) >= phase.max_cards:
            cprint("\n  [bold green]All slots for this phase filled![/bold green]", style="bold")
            input("  Press Enter to continue...")
            break

        placed_ids = {p.id for p, _ in match.field}
        journeyman_avail = bool(match.persistent_buffs and match.persistent_buffs.get("journeyman_available"))
        journeyman_ref = [match.journeyman_used]
        player = select_slot_player(match.squad, match.fatigue, slot_def, placed_ids,
                                     match.field, match.synergies,
                                     carryover=match.carryover,
                                     journeyman_available=journeyman_avail,
                                     journeyman_used_ref=journeyman_ref)
        match.journeyman_used = journeyman_ref[0]

        if player is None:
            continue  # Skip this slot

        # Determine the actual position they'll play
        valid = slot_positions(slot_def)
        if len(valid) == 1:
            slot_pos = valid[0]
        else:
            # Multiple positions possible — use player's natural position if valid
            if player.position in valid:
                slot_pos = player.position
            else:
                slot_pos = valid[0]

        place_player(match, player, slot_pos)

        # ── LIVE SCORE PREVIEW ──
        # Recalculate phase score with current field to show running total
        preview = calculate_round_score(match.field, match.synergies, fatigue=match.fatigue)
        preview_total = preview["total"]
        cprint(f"\n  [bold]→ Phase running: {preview_total} pts[/bold]"
               f"  (from {len(match.field)}/{phase.max_cards} cards)",
               style="bold cyan")
        if preview.get("fired_synergies"):
            cprint(f"    ⚡ {', '.join(preview['fired_synergies'])} active",
                   style="yellow")
        # Show per-player breakdown inline
        for entry in preview["breakdown"]:
            fatigue_str = f" ×{entry['fatigue']}" if entry['fatigue'] < 1.0 else ""
            cprint(f"      {entry['player']:18s} [{entry['position']:3s}] "
                   f"→ {entry['subtotal']:4d} pts"
                   f"  (base {entry['base_chips']}{' +'+str(entry['add_chips']) if entry['add_chips'] else ''}"
                   f" ×{entry['multiply']}{fatigue_str})",
                   style="dim")

        # Wait for player to acknowledge before next slot
        if len(match.field) < phase.max_cards:
            cprint("  Press Enter to continue filling...", style="dim")
            input()

    # Phase placement done
    show_phase_header(phase, match.current_phase_idx,
                      match.current_round + 1, match.current_target,
                      match.round_score, match.rounds_won, match.rounds_lost,
                      carryover=match.carryover)
    show_field(match.field, match.fatigue)
    cprint("\n  [bold green]Phase field set![/bold green]", style="bold")
    input("  Press Enter to score this phase...")


# ─── Formation Selection ─────────────────────────────────────────────

def select_formation(squad) -> object:
    """Let the player pick a formation. Shows fit score based on squad."""
    formations = get_all_formations()

    cprint("\n  ╔═══════════════════════════════════════════════════╗", style="bold cyan")
    cprint(  "  ║         Choose Your Formation                    ║", style="bold cyan")
    cprint(  "  ╚═══════════════════════════════════════════════════╝", style="bold cyan")

    # Pre-compute fit scores
    def formation_fit(f, squad):
        """Return (score, reasons) tuple for how well a formation fits the squad."""
        score = 0
        reasons = []

        # Count position bonuses utilized
        for pos, bonus in f.position_bonus.items():
            count = sum(1 for p in squad if p.position == pos)
            if bonus > 0 and count > 0:
                score += count * count * 2
                reasons.append(f"+{count}×{pos} get +{bonus}")
            elif bonus < 0 and count > 0:
                score -= count * count * 2
                reasons.append(f"⚠ {count}×{pos} penalised {bonus}")

        # Squad composition scoring
        cms = [p for p in squad if p.position == "CM"]
        pas8_cms = sum(1 for p in cms if p.pas >= 8)
        wingers = [p for p in squad if p.position in ("LW", "RW")]
        pacey_wingers = sum(1 for p in wingers if "pacey" in p.traits)
        clinical_wingers = sum(1 for p in wingers if "clinical" in p.traits)
        fbs = [p for p in squad if p.position == "FB"]
        pacey_fbs = sum(1 for p in fbs if "pacey" in p.traits)
        sts = [p for p in squad if p.position == "ST"]
        cbs = [p for p in squad if p.position == "CB"]
        phys_sts = sum(1 for p in sts if "physical" in p.traits)

        if f.id == "4-4-2":
            if len(sts) >= 2:
                q = min(len(sts), 4)
                score += q * q * 3
                reasons.append(f"{len(sts)} STs")
            if phys_sts >= 1:
                score += 15
                reasons.append("Physical ST → Big Man")

        elif f.id == "4-3-3":
            if pas8_cms >= 3:
                score += 30
                reasons.append(f"{pas8_cms} CMs PAS8+ → Tiki-Taka")
            if pacey_wingers >= 1 or clinical_wingers >= 1:
                score += 20
                reasons.append("Wingers → Cut Inside/Overlap")
            if len(squad) > 0:
                score += 10  # General attacking bonus

        elif f.id == "5-3-2":
            if len(cbs) >= 3:
                score += 25
                reasons.append(f"{len(cbs)} CBs + CDM → Defensive Shield")
            if len(sts) >= 2:
                score += 15
                reasons.append(f"{len(sts)} STs")
            if phys_sts >= 1:
                score += 10
                reasons.append("Physical ST → Big Man")

        elif f.id == "3-4-3":
            if len(wingers) >= 2:
                score += 25
                reasons.append(f"{len(wingers)} wingers")
            if pacey_fbs >= 1:
                score += 10
                reasons.append("Pacey FB → Overlap")
            if pacey_wingers >= 1 or clinical_wingers >= 1:
                score += 15
                reasons.append("Wingers → Cut Inside/Overlap")
            score += 15  # High-risk reward bonus

        elif f.id == "4-2-3-1":
            cams = [p for p in squad if p.position == "CAM"]
            if cams:
                score += 30
                reasons.append(f"{len(cams)} CAMs → No.10 role")
            if pas8_cms >= 2:
                score += 20
                reasons.append(f"{pas8_cms} CMs PAS8+ → Double pivot")
            tech_players = sum(1 for p in squad if "technical" in p.traits)
            if tech_players >= 3:
                score += 15
                reasons.append("Technical players → Possession")

        elif f.id == "4-5-1":
            cdms = [p for p in squad if p.position == "CDM"]
            if cdms:
                score += 20
                reasons.append(f"{len(cdms)} CDMs → Screen")
            if pacey_wingers >= 2:
                score += 25
                reasons.append(f"{pacey_wingers} pacey wingers → Counter")
            if len(sts) == 1:
                score += 5
                reasons.append("1 ST → Lone striker")

        return score, reasons

    scored = []
    for i, f in enumerate(formations):
        score, reasons = formation_fit(f, squad)
        scored.append((score, i, f, reasons))

    scored.sort(key=lambda x: -x[0])
    best_score = scored[0][0] if scored else 0

    for score, i, f, reasons in scored:
        is_best = score > 0 and score == best_score
        star = " ⭐" if is_best else ""
        # Show bonuses in green, penalties in red
        if f.position_bonus:
            parts = []
            for pos, bonus in f.position_bonus.items():
                style = "bold green" if bonus > 0 else "bold red"
                parts.append(f"[{style}]{pos}: {bonus:+d}[/{style}]")
            bonus_str = "  ".join(parts)
            desc = f"  [{i}] [bold]{f.name:6s}[/bold]  {bonus_str}{star}"
        else:
            desc = f"  [{i}] [bold]{f.name:6s}[/bold]  [dim]Balanced[/dim]{star}"
        cprint(desc, style="bold yellow" if is_best else "yellow")
        cprint(f"      {f.description}", style="dim")
        if score > 0 and reasons:
            cprint(f"      📊 Fit: {', '.join(reasons[:3])}", style="cyan")
    cprint(f"\n      ⭐ = recommended for your squad", style="dim")

    try:
        choice = input("\n  Pick formation # (default 0): ").strip()
        if choice == "":
            idx = 0
        else:
            idx = int(choice)
        if 0 <= idx < len(formations):
            return formations[idx]
        else:
            cprint(f"  Number out of range. Pick 0-{len(formations)-1}. Defaulting to 0.",
                   style="red")
            return formations[0]
    except ValueError:
        cprint(f"  Invalid input. Defaulting to 4-4-2.", style="red")
        return formations[0]


# ─── Main Game Loop ───────────────────────────────────────────────────

def play_match(match: MatchState) -> bool:
    """Play a full match (3 rounds, each with 6 phases). Returns True if won."""
    round_num = 0

    while not match.is_match_over and round_num < 3:
        match.current_round = round_num
        start_round(match)

        # Show this round's 5 random phase synergies
        if match.synergies:
            cprint(f"\n  [bold]Round {round_num+1} Synergies:[/bold]", style="bold yellow")
            for s in match.synergies:
                cprint(f"    ✦ {s.name} [{s.rarity}] — {s.description}", style="yellow")

        # Run 6 phases
        for phase_idx in range(6):
            match.current_phase_idx = phase_idx
            start_phase(match)
            run_phase_placement(match)
            result = resolve_phase(match)

            # Show phase result
            clear_screen()
            show_phase_result(result)
            cprint(f"\n  Running total: {match.round_score} (target: {match.current_target})", style="dim")

            # AUTO-WIN: if we've already reached the target, skip remaining phases
            if match.round_score >= match.current_target:
                cprint(f"\n  🎯 [bold green]TARGET REACHED! Auto-winning round![/bold green]", style="bold green")
                input("  Press Enter to advance to next round...")
                break

            input("\n  Press Enter for next phase...")

            if phase_idx < 5:
                advance_phase(match)

        advance_phase(match)  # Marks round complete

        # Check round result
        won = check_round(match)
        clear_screen()
        show_round_result(match.round_score, match.current_target, won)
        cprint(f"\n  Round phases:")
        for i, pr in enumerate(match.phase_results):
            cprint(f"    Phase {i+1}: {pr['phase_name']:15s} → {pr['total']:4d} pts")
        cprint(f"    {'─'*30}\n    {'Total':15s} → {match.round_score:4d} / {match.current_target}")

        if not match.is_match_over:
            cprint(f"\n  Match: {match.rounds_won}-{match.rounds_lost}", style="bold")
            input("\n  Press Enter for next round...")

        round_num += 1

    # Match result
    clear_screen()
    if match.is_match_won:
        cprint(f"\n  🏆 [bold green]MATCH WON![/bold green] {match.rounds_won}-{match.rounds_lost}", style="bold green")
        input("\n  Press Enter to continue...")
        return True
    else:
        cprint(f"\n  💀 [bold red]MATCH LOST[/bold red] {match.rounds_won}-{match.rounds_lost}", style="bold red")
        input("\n  Press Enter to continue...")
        return False


# ─── Campaign Display ────────────────────────────────────────────────

def _show_campaign_bracket(current_match: int) -> None:
    """Show a compact bracket showing campaign progress.

    current_match is the 0-indexed match about to be played (or just lost).
    """
    labels = ["GS", "R16", "QF", "SF", "FN"]
    status_chars = []
    for i in range(5):
        if i < current_match:
            status_chars.append("✅")  # Won
        elif i == current_match:
            status_chars.append("⚔️")  # Current
        else:
            status_chars.append("⬜")  # Upcoming

    bracket_line = "  " + " → ".join(
        f"[{labels[i]}] {status_chars[i]}" for i in range(5)
    )
    cprint("\n  [bold]Campaign Bracket:[/bold]", style="bold yellow")
    cprint(bracket_line, style="bold")
    # Legend
    cprint("  GS=Group Stage  R16=Round of 16  QF=Quarter Final  "
           "SF=Semi Final  FN=Final", style="dim")
    cprint(f"  {'─' * 55}", style="dim")


# ─── Entry Point ──────────────────────────────────────────────────────

def main():
    """Main game loop with global error catching."""
    try:
        _run_game()
    except KeyboardInterrupt:
        cprint("\n  Game interrupted. See you next time!", style="yellow")
    except Exception as exc:
        cprint(f"\n  [bold red]⚠️  UNEXPECTED ERROR[/bold red]", style="bold red")
        cprint(f"  {type(exc).__name__}: {exc}", style="red")
        cprint("\n  Sorry about that! The game hit a snag.", style="yellow")
        cprint("  Please report what you were doing so we can fix it.", style="dim")
        input("\n  Press Enter to exit...")


def _run_game():
    """Main game loop — campaign of 5 escalating matches."""
    data = load_all()
    players = data["players"]
    all_synergies = data["synergies"]

    clear_screen()
    cprint("\n  ╔═══════════════════════════════════════════════════╗", style="bold cyan")
    cprint( "  ║              ⚽  S Q U A D  ⚽                   ║", style="bold cyan")
    cprint( "  ║     Football Card Roguelike — Phase System       ║", style="bold cyan")
    cprint( "  ╚═══════════════════════════════════════════════════╝", style="bold cyan")
    cprint("\n  A campaign of 5 matches. Win a match = win 2 of 3 rounds.", style="dim")
    cprint("  Lose any match — tournament over. Win all 5 — champion!", style="dim")
    input("\n  Press Enter to start...")

    # Build your squad within budget
    squad = build_squad(players)

    # Formation
    formation = select_formation(squad)

    # Squad-persistent synergies (trait-based, automatically check all)
    all_persistent = [s for s in all_synergies if s.persistent]
    persistent_buffs = detect_squad_synergies(squad, all_persistent)
    fired_persistent = persistent_buffs.get("fired_synergies", [])
    if fired_persistent:
        cprint(f"\n  🏷️  [bold]Persistent Synergies Active:[/bold]", style="bold magenta")
        for name in fired_persistent:
            cprint(f"    ✦ {name}", style="magenta")
        if persistent_buffs.get("fatigue_penalty", 0.7) != 0.7:
            cprint(f"    Fatigue penalty: ×{persistent_buffs['fatigue_penalty']} (instead of ×0.7)", style="cyan")
        if persistent_buffs.get("journeyman_available"):
            cprint(f"    🛠️  Journeyman: once per match, restore one player's fatigue", style="cyan")
    else:
        cprint(f"\n  No persistent synergies activated by your squad.", style="dim")

    # Pool of all phase-specific synergies — 5 random ones picked each round
    phase_synergy_pool = [s for s in all_synergies if not s.persistent]

    # ── Campaign: 5 matches, increasing difficulty ──
    for match_idx, match_def in enumerate(CAMPAIGN_MATCHES):
        clear_screen()
        # Campaign bracket display
        _show_campaign_bracket(match_idx)

        # Create match for this campaign game
        match = create_match(squad, [],  # synergies empty — start_round fills them
                             opponent_name=match_def["opponent"],
                             round_targets=match_def["targets"],
                             formation=formation,
                             persistent_buffs=persistent_buffs,
                             synergy_pool=phase_synergy_pool)

        cprint(f"\n  ╔═══════════════════════════════════════════════════╗", style="bold cyan")
        cprint(f"  ║     [bold]{match_def['name']:^42s}[/bold]     ║", style="bold cyan")
        cprint(f"  ║     {match_def['tier']:^42s}     ║", style="bold cyan")
        cprint(f"  ╚═══════════════════════════════════════════════════╝", style="bold cyan")

        cprint(f"\n  🆚 [bold]{match_def['opponent']}[/bold]", style="bold red")
        cprint(f"  Targets: R1={match.round_targets[0]}  "
               f"R2={match.round_targets[1]}  "
               f"R3={match.round_targets[2]}", style="dim")
        if formation:
            cprint(f"  Formation: [bold]{formation.name}[/bold] (×{formation.global_mult} mult)", style="cyan")
        input("\n  Press Enter to kick off...")

        won = play_match(match)

        clear_screen()
        if not won:
            # Match lost — campaign over
            _show_campaign_bracket(match_idx)
            cprint(f"\n  ╔═══════════════════════════════════════════════════╗", style="bold red")
            cprint(f"  ║     [bold red]CAMPAIGN ENDED[/bold red]                    ║", style="bold red")
            cprint(f"  ╚═══════════════════════════════════════════════════╝", style="bold red")
            cprint(f"\n  💀 [bold red]Lost at {match_def['name']}[/bold red] "
                   f"({match.rounds_won}-{match.rounds_lost})", style="bold red")
            cprint(f"  {match_def['opponent']} was too strong.", style="dim")
            cprint(f"\n  [bold]Reach:[/bold] Match {match_idx + 1}/5", style="yellow")
            if match_idx == 4:
                cprint("  So close to the title...", style="dim")
            else:
                cprint("  Better luck next season.", style="dim")
            input("\n  Press Enter to exit...")
            return

        # Match won!
        cprint(f"\n  ╔═══════════════════════════════════════════════════╗", style="bold green")
        cprint(f"  ║     [bold green]{match_def['name']} — WON![/bold green]              ║", style="bold green")
        cprint(f"  ╚═══════════════════════════════════════════════════╝", style="bold green")
        cprint(f"\n  🏆 [bold green]{match_def['opponent']} defeated[/bold green] "
               f"({match.rounds_won}-{match.rounds_lost})", style="bold green")

        if match_idx < 4:
            cprint(f"\n  Campaign: {match_idx + 1}/5 matches won", style="bold yellow")
        input("\n  Press Enter to continue...")

    # ── All 5 matches won! ──
    clear_screen()
    cprint("\n  ╔═══════════════════════════════════════════════════╗", style="bold green")
    cprint( "  ║                                               ║", style="bold green")
    cprint( "  ║     🏆  [bold bright_green]TOURNAMENT CHAMPIONS![/bold bright_green]  🏆     ║", style="bold green")
    cprint( "  ║                                               ║", style="bold green")
    cprint( "  ║     [bold]Your squad conquered all 5 matches![/bold]  ║", style="bold green")
    cprint( "  ║                                               ║", style="bold green")
    cprint( "  ╚═══════════════════════════════════════════════════╝", style="bold green")
    cprint("\n  [bold]Campaign Results:[/bold]", style="bold yellow")
    for i, mdef in enumerate(CAMPAIGN_MATCHES):
        cprint(f"    Match {i+1}: [bold]{mdef['name']:18s}[/bold] → {mdef['opponent']:25s} — WIN", style="green")
    cprint("\n  [bold bright_green]You are the champion! ⚽🏆✨[/bold bright_green]")
    cprint("\n  Thanks for playing Squad!\n", style="dim")


if __name__ == "__main__":
    main()
