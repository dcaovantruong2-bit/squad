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
                       advance_phase, check_round, set_selected_phases,
                       CAMPAIGN_MATCHES)
from src.phases import (slot_positions, slot_label, is_player_eligible)
from src.scoring import (detect_squad_synergies, detect_synergies, calculate_chips,
                         compute_synergy_preview, calculate_round_score,
                         get_fired_synergy_names)


from src.ui.console import cprint, clear_screen
from src.ui.table import Table
from src.ui.synergy_box import SynergyBox
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
    """Show the current phase header with context bar."""
    clear_screen()
    
    # Context bar at top
    cprint("", style="")  # blank line
    cprint(f"  [bold]R{round_num}/3[/bold]  │  "
           f"Score: [bold cyan]{round_score}/{target}[/bold cyan]  │  "
           f"[bold]{round_won}-{round_lost}[/bold]  │  "
           f"Phase {phase_idx+1}/6", style="bold")
    cprint("  " + "─" * 55, style="dim")
    
    # Phase info
    weight_icons = {"DEF": "🛡️", "PAS": "🔄", "PAC": "⚡", "ATK": "🎯", "SPC": "✨"}
    icon = weight_icons.get(phase.weight, "⚽")
    slots_str = " → ".join(slot_label(s) for s in phase.slots)
    
    cprint(f"\n  {icon} [bold]{phase.name}[/bold]", style="bold yellow")
    cprint(f"  [dim]{phase.description}[/dim]", style="dim")
    cprint(f"  Slots: {slots_str}  │  Cards: {len(phase.slots)}", style="dim")
    
    # Show carryover bonus from previous phase
    if carryover:
        bonus = carryover.get("add_chips", 0)
        source = carryover.get("source_synergy", "Previous phase")
        cprint(f"\n  ⚡ [bold yellow]CARRYOVER:[/bold yellow] {source} — "
               f"first attacker gets +{bonus} chips!", style="bold yellow")


