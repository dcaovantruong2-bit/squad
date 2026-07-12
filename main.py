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
from src.phases import Phase, slot_positions, slot_label, is_player_eligible, get_position_penalty, get_position_penalty_label
from src.scoring import (detect_squad_synergies, detect_synergies, calculate_chips,
                          compute_synergy_preview, calculate_round_score,
                          get_fired_synergy_names, ATTACKER_POSITIONS)


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
    """Show scoring result like Balatro — chips × mult × x_mult with clear math."""
    clear_screen()
    
    # ── Header ──
    cprint("", style="")
    cprint("  ╔═══════════════════════════════════════════════════╗", style="bold yellow")
    cprint(f"  ║            [bold]{result['phase_name']:>12s}[/bold]            ║", style="bold yellow")
    cprint("  ╚═══════════════════════════════════════════════════╝", style="bold yellow")
    cprint("")
    
    # ── Player Chip Contributions ──
    cprint("  [bold underline]FIELD PLAYERS (chip contributions):[/bold underline]", style="bold")
    for entry in result["breakdown"]:
        p = entry["player"]
        pos = entry["position"]
        base = entry["base_chips"]
        bonus = entry["pos_bonus"]
        pers_add = entry["persistent_add"]
        pers_mult = entry["persistent_mult"]
        fatigue_mult = entry.get("fatigue", 1.0)
        eff = entry["effective_chips"]

        # Show: Player (Pos)  base +bonus +pers_add = X  ×pers_mult ×fatigue = effective
        line = f"  [bold]{p:20s}[/bold] ({pos:3s})  [green]{base:2d}[/green]"
        if bonus:
            line += f" +[cyan]{bonus:2d}b[/cyan]"
        if pers_add:
            line += f" +[magenta]{pers_add:2d}p[/magenta]"
        # Show multipliers
        parts = []
        if pers_mult != 1.0:
            parts.append(f"×{pers_mult:.2f}pm")
        if fatigue_mult != 1.0:
            parts.append(f"×{fatigue_mult:.2f}f")
        suffix = "".join(parts) if parts else ""
        if suffix:
            line += f"  [dim]{suffix}[/dim]"
        line += f"  = [bold cyan]{eff:>3d}[/bold cyan]"
        cprint(line, style="bold" if fatigue_mult < 1.0 else "dim")
    
    # ── Phase Synergy Effects ──
    cprint("")
    cprint("  [bold underline]SYNERGY EFFECTS:[/bold underline]", style="bold")
    fired_details = result.get("fired_details", [])
    synergy_chips = 0
    add_mult_parts = []
    x_mult_parts = []
    
    for detail in fired_details:
        name = detail["name"]
        etype = detail["effect_type"]
        value = detail["value"]
        contribs = ", ".join(detail.get("contributors", []))
        
        if etype == "chips":
            synergy_chips += value
            cprint(f"  [green]+{value} chips[/green]  {name}  [dim]({contribs})[/dim]", style="green")
        elif etype == "add_mult":
            add_mult_parts.append(value)
            cprint(f"  [yellow]+{value} mult[/yellow]  {name}  [dim]({contribs})[/dim]", style="yellow")
        elif etype == "x_mult":
            x_mult_parts.append(value)
            cprint(f"  [red]×{value}[/red]  {name}  [dim]({contribs})[/dim]", style="red")
        elif etype == "carryover":
            cprint(f"  [cyan]⇢  carryover: +{value} chips next phase[/cyan]  {name}  [dim]({contribs})[/dim]", style="cyan")
    
    # Carryover from previous phase
    carryover_chips = result.get("carryover_chips", 0)
    if carryover_chips > 0:
        cprint(f"  [cyan]+{carryover_chips} chips (carryover from previous phase)[/cyan]", style="cyan")
    
    # Persistent chips
    persistent_chips = result.get("persistent_chips", 0)
    if persistent_chips:
        cprint(f"  [magenta]+{persistent_chips} persistent chips[/magenta]", style="magenta")
    
    # ── Balatro-style Formula Display ──
    cprint("")
    cprint("  " + "─" * 55, style="dim")
    
    player_chip_sum = result.get("player_chip_sum", 0)
    total_chips = result.get("total_chips", 0)
    add_mult = result.get("add_mult", 1)
    x_mult = result.get("x_mult", 1.0)
    formation_mult = result.get("formation_mult", 1.0)
    subtotal = result.get("subtotal_before_formation", 0)
    
    # Chips line
    chips_display = f"{player_chip_sum}"
    if synergy_chips:
        chips_display += f" +{synergy_chips}syn"
    if carryover_chips:
        chips_display += f" +{carryover_chips}carry"
    if persistent_chips:
        chips_display += f" +{persistent_chips}pers"
    cprint(f"  🃏 [bold]CHIPS:[/bold]  {player_chip_sum}", style="bold")
    if synergy_chips or carryover_chips or persistent_chips:
        cprint(f"          + bonuses → [bold cyan]{total_chips}[/bold cyan]", style="cyan")
    
    # Add Mult line
    am_str = "1" if not add_mult_parts else f"1 + {' + '.join(str(v) for v in add_mult_parts)}"
    cprint(f"  ➕ [bold]ADD MULT:[/bold]  {am_str} = [bold yellow]{add_mult}[/bold yellow]", style="bold")
    
    # X Mult line
    xm_str = " × ".join(str(v) for v in x_mult_parts) if x_mult_parts else "1"
    cprint(f"  ✖ [bold]× MULT:[/bold]    {' × '.join(str(v) for v in x_mult_parts) if x_mult_parts else '1'} = [bold red]{x_mult:.3f}[/bold red]", style="bold")
    
    # Formula
    cprint(f"")
    cprint(f"  [bold]FORMULA:[/bold]  {total_chips} × {add_mult} × {x_mult:.3f} = [bold cyan]{subtotal}[/bold cyan]", style="bold")
    
    if formation_mult != 1.0:
        cprint(f"  [cyan]× {result.get('formation_name', 'Formation')}:[/cyan]         ×{formation_mult:.2f}", style="cyan")
    if result.get("momentum", 1.0) != 1.0:
        cprint(f"  [yellow]× Momentum:[/yellow]          ×{result['momentum']:.1f}", style="yellow")
    if result.get("phase_mult", 1.0) != 1.0:
        pm = result["phase_mult"]
        cprint(f"  [magenta]× Phase adj:[/magenta]        ×{pm:.2f}", style="magenta")
    
    # ── PHASE TOTAL — big number ──
    cprint("")
    cprint("  " + "═" * 55, style="bold yellow")
    cprint(f"  [bold]PHASE TOTAL:[/bold]     [bold green]{result['total']:>7d}[/bold green]", style="bold yellow")
    cprint("  " + "═" * 55, style="bold yellow")
    
    # ── Synergies fired ──
    phase_syns = [d["name"] for d in fired_details if "(persistent)" not in d["name"] and "(carryover)" not in d["name"]]
    persistent_names = [s for s in result.get("fired_synergies", []) if "persistent" in str(s).lower() or s.endswith(")")]
    all_fired_names = set(phase_syns) | set(persistent_names)
    if all_fired_names:
        cprint("")
        cprint(f"  [yellow]⚡ {', '.join(sorted(all_fired_names)[:5])}[/yellow]", style="yellow")
        if len(all_fired_names) > 5:
            cprint(f"  [dim]           +{len(all_fired_names)-5} more[/dim]", style="dim")



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
    
    # Morale
    if match_state:
        cprint(f"\n  💰 [bold]Morale:[/bold] [yellow]{match_state.morale}[/yellow]", style="bold")