def show_pitch(field: list[tuple], phase_slots: list, fatigue: dict) -> None:
    """Show the pitch with slot status (filled/empty)."""
    cprint("\n  [bold]─── ON THE PITCH ───[/bold]", style="bold green")
    
    for i, slot_def in enumerate(phase_slots):
        slot_lbl = slot_label(slot_def)
        
        # Check if this slot is filled
        if i < len(field):
            player, pos = field[i]
            chips = calculate_chips(player, pos)
            fm = fatigue.get(player.id, 1.0)
            fat_str = f" {int(fm*100)}%" if fm < 1.0 else " FRESH"
            cprint(f"  │  Slot {i+1}: {slot_lbl:20s} │  [green]✅[/green] {player.name:18s}  "
                   f"{chips:3d} chips{fat_str}", style="green")
        else:
            cprint(f"  │  Slot {i+1}: {slot_lbl:20s} │  [dim][EMPTY][/dim]", style="dim")
    
    cprint("  " + "─" * 60, style="dim")


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
    """Show scoring result like Balatro — chips × mult for each player with clear math."""
    clear_screen()
    
    # ── Header — Phase name + context ──
    cprint("", style="")
    cprint("  ╔═══════════════════════════════════════════════════╗", style="bold yellow")
    cprint(f"  ║            [bold]{result['phase_name']:>12s}[/bold]            ║", style="bold yellow")
    cprint("  ╚═══════════════════════════════════════════════════╝", style="bold yellow")
    cprint("")
    
    all_fired = set()
    
    # ── Per-player scoring breakdown (Balatro-style) ──
    for entry in result["breakdown"]:
        p = entry["player"]
        pos = entry["position"]
        base = entry["base_chips"]
        add = entry["add_chips"]
        mult = entry["multiply"]
        fatigue_mult = entry.get("fatigue", 1.0)
        subtotal = entry["subtotal"]
        
        chips_total = base + add
        
        # Build display line: Player (Pos) base + add = subtotal  [×mult ×fat]
        line = f"  [bold]{p:20s}[/bold] ({pos:3s})  [green]{base:3d}[/green]"
        if add > 0:
            line += f" +[yellow]{add:3d}[/yellow]"
        elif add < 0:
            line += f" -[red]{-add:3d}[/red]"
        line += f" = [bold]{chips_total:3d}[/bold]"
        
        # Show multipliers if any
        mult_label = ""
        if mult != 1.0:
            mult_label += f" ×{mult:.2f}"
        if fatigue_mult != 1.0:
            mult_label += f" ×{fatigue_mult:.2f}f"
        if mult_label:
            line += f" [dim]{mult_label}[/dim]"
        
        line += f"  = [bold cyan]{subtotal:>4d}[/bold cyan]"
        
        cprint(line, style="bold" if mult != 1.0 or fatigue_mult != 1.0 else "dim")
        
        # Track fired synergies for display below
        for syn in entry.get("fired_synergies", []):
            all_fired.add(syn.split(" (")[0])
    
    # ── Running Total + Global Effects ──
    cprint("")
    cprint("  " + "─" * 55, style="dim")
    
    subtotal = result.get("subtotal_before_globals", 0)
    cprint(f"  [bold]Subtotal:[/bold]  {subtotal:>6d}", style="bold")
    
    if result.get("global_add", 0) != 0:
        cprint(f"  [magenta]+ Global bonus:[/magenta]      +{result['global_add']:>3d}", style="magenta")
    if result.get("global_mult", 1.0) != 1.0:
        cprint(f"  [magenta]× Global mult:[/magenta]        ×{result['global_mult']:.3f}", style="magenta")
    if result.get("formation_mult", 1.0) != 1.0:
        cprint(f"  [cyan]× {result.get('formation_name', 'Formation')}:[/cyan]       ×{result['formation_mult']:.2f}", style="cyan")
    
    # ── PHASE TOTAL — big number like Balatro ──
    cprint("")
    cprint("  " + "═" * 55, style="bold yellow")
    cprint(f"  [bold]PHASE TOTAL:[/bold]     [bold green]{result['total']:>7d}[/bold green]", style="bold yellow")
    cprint("  " + "═" * 55, style="bold yellow")
    
    # ── Synergies fired in this phase ──
    phase_syns = [s for s in all_fired if "(persistent)" not in s]
    if phase_syns:
        cprint("")
        cprint(f"  [yellow]⚡ Synergies: {', '.join(sorted(phase_syns)[:5])}[/yellow]", style="yellow")
        if len(phase_syns) > 5:
            cprint(f"  [dim]           +{len(phase_syns)-5} more[/dim]", style="dim")


def show_round_result(score: int, target: int, won: bool,
                      phase_results: list | None = None,
                      match_state=None) -> None:
    """Show round result with phase breakdown bar chart and fatigue summary."""
    if won:
        cprint(f"\n  🎉 [bold green]ROUND WON![/bold green]  {score} / {target}", style="bold green")
    else:
        cprint(f"\n  💔 [bold red]ROUND LOST[/bold red]  {score} / {target}", style="bold red")
    
    # Phase breakdown bars
    if phase_results:
        cprint(f"\n  [bold]Phase Breakdown:[/bold]", style="bold")
        max_phase = max((pr.get("total", 0) for pr in phase_results), default=1)
        if max_phase == 0:
            max_phase = 1
        bar_max = 20
        
        for i, pr in enumerate(phase_results):
            phase_total = pr.get("total", 0)
            bar_filled = int((phase_total / max_phase) * bar_max) if max_phase > 0 else 0
            bar = "█" * min(bar_filled, bar_max) + "░" * (bar_max - min(bar_filled, bar_max))
            
            # Count synergies for this phase
            syn_count = len([s for s in pr.get("fired_synergies", [])
                           if "(persistent)" not in s])
            syn_tag = f"  ⚡×{syn_count}" if syn_count > 0 else ""
            
            cprint(f"    {i+1}. {pr.get('phase_name', 'Unknown'):15s}  "
                   f"{phase_total:4d} pts  {bar}{syn_tag}",
                   style="bold green" if syn_count > 0 else "dim")
    
    cprint(f"    {'─' * 50}", style="dim")
    cprint(f"    {'Total':15s}  {score:4d} / {target}", style="bold")
    
    # Fatigue summary (if match state provided)
    if match_state and hasattr(match_state, 'fatigue') and match_state.fatigue:
        fresh = sum(1 for fm in match_state.fatigue.values() if fm >= 1.0)
        tired = sum(1 for fm in match_state.fatigue.values() if 0.7 <= fm < 1.0)
        exhausted = sum(1 for fm in match_state.fatigue.values() if fm < 0.7)
        
        if fresh + tired + exhausted > 0:
            cprint(f"\n  [bold]Squad Fatigue:[/bold]", style="bold")
            parts = []
            if fresh > 0:
                parts.append(f"[green]{fresh} fresh[/green]")
            if tired > 0:
                parts.append(f"[yellow]{tired} at 70%[/yellow]")
            if exhausted > 0:
                parts.append(f"[red]{exhausted} below 50%[/red]")
            cprint(f"    {', '.join(parts)}")
    
    # Match record
    if match_state:
        cprint(f"\n  Match: [bold]{match_state.rounds_won}-{match_state.rounds_lost}[/bold] "
               f"(need 2 to win)", style="bold")


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

    for slot_idx, slot_def in enumerate(phase.slots):
        # Show current state with pitch view
        show_phase_header(phase, match.current_phase_idx,
                          match.current_round + 1, match.current_target,
                          match.round_score, match.rounds_won, match.rounds_lost,
                          carryover=match.carryover)
        show_pitch(match.field, phase.slots, match.fatigue)

        # If this slot already filled (shouldn't happen but guard)
        if len(match.field) >= phase.max_cards:
            cprint("\n  [bold green]All slots for this phase filled![/bold green]", style="bold")
            input("  Press Enter to continue...")
            break

        placed_ids = {p.id for p, _ in match.field}
        journeyman_avail = bool(match.persistent_buffs and match.persistent_buffs.get("journeyman_available"))
        journeyman_ref = [match.journeyman_used]
        
        cprint(f"\n  [bold]Fill Slot {slot_idx+1}: {slot_label(slot_def)}[/bold]", style="bold")
        
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
        
        cprint(f"\n  [bold]→ Running total: {preview_total} pts[/bold]"
               f"  ({len(match.field)}/{phase.max_cards} cards placed)",
               style="bold cyan")
        
        if preview.get("fired_synergies"):
            phase_syns = [s for s in preview["fired_synergies"] if "(persistent)" not in s]
            if phase_syns:
                cprint(f"    ⚡ {', '.join(phase_syns)} active", style="yellow")

        # Wait for player to acknowledge before next slot
        if len(match.field) < phase.max_cards:
            cprint("  Press Enter for next slot...", style="dim")
            input()

    # Phase placement done — show final pitch
    show_phase_header(phase, match.current_phase_idx,
                      match.current_round + 1, match.current_target,
                      match.round_score, match.rounds_won, match.rounds_lost,
                      carryover=match.carryover)
    show_pitch(match.field, phase.slots, match.fatigue)
    cprint("\n  [bold green]✓ Phase field set![/bold green]", style="bold")
    input("  Press Enter to score this phase...")


# ─── Formation Selection ─────────────────────────────────────────────