def show_shop(match_state) -> None:
    """Display the between-rounds shop and handle purchases with selection UIs."""
    from src.shop import SHOP_ITEMS, get_shop_inventory, apply_shop_item, ActiveBuffs
    from src.formations import get_all_formations
    from src.cards import PlayerCard
    import random

    # Generate shop inventory (4 items)
    inventory = get_shop_inventory()

    while True:
        clear_screen()
        cprint("\n  ╔═══════════════════════════════════════════════════╗", style="bold cyan")
        cprint(f"  ║            🏪  BETWEEN ROUNDS SHOP              ║", style="bold cyan")
        cprint("  ╚═══════════════════════════════════════════════════╝", style="bold cyan")
        cprint(f"\n  💰 [bold]Your Morale:[/bold] [yellow]{match_state.morale}[/yellow]\n", style="bold")

        cprint("  [bold]Available Items:[/bold]", style="bold")
        for idx, item in enumerate(inventory):
            can_afford = match_state.morale >= item.cost
            cost_color = "green" if can_afford else "red"
            cprint(f"\n  [{idx+1}] [bold]{item.name}[/bold]  "
                   f"([{cost_color}]{item.cost} Morale[/{cost_color}])  "
                   f"[dim]{item.rarity}[/dim]", style="bold")
            cprint(f"      {item.description}", style="dim")

        cprint(f"\n  [0] [dim]Skip shop — continue[/dim]", style="dim")
        cprint(f"  [R] [dim]Reroll shop (free)[/dim]", style="dim")

        choice = input("\n  Your choice: ").strip().upper()

        if choice == "0" or choice == "":
            break
        elif choice == "R":
            inventory = get_shop_inventory()
            continue

        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(inventory):
                continue
            item = inventory[idx]
        except (ValueError, IndexError):
            continue

        if match_state.morale < item.cost:
            cprint("  [red]Not enough Morale![/red]", style="red")
            input("  Press Enter...")
            continue

        # ── Handle each item type with its selection UI ──
        purchased = False

        if item.id == "inspired_sub":
            # Pick a tired player, reset their fatigue
            tired_players = [(p, fm) for p in match_state.squad
                             for pid, fm in match_state.fatigue.items()
                             if p.id == pid and fm < 1.0]
            if not tired_players:
                cprint("  [yellow]No tired players! Everyone is fresh.[/yellow]", style="yellow")
                input("  Press Enter...")
                continue
            cprint("\n  [bold]Pick a player to restore:[/bold]", style="bold")
            for i, (p, fm) in enumerate(tired_players):
                cprint(f"  [{i+1}] {p.name:20s} ({p.position})  [{int(fm*100)}%]", style="yellow")
            pick = input("  Pick: ").strip()
            try:
                pi = int(pick) - 1
                if 0 <= pi < len(tired_players):
                    p = tired_players[pi][0]
                    match_state.fatigue[p.id] = 1.0
                    cprint(f"  [green]✅ {p.name}'s fatigue restored to 100%![/green]", style="green")
                    match_state.morale -= item.cost
                    purchased = True
                else:
                    continue
            except ValueError:
                continue

        elif item.id == "tactical_upgrade":
            # Pick a player, then pick a stat
            cprint("\n  [bold]Pick a player to upgrade:[/bold]", style="bold")
            squad_list = list(match_state.squad)
            for i, p in enumerate(squad_list):
                cprint(f"  [{i+1}] {p.name:20s} ({p.position})  "
                       f"ATK:{p.atk} PAC:{p.pac} PAS:{p.pas} DEF:{p.def_} SPC:{p.spc}", style="dim")
            p_pick = input("  Pick: ").strip()
            try:
                pi = int(p_pick) - 1
                if 0 <= pi < len(squad_list):
                    player = squad_list[pi]
                    STATS = {"ATK": "atk", "PAC": "pac", "PAS": "pas", "DEF": "def_", "SPC": "spc"}
                    cprint(f"\n  [bold]Pick a stat for {player.name}:[/bold]", style="bold")
                    for si, (label, attr) in enumerate(STATS.items()):
                        cprint(f"  [{si+1}] {label} ({getattr(player, attr)} → {getattr(player, attr)+1})", style="dim")
                    s_pick = input("  Stat: ").strip()
                    try:
                        si = int(s_pick) - 1
                        if 0 <= si < len(STATS):
                            attr = list(STATS.values())[si]
                            setattr(player, attr, getattr(player, attr) + 1)
                            cprint(f"  [green]✅ {player.name}'s {list(STATS.keys())[si]} boosted to {getattr(player, attr)}![/green]", style="green")
                            match_state.morale -= item.cost
                            purchased = True
                        else:
                            continue
                    except ValueError:
                        continue
                else:
                    continue
            except ValueError:
                continue

        elif item.id == "veterans_wisdom":
            # Pick a player, grant random trait
            POSITIVE_TRAITS = ["pacey", "clinical", "technical", "physical", "leader",
                               "aerial", "playmaker", "poacher", "destroyer", "journeyman"]
            cprint("\n  [bold]Pick a player to mentor:[/bold]", style="bold")
            squad_list = list(match_state.squad)
            for i, p in enumerate(squad_list):
                traits_str = ", ".join(p.traits) if p.traits else "none"
                cprint(f"  [{i+1}] {p.name:20s} ({p.position})  traits: {traits_str}", style="dim")
            pick = input("  Pick: ").strip()
            try:
                pi = int(pick) - 1
                if 0 <= pi < len(squad_list):
                    player = squad_list[pi]
                    available = [t for t in POSITIVE_TRAITS if t not in player.traits]
                    if not available:
                        cprint(f"  [yellow]{player.name} already has all traits![/yellow]", style="yellow")
                        input("  Press Enter...")
                        continue
                    new_trait = random.choice(available)
                    player.traits.append(new_trait)
                    cprint(f"  [green]✅ {player.name} gained trait: {new_trait}![/green]", style="green")
                    match_state.morale -= item.cost
                    purchased = True
                else:
                    continue
            except ValueError:
                continue

        elif item.id == "formation_tweak":
            # Pick a different formation
            from src.formations import get_all_formations
            formations = get_all_formations()
            current_id = match_state.formation.id if match_state.formation else ""
            others = [f for f in formations if f.id != current_id]
            if not others:
                cprint("  [yellow]No other formations available![/yellow]", style="yellow")
                input("  Press Enter...")
                continue
            cprint("\n  [bold]Pick a new formation:[/bold]", style="bold")
            for i, f in enumerate(others):
                cprint(f"  [{i+1}] [bold]{f.name}[/bold]  (×{f.global_mult})  {f.description}", style="dim")
            pick = input("  Pick: ").strip()
            try:
                fi = int(pick) - 1
                if 0 <= fi < len(others):
                    match_state.formation = others[fi]
                    cprint(f"  [green]✅ Switched to {others[fi].name}![/green]", style="green")
                    match_state.morale -= item.cost
                    purchased = True
                else:
                    continue
            except ValueError:
                continue

        elif item.id in ("set_piece_drill", "momentum_injector", "scout_report",
                         "double_session", "tactical_shift", "super_sub"):
            # Non-interactive items — just apply
            result = apply_shop_item(item, match_state, match_state.squad)
            match_state.morale -= item.cost
            cprint(f"  [green]✅ {result}[/green]", style="green")
            purchased = True

        else:
            cprint(f"  [yellow]Unknown item: {item.id}[/yellow]", style="yellow")
            input("  Press Enter...")
            continue

        if purchased:
            # Remove purchased item from inventory
            inventory.remove(item)
            input("  Press Enter...")
            # One purchase per visit
            break