# ASCII pitch diagrams for each formation
FORMATION_PITCHES = {
    "4-4-2": [
        "           ST      ST           ",
        "                                 ",
        "        CM      CM              ",
        "                                 ",
        "   FB                      FB   ",
        "        CB      CB              ",
        "             GK                 ",
    ],
    "4-3-3": [
        "              ST                ",
        "    LW                  RW      ",
        "        CM    CM    CM          ",
        "                                 ",
        "   FB                      FB   ",
        "        CB      CB              ",
        "             GK                 ",
    ],
    "5-3-2": [
        "           ST      ST           ",
        "                                 ",
        "        CM      CM              ",
        "            CDM                 ",
        "                                 ",
        "   CB  CB  CB  CB  CB           ",
        "             GK                 ",
    ],
    "3-4-3": [
        "           ST      ST           ",
        "    LW                  RW      ",
        "        CM      CM              ",
        "                                 ",
        "   FB                      FB   ",
        "        CB      CB              ",
        "             GK                 ",
    ],
    "4-2-3-1": [
        "              ST                ",
        "    LW      CAM      RW         ",
        "                                 ",
        "        CM      CM              ",
        "                                 ",
        "   FB                      FB   ",
        "        CB      CB              ",
        "             GK                 ",
    ],
    "4-5-1": [
        "              ST                ",
        "    LW                  RW      ",
        "    CM    CM    CM    CM       ",
        "            CDM                 ",
        "                                 ",
        "   FB                      FB   ",
        "        CB      CB              ",
        "             GK                 ",
    ],
}


def select_formation(squad) -> object:
    """Let the player pick a formation. Shows fit score based on squad."""
    formations = get_all_formations()

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

    # Score all formations
    scored = []
    for i, f in enumerate(formations):
        score, reasons = formation_fit(f, squad)
        scored.append((score, i, f, reasons))

    scored.sort(key=lambda x: -x[0])
    best_score = scored[0][0] if scored else 0

    # Show the recommended formation with pitch diagram
    clear_screen()
    cprint("  ╔═══════════════════════════════════════════════════╗", style="bold cyan")
    cprint(  "  ║         Choose Your Formation                    ║", style="bold cyan")
    cprint(  "  ╚═══════════════════════════════════════════════════╝", style="bold cyan")

    # Find the best formation and show its pitch
    best_f = scored[0][2] if scored else formations[0]
    best_reasons = scored[0][3] if scored else []
    
    # ⭐ RECOMMENDED
    if best_score > 0:
        cprint(f"\n  [bold yellow]⭐ RECOMMENDED: {best_f.name}[/bold yellow]"
               f"  (fit: [bold]{best_score}[/bold])", style="bold yellow")
        
        # ASCII pitch diagram
        pitch_lines = FORMATION_PITCHES.get(best_f.id, [])
        if pitch_lines:
            cprint("  [dim]┌──────────────────────────────────────┐[/dim]", style="dim")
            for line in pitch_lines:
                cprint(f"  [dim]│[/dim]{line}[dim]│[/dim]", style="dim")
            cprint("  [dim]└──────────────────────────────────────┘[/dim]", style="dim")
        
        if best_reasons:
            cprint(f"      [cyan]📊 {', '.join(best_reasons[:3])}[/cyan]", style="cyan")
    else:
        cprint("\n  [dim]No formation has a strong fit for your squad.[/dim]", style="dim")

    # List all formations
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
            cprint(f"      [cyan]📊 Fit: {', '.join(reasons[:3])}[/cyan]", style="cyan")
    
    cprint(f"\n      [dim]⭐ = recommended for your squad[/dim]", style="dim")
    cprint("      [dim]0 = default choice[/dim]", style="dim")

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


# ─── Phase Selection (Balatro-Like) ───────────────────────────────────────

def run_phase_selection(match: MatchState) -> None:
    """Show 6 dealt phase cards, let player pick 3 in order."""
    hand = match.phase_hand
    selected = []
    
    weight_icons = {"DEF": "🛡️", "PAS": "🔄", "PAC": "⚡", "ATK": "🎯", "SPC": "✨"}
    rarity_styles = {"common": "dim", "uncommon": "cyan", "rare": "yellow"}
    
    for pick_num in range(3):
        available = [p for p in hand if p not in selected]
        
        while True:
            clear_screen()
            cprint("  ╔═══════════════════════════════════════════════════╗", style="bold cyan")
            cprint(f"  ║        🃏  PICK PHASE {pick_num + 1} / 3                    ║", style="bold cyan")
            cprint("  ╚═══════════════════════════════════════════════════╝", style="bold cyan")
            cprint(f"  Round {match.current_round + 1}/3 — Target: {match.current_target}", style="bold")
            
            if selected:
                picked_names = " → ".join(p.name for p in selected)
                cprint(f"  [bold]Selected order:[/bold] {picked_names}  [dim](next pick goes after)[/dim]", style="bold yellow")
            else:
                cprint(f"  [dim]Pick your first phase. Order matters for carryover![/dim]", style="dim")
            
            # Show synergy context for this round
            if match.synergies:
                cprint("  [bold]📋 Round Synergies (pick phases that match your squad):[/bold]", style="bold yellow")
                for s in match.synergies:
                    color = rarity_styles.get(s.rarity, "dim")
                    cprint(f"    ✦ [bold]{s.name:22s}[/bold]  [{color}]{s.description}[/{color}]", style="yellow")
            
            cprint(f"\n  [bold]Available Phases:[/bold]", style="bold")
            
            for i, phase in enumerate(available):
                icon = weight_icons.get(phase.weight, "⚽")
                slots_str = " → ".join(slot_label(s) for s in phase.slots)
                
                cprint(f"")
                cprint(f"  [{i}] {icon} [bold]{phase.name}[/bold]", style="bold")
                cprint(f"      [dim]{phase.description}[/dim]", style="dim")
                cprint(f"      Slots: {slots_str}  |  Cards: {len(phase.slots)}", style="dim")
                
                # Show which squad players would excel in this phase
                eligible_by_slot = []
                for slot_def in phase.slots:
                    if isinstance(slot_def, str):
                        pos = slot_def
                        qualifying = [p for p in match.squad if p.position == pos]
                    elif isinstance(slot_def, list):
                        pos = slot_def[0]
                        qualifying = [p for p in match.squad if p.position in slot_def]
                    elif isinstance(slot_def, dict):
                        pos = slot_def["as"]
                        # For stat-based slots, any player meeting the threshold
                        qualifying = [p for p in match.squad
                                      if is_player_eligible(p, slot_def)]
                    else:
                        continue
                    
                    if qualifying:
                        best = max(qualifying, key=lambda p: calculate_chips(p, pos))
                        eligible_by_slot.append(f"{best.name} ({best.position}→{pos})")
                
                if eligible_by_slot:
                    cprint(f"      [green]Best fit:[/green] {', '.join(eligible_by_slot)}", style="green")
                
                # Preview which round synergies would fire for this phase
                if match.synergies:
                    # Simulate fielding the best available for each slot
                    sim_field = []
                    sim_used = set()
                    for slot_def in phase.slots:
                        if isinstance(slot_def, str):
                            pos = slot_def
                            pool = [p for p in match.squad if p.id not in sim_used and p.position == pos]
                        elif isinstance(slot_def, list):
                            pos = slot_def[0]
                            pool = [p for p in match.squad if p.id not in sim_used and p.position in slot_def]
                        elif isinstance(slot_def, dict):
                            pos = slot_def["as"]
                            pool = [p for p in match.squad if p.id not in sim_used
                                    and is_player_eligible(p, slot_def)]
                        else:
                            continue
                        if pool:
                            best = max(pool, key=lambda p: calculate_chips(p, pos))
                            sim_field.append((best, pos))
                            sim_used.add(best.id)
                    
                    if sim_field:
                        sim_result = detect_synergies(sim_field, match.synergies)
                        fired = get_fired_synergy_names(sim_result)
                        if fired:
                            cprint(f"      [yellow]⚡ Potential: {', '.join(sorted(fired)[:3])}[/yellow]",
                                   style="yellow")
                            if len(fired) > 3:
                                cprint(f"      [dim]        +{len(fired)-3} more[/dim]", style="dim")
            
            cprint(f"\n  [dim]Pick 0-{len(available) - 1}: [/dim]", style="dim", end="")
            
            try:
                raw = input().strip()
            except (EOFError, KeyboardInterrupt):
                return
            
            if raw == "":
                continue
            
            try:
                idx = int(raw)
                if 0 <= idx < len(available):
                    selected.append(available[idx])
                    break
                else:
                    cprint(f"  Number out of range. Pick 0-{len(available) - 1}.", style="red")
                    input("  Press Enter...")
            except ValueError:
                cprint(f"  Enter a number 0-{len(available) - 1}.", style="red")
                input("  Press Enter...")
    
    # Show final selected order
    set_selected_phases(match, selected)
    clear_screen()
    order_str = " → ".join(f"[bold]{p.name}[/bold]" for p in selected)
    cprint(f"\n  ✅ [bold green]Phase order set![/bold green]", style="bold green")
    cprint(f"  {order_str}", style="bold yellow")
    cprint(f"  [dim]Order matters for carryover (e.g. Double Pivot → next attacker gets bonus)[/dim]", style="dim")
    input("\n  Press Enter to begin...")