# ─── Phase Placement UI ───────────────────────────────────────────────

def select_slot_player(squad, fatigue, phase_slot, used_ids, current_field, synergies,
                        carryover: dict | None = None,
                        journeyman_available: bool = False,
                        journeyman_used_ref: list = None) -> object | None:
    """Let user pick a player from squad to fill one phase slot.

    Shows eligible players with OOP penalty, chip preview, and synergy tags.
    Accepts 'auto' to auto-fill with best player.
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
                slot_pos = phase_slot["as"]
            else:
                slot_pos = p.position if p.position in slot_positions_list else slot_positions_list[0]

            chips = calculate_chips(p, slot_pos)
            oop = get_position_penalty(p.position, slot_pos)
            oop_label = get_position_penalty_label(p.position, slot_pos)
            effective = int(chips * fm * oop)

            # OOP color/style
            if oop_label == "natural":
                oop_style = "green"
                oop_display = ""
            elif oop_label == "similar":
                oop_style = "cyan"
                oop_display = " [similar ×0.9]"
            elif oop_label == "OOP":
                oop_style = "yellow"
                oop_display = f" [OOP ×{oop:.1f}]"
            else:
                oop_style = "red"
                oop_display = " [BLOCKED]"

            # Check which synergies this player would unlock
            new_syns = compute_synergy_preview(p, slot_pos, current_field, synergies)
            syn_tag = ""
            if new_syns:
                syn_str = ", ".join(sorted(new_syns)[:2])
                syn_tag = f" ⚡{syn_str}"
                if len(new_syns) > 2:
                    syn_tag += f"+{len(new_syns)-2}"

            # Carryover tag
            carry_tag = ""
            if carryover and slot_pos in ATTACKER_POSITIONS:
                bonus = carryover.get("chips", carryover.get("add_chips", 0))
                if bonus:
                    carry_tag = f" 📦+{bonus}"

            cprint(f"    [{i}] {p.name:20s} [{p.position}]→{slot_pos:3s}  "
                   f"{status:5s}  → {effective:3d} chips{oop_display}"
                   f"{syn_tag}{carry_tag}",
                   style=color_for_fatigue(fm) if oop >= 0.7 else "red")

        # Show journeyman availability hint
        if journeyman_available and journeyman_used_ref is not None and not journeyman_used_ref[0]:
            cprint("  (type 'reset <#>' to fully restore a tired player -- once per match)", style="dim")

        cprint("  [dim](type 'auto' to auto-fill, 'skip' to pass)[/dim]", style="dim")

        try:
            raw = input("  Pick #: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if raw == 'skip':
            return None
        
        if raw == 'auto':
            # Auto-fill: pick highest effective-chips player
            best = max(eligible, key=lambda p: (
                calculate_chips(p, 
                    p.position if p.position in slot_positions(phase_slot) or not isinstance(phase_slot, str) 
                    else slot_positions(phase_slot)[0]) 
                * fatigue.get(p.id, 1.0) 
                * get_position_penalty(p.position, 
                    p.position if p.position in slot_positions(phase_slot) or not isinstance(phase_slot, str) 
                    else slot_positions(phase_slot)[0])
            ))
            return best

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
            cprint(f"  Type a number (0-{len(eligible)-1}), 'auto', or 'skip'.", style="red")
            continue

        if 0 <= idx < len(eligible):
            return eligible[idx]
        else:
            cprint(f"  Number out of range. Pick 0-{len(eligible)-1}.", style="red")


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


# ─── Available Synergy Detection ────────────────────────────────────────

def get_available_synergies(squad, all_synergies, persistent_buffs=None):
    """Return only synergies that can potentially fire given the squad.
    For each, also list the key players involved.
    Returns list of (synergy_name, description, [player_names_with_roles])"""
    from collections import defaultdict
    
    available = []
    
    for s in all_synergies:
        if s.persistent:
            continue  # Persistent are always active, shown elsewhere
        
        tr = s.trigger
        can_fire = False
        involved = []
        
        if s.trigger_type == 'clean_sheet':
            gks = [p for p in squad if p.position == 'GK']
            cbs = [p for p in squad if p.position == 'CB']
            for gk in gks:
                for cb in cbs:
                    if gk.def_ + cb.def_ >= tr['threshold']:
                        can_fire = True
                        involved = [f'{gk.name} (DEF{gk.def_})', f'{cb.name} (DEF{cb.def_})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'organised_defence':
            cbs = [p for p in squad if p.position == 'CB']
            for i, cb1 in enumerate(cbs):
                for cb2 in cbs[i+1:]:
                    if cb1.def_ + cb2.def_ >= tr['threshold']:
                        can_fire = True
                        involved = [f'{cb1.name} (DEF{cb1.def_})', f'{cb2.name} (DEF{cb2.def_})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'wingback_overlap':
            fbs = [p for p in squad if p.position == 'FB']
            cms = [p for p in squad if p.position == 'CM']
            for fb in fbs:
                for cm in cms:
                    if fb.pac + cm.pas >= tr['threshold']:
                        can_fire = True
                        involved = [f'{fb.name} (PAC{fb.pac})', f'{cm.name} (PAS{cm.pas})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'overload':
            pos_counts = defaultdict(int)
            pos_players = defaultdict(list)
            for p in squad:
                pos_counts[p.position] += 1
                pos_players[p.position].append(p.name)
            for pos, count in pos_counts.items():
                if count >= tr.get('min_duplicates', 2):
                    can_fire = True
                    involved = pos_players[pos][:3]
                    break
        
        elif s.trigger_type == 'stretch_backline':
            fbs = [p for p in squad if p.position == 'FB']
            lws = [p for p in squad if p.position == 'LW']
            for fb in fbs:
                for lw in lws:
                    if fb.pac + lw.pac >= tr['threshold']:
                        can_fire = True
                        involved = [f'{fb.name} (PAC{fb.pac})', f'{lw.name} (PAC{lw.pac})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'route_one':
            cbs = [p for p in squad if p.position == 'CB']
            sts = [p for p in squad if p.position == 'ST']
            for cb in cbs:
                for st in sts:
                    if cb.pas + st.pac >= tr['threshold']:
                        can_fire = True
                        involved = [f'{cb.name} (PAS{cb.pas})', f'{st.name} (PAC{st.pac})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'battering_ram':
            cbs = [p for p in squad if p.position == 'CB']
            sts = [p for p in squad if p.position == 'ST']
            for cb in cbs:
                for st in sts:
                    if cb.def_ + st.atk >= tr['threshold']:
                        can_fire = True
                        involved = [f'{cb.name} (DEF{cb.def_})', f'{st.name} (ATK{st.atk})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'defensive_duo':
            high = sorted(squad, key=lambda p: p.def_, reverse=True)
            if len(high) >= 2 and high[0].def_ + high[1].def_ >= tr['threshold']:
                can_fire = True
                involved = [f'{high[0].name} (DEF{high[0].def_})', f'{high[1].name} (DEF{high[1].def_})']
        
        elif s.trigger_type == 'back_three':
            top3 = sorted(squad, key=lambda p: p.def_, reverse=True)[:3]
            if len(top3) >= 3 and all(p.def_ >= tr['threshold'] for p in top3):
                can_fire = True
                involved = [f'{p.name} (DEF{p.def_})' for p in top3]
        
        elif s.trigger_type == 'midfield_engine':
            cms = [p for p in squad if p.position == 'CM']
            for cm1 in cms:
                for cm2 in cms:
                    if cm1.id != cm2.id and cm1.pas + cm2.def_ >= tr['threshold']:
                        can_fire = True
                        involved = [f'{cm1.name} (PAS{cm1.pas})', f'{cm2.name} (DEF{cm2.def_})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'double_pivot':
            cms = [p for p in squad if p.position == 'CM']
            for i, cm1 in enumerate(cms):
                for cm2 in cms[i+1:]:
                    if cm1.pas + cm2.pas >= tr['threshold']:
                        can_fire = True
                        involved = [f'{cm1.name} (PAS{cm1.pas})', f'{cm2.name} (PAS{cm2.pas})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'trio':
            cms = [p for p in squad if p.position == 'CM']
            good = [p for p in cms if p.pas >= tr.get('threshold', 7)]
            if len(good) >= 3:
                can_fire = True
                involved = [f'{p.name} (PAS{p.pas})' for p in good[:3]]
        
        elif s.trigger_type == 'covering_defender':
            cbs = [p for p in squad if p.position == 'CB']
            fast = [p for p in cbs if p.pac >= tr['threshold_a']]
            strong = [p for p in cbs if p.def_ >= tr['threshold_b']]
            for f in fast:
                for st in strong:
                    if f.id != st.id:
                        can_fire = True
                        involved = [f'{f.name} (PAC{f.pac})', f'{st.name} (DEF{st.def_})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'target_man_release':
            sts = [p for p in squad if p.position == 'ST']
            wingers = [p for p in squad if p.position in ('LW', 'RW')]
            for st in sts:
                for w in wingers:
                    if st.atk + w.pac >= tr['threshold']:
                        can_fire = True
                        involved = [f'{st.name} (ATK{st.atk})', f'{w.name} (PAC{w.pac})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'near_post_flick':
            cams = [p for p in squad if p.position == 'CAM']
            sts = [p for p in squad if p.position == 'ST']
            for cam in cams:
                for st in sts:
                    if cam.spc + st.atk >= tr['threshold']:
                        can_fire = True
                        involved = [f'{cam.name} (SPC{cam.spc})', f'{st.name} (ATK{st.atk})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'one_two':
            cms = [p for p in squad if p.position == 'CM']
            sts = [p for p in squad if p.position == 'ST']
            for cm in cms:
                for st in sts:
                    if cm.pas + st.pac >= tr['threshold']:
                        can_fire = True
                        involved = [f'{cm.name} (PAS{cm.pas})', f'{st.name} (PAC{st.pac})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'overlap':
            fbs = [p for p in squad if p.position == 'FB']
            lws = [p for p in squad if p.position == 'LW']
            for fb in fbs:
                for lw in lws:
                    if fb.pac + lw.pas >= tr['threshold']:
                        can_fire = True
                        involved = [f'{fb.name} (PAC{fb.pac})', f'{lw.name} (PAS{lw.pas})']
                        break
                if can_fire: break
        
        elif s.trigger_type == 'set_piece_threat':
            def_high = [p for p in squad if p.def_ >= tr['threshold_a']]
            spc_high = [p for p in squad if p.spc >= tr['threshold_b']]
            for dp in def_high:
                for sp in spc_high:
                    if dp.id != sp.id:
                        can_fire = True
                        involved = [f'{dp.name} (DEF{dp.def_})', f'{sp.name} (SPC{sp.spc})']
                        break
                if can_fire: break
        
        if can_fire:
            available.append((s.name, s.description, involved))
    
    return available


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
            
            # Show available synergies (squad-relevant only)
            if match.synergies:
                syns = get_available_synergies(match.squad, match.synergies)
                if syns:
                    cprint("  [bold]📋 Squad synergies available:[/bold]", style="bold yellow")
                    for name, desc, players_involved in syns:
                        plyr = " — " + ", ".join(players_involved[:2])
                        cprint(f"    ✦ [bold]{name:22s}[/bold] [dim]{desc[:50]}[/dim]{plyr}", style="yellow")
            
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
                
                # Phase adjustment tags
                phase_id = phase.id
                fatigue_val = match.phase_fatigue.get(phase_id, 1.0)
                opp_val = match.opponent_adjustments.get(phase_id, 1.0)
                tags = []
                if fatigue_val < 1.0:
                    tags.append(f"[yellow]fatigue ×{fatigue_val:.2f}[/yellow]")
                if opp_val != 1.0:
                    style = "green" if opp_val > 1.0 else "red"
                    label = "weakness" if opp_val > 1.0 else "strong"
                    tags.append(f"[{style}]opp. {label} ×{opp_val:.2f}[/{style}]")
                if tags:
                    cprint(f"      {' '.join(tags)}", style="dim")
                
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
    input("  Press Enter to begin Round...")


def play_match(match: MatchState) -> bool:
    """Play a full match (3 rounds, each with 6 phases). Returns True if won."""
    round_num = 0

    while not match.is_match_over and round_num < 3:
        match.current_round = round_num
        start_round(match)

        # Show available synergies based on squad
        if match.synergies:
            clear_screen()
            cprint(f"  [bold]📋 ROUND {round_num+1} / 3[/bold]", style="bold yellow")
            cprint(f"  Target: {match.current_target}  —  Score: {match.round_score}", style="bold")
            cprint("  " + "─" * 55, style="dim")
            av = get_available_synergies(match.squad, match.synergies)
            if av:
                cprint(f"  [bold]⚡ {len(av)} synergies match your squad:[/bold]", style="bold yellow")
                for name, desc, players_involved in av[:8]:
                    plyr = " — " + ", ".join(players_involved[:2])
                    cprint(f"    ✦ [bold]{name:22s}[/bold] [dim]{desc[:45]}[/dim]{plyr}", style="yellow")
                if len(av) > 8:
                    cprint(f"    [dim]...and {len(av)-8} more (see phase selection)[/dim]", style="dim")
            else:
                cprint(f"  [dim]No phase synergies match your current squad.[/dim]", style="dim")
            cprint(f"  [dim]Build your phase selections around these![/dim]", style="dim")
            input("  Press Enter to begin Round...")

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

        # Calculate Morale earnings
        from src.shop import calculate_morale_earnings
        morale_earned = calculate_morale_earnings(
            phases_won=sum(1 for pr in match.phase_results if pr.get("total", 0) >= match.current_target * 0.7),
            phases_total=len(match.phase_results),
            round_won=won,
            round_target=match.current_target,
            round_score=match.round_score,
        )
        match.morale += morale_earned["total"]
        if morale_earned["total"] > 0:
            cprint(f"\n  💰 [yellow]+{morale_earned['total']} Morale earned![/yellow] "
                   f"(Total: {match.morale})", style="yellow")

        if not match.is_match_over:
            cprint(f"\n  Match: {match.rounds_won}-{match.rounds_lost}", style="bold")
            input("\n  Press Enter for next round...")
            # Shop between rounds
            show_shop(match)

        round_num += 1

    # Match result
    clear_screen()
    if match.is_match_won:
        cprint(f"\n  🏆 [bold green]MATCH WON![/bold green] {match.rounds_won}-{match.rounds_lost}", style="bold green")
        input()
        return True
    else:
        cprint(f"\n  💀 [bold red]MATCH LOST[/bold red] {match.rounds_won}-{match.rounds_lost}", style="bold red")
        input()
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
        input("  Press Enter to begin Round...")


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
        input("  Press Enter to begin Round...")

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
            input("  Press Enter to begin Round...")
            return

        # Match won!
        cprint(f"\n  ╔═══════════════════════════════════════════════════╗", style="bold green")
        cprint(f"  ║     [bold green]{match_def['name']} — WON![/bold green]              ║", style="bold green")
        cprint(f"  ╚═══════════════════════════════════════════════════╝", style="bold green")
        cprint(f"\n  🏆 [bold green]{match_def['opponent']} defeated[/bold green] "
               f"({match.rounds_won}-{match.rounds_lost})", style="bold green")

        if match_idx < 4:
            cprint(f"\n  Campaign: {match_idx + 1}/5 matches won", style="bold yellow")
        input("  Press Enter to begin Round...")

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