def play_match(match: MatchState) -> bool:
    """Play a full match (3 rounds, each with 6 phases). Returns True if won."""
    round_num = 0

    while not match.is_match_over and round_num < 3:
        match.current_round = round_num
        start_round(match)

        # Show this round's 5 random phase synergies as a tactical briefing
        if match.synergies:
            clear_screen()
            cprint("\n  [bold]📋 ROUND SYNERGIES[/bold]", style="bold yellow")
            cprint(f"  [dim]Round {round_num+1} / 3 — Target: {match.current_target} — "
                   f"Score: {match.round_score}[/dim]", style="dim")
            cprint("  " + "─" * 55, style="dim")
            
            for s in match.synergies:
                rarity_color = {
                    "Common": "dim",
                    "Uncommon": "cyan",
                    "Rare": "yellow",
                    "Epic": "magenta",
                    "Legendary": "bold green",
                }.get(s.rarity, "dim")
                
                cprint(f"    ✦ [bold]{s.name:22s}[/bold]  [{rarity_color}]{s.rarity:10s}[/{rarity_color}]"
                       f"  [dim]{s.description}[/dim]", style="yellow")
            
            cprint(f"  [dim]These synergies apply to phases where conditions are met.[/dim]", style="dim")
            cprint(f"  [dim]Build your phase selections around them![/dim]", style="dim")
            input("\\n  Press Enter to begin Round...")

        # Phase selection: deal 6, pick 3 in order
        run_phase_selection(match)

        # Run 3 selected phases
        for phase_idx in range(3):
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

            if phase_idx < 2:
                advance_phase(match)

        advance_phase(match)  # Marks round complete

        # Check round result
        won = check_round(match)
        clear_screen()
        show_round_result(match.round_score, match.current_target, won,
                          phase_results=match.phase_results,
                          match_state=match)

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

# Scouting reports — color commentary for each opponent
OPPONENT_SCOUTING = {
    "Wolves FC": "\"Relegation battlers. Forwards can't finish — exploit set pieces.\"",
    "Inter Your-Nan": "\"Defensively organised. Test them early, they tire in R3.\"",
    "Borussia Mönchen-flapjack": "\"Midfield maestros. Match their PAS output or get overrun.\"",
    "Man City Oilers": "\"Possession monsters. Need high PAC phases to break their press.\"",
    "Galácticos FC": "\"No weaknesses. Perfect execution required across all 6 phases.\"",
}

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
        # Scouting report
        scouting = OPPONENT_SCOUTING.get(match_def["opponent"], "")
        if scouting:
            cprint(f"     [cyan]🔍 {scouting}[/cyan]", style="cyan")
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
