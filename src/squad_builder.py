"""Squad builder — pick your squad within budget, role-group minimums enforced.

Flow:
  1. See full player pool with costs grouped by position
  2. Pick until budget exhausted or you're happy
  3. Must meet role-group minimums:
     - 1 GK (unique position)
     - 3+ Defenders (CB/FB combined)
     - 3+ Midfielders (CM/CDM/CAM combined)
     - 2+ Attackers (ST/LW/RW combined)
     - 10+ players total
"""

from collections import Counter, defaultdict
from src.cards import PlayerCard
from src.loader import load_synergies
from src.scoring import compute_synergy_potential
from src.ui.console import cprint, clear_screen

# ─── Constants ──────────────────────────────────────────────────────────
BUDGET = 360
MIN_TOTAL = 11

# Pre-load all synergies for computing synergy potential in the builder
_ALL_SYNERGIES = load_synergies()

# Role groups — flexible buckets instead of rigid per-position minimums.
# You must fill each group with the specified minimum across any of its positions.
ROLE_GROUPS = {
    "GK": {"positions": ["GK"], "min": 1, "label": "Goalkeeper", "icon": "🧤"},
    "Defenders": {"positions": ["CB", "FB"], "min": 3, "label": "Defenders (CB/FB)", "icon": "🛡️"},
    "Midfielders": {"positions": ["CM", "CDM", "CAM"], "min": 3, "label": "Midfielders (CM/CDM/CAM)", "icon": "🔄"},
    "Attackers": {"positions": ["ST", "LW", "RW"], "min": 2, "label": "Attackers (ST/LW/RW)", "icon": "⚽"},
}

# Position display config
POSITION_CONFIG = {
    "GK": {"icon": "🧤", "color": "cyan"},
    "CB": {"icon": "🛡️", "color": "blue"},
    "FB": {"icon": "↔️", "color": "cyan"},
    "CDM": {"icon": "🔧", "color": "yellow"},
    "CM": {"icon": "🔄", "color": "yellow"},
    "CAM": {"icon": "🎯", "color": "yellow"},
    "LW": {"icon": "⬅️", "color": "green"},
    "RW": {"icon": "➡️", "color": "green"},
    "ST": {"icon": "⚽", "color": "green"},
}
POSITION_ORDER = ["GK", "CB", "FB", "CDM", "CM", "CAM", "LW", "RW", "ST"]


def check_minimums(squad: list[PlayerCard]) -> list[str]:
    """Return list of unmet requirements (empty = squad is valid)."""
    pos_counts = Counter(p.position for p in squad)
    missing = []

    for group_name, cfg in ROLE_GROUPS.items():
        total = sum(pos_counts.get(pos, 0) for pos in cfg["positions"])
        if total < cfg["min"]:
            missing.append(f"{cfg['label']} (have {total})")

    if len(squad) < MIN_TOTAL:
        missing.append(f"11 players minimum (have {len(squad)})")

    return missing


def format_squad_report(squad: list[PlayerCard]) -> str:
    """Return a multi-line summary of the squad grouped by position."""
    from collections import defaultdict
    by_pos = defaultdict(list)
    for p in squad:
        by_pos[p.position].append(p)

    lines = []
    for label in ["GK", "CB", "FB", "CDM", "CM", "CAM", "LW", "RW", "ST"]:
        players = by_pos.get(label, [])
        if players:
            names = ", ".join(p.name for p in players)
            lines.append(f"    {label:4s}: {names}")
    return "\n".join(lines)


def build_squad(all_players: list[PlayerCard]) -> list[PlayerCard]:
    """Interactive squad builder. Returns the player's chosen squad."""
    from collections import defaultdict

    # ── Group players by position ──
    by_pos = defaultdict(list)
    for p in all_players:
        by_pos[p.position].append(p)

    selected: list[PlayerCard] = []
    spent = 0

    def render_role_bar():
        """Show role requirements as a compact progress bar."""
        pos_counts = Counter(p.position for p in selected)
        parts = []
        for group_name, cfg in ROLE_GROUPS.items():
            total = sum(pos_counts.get(pos, 0) for pos in cfg["positions"])
            ok = total >= cfg["min"]
            status = f"[green]{total}[/green]" if ok else f"[red]{total}[/red]"
            parts.append(f"  {cfg['icon']} {cfg['icon'] if ok else ''} {cfg['label']}: {status}/{cfg['min']}")
        cprint("  " + " │".join(parts), style="bold")

    def render_budget_bar():
        """Show visual budget bar."""
        remaining = BUDGET - spent
        bar_len = 25
        filled = int((spent / BUDGET) * bar_len) if BUDGET > 0 else 0
        bar = "█" * min(filled, bar_len) + "░" * (bar_len - min(filled, bar_len))
        bar_color = "green" if remaining > BUDGET * 0.2 else "yellow" if remaining > BUDGET * 0.1 else "red"
        cprint(f"\n  Budget: [bold {bar_color}]{spent:3d} / {BUDGET}[/bold {bar_color}]  [{bar_color}]{bar}[/{bar_color}]  [bold]{remaining:3d} left[/bold]", style="bold")
        cprint(f"  Squad: [bold]{len(selected)}[/bold] players  (min {MIN_TOTAL} required)", style="dim")

    def render_selected_squad():
        """Show currently selected players with synergy tags."""
        cprint("\n  [bold underline]YOUR SQUAD[/bold underline]", style="bold green")
        
        if not selected:
            cprint("    [dim](no players picked yet)[/dim]", style="dim")
            return
        
        # Pre-compute synergy potential for the current selection
        syn_cache = {}
        if selected:
            for p in selected:
                other = [s for s in selected if s.id != p.id]
                syns = compute_synergy_potential(p, other + [p], _ALL_SYNERGIES)
                syn_cache[p.id] = syns
        
        for i, p in enumerate(selected):
            syn_tags = syn_cache.get(p.id, [])
            syn_str = ""
            if syn_tags:
                shown = syn_tags[:2]
                syn_str = f"  [yellow]⚡{', '.join(shown)}[/yellow]"
                if len(syn_tags) > 2:
                    syn_str += f"[yellow]+{len(syn_tags)-2}[/yellow]"
            
            cprint(f"    [{i:2d}] {p.name:22s}  [{p.position:3s}]  cost:[bold]{p.cost:2d}[/bold]{syn_str}", style="bold")

    def render_available_players():
        """Show available players grouped by position."""
        cprint("\n  [bold underline]AVAILABLE PLAYERS[/bold underline]", style="bold cyan")
        
        selected_ids = {p.id for p in selected}
        remaining = BUDGET - spent
        
        # Pre-compute synergy potential for each player
        syn_cache = {}
        if selected:
            for players in by_pos.values():
                for player in players:
                    if player.id not in selected_ids:
                        syns = compute_synergy_potential(player, selected + [player], _ALL_SYNERGIES)
                        syn_cache[player.id] = len(syns)
        
        # Flat index for picking
        idx = 0
        for pos in POSITION_ORDER:
            players = by_pos.get(pos, [])
            avail = [p for p in players if p.id not in selected_ids]
            if not avail:
                continue
            
            cfg = POSITION_CONFIG.get(pos, {"icon": "", "color": "dim"})
            cprint(f"\n  {cfg['icon']} [bold underline]{pos}[/bold underline] ({len(avail)} available)", style=cfg['color'])
            
            for p in avail:
                can_afford = remaining >= p.cost
                cost_style = "bold green" if can_afford else "bold red"
                cost_label = "CAN AFFORD" if can_afford else "TOO EXPENSIVE"
                
                syn_tag = ""
                if p.id in syn_cache:
                    sc = syn_cache[p.id]
                    if sc > 0:
                        syn_tag = f"  [yellow]⚡{sc}[/yellow]"
                
                cprint(f"    [{idx:2d}] {p.name:22s}  cost:[{cost_style}]{p.cost:2d}[/{cost_style}]  {cost_label:12s}"
                       f"  ATK:{p.atk} PAC:{p.pac} PAS:{p.pas} DEF:{p.def_} SPC:{p.spc}{syn_tag}",
                       style="dim" if not can_afford else "")
                idx += 1
        
        return idx

    # Build flat index → player mapping
    def build_available_list():
        selected_ids = {p.id for p in selected}
        result = []
        for pos in POSITION_ORDER:
            for p in by_pos.get(pos, []):
                if p.id not in selected_ids:
                    result.append(p)
        return result

    # ── Main loop ──
    while True:
        clear_screen()
        
        # ── Zone 1: Header + Budget ──
        cprint("  ╔═══════════════════════════════════════════════════╗", style="bold cyan")
        cprint("  ║           ⚽  BUILD YOUR SQUAD  ⚽              ║", style="bold cyan")
        cprint("  ╚═══════════════════════════════════════════════════╝", style="bold cyan")
        render_budget_bar()
        
        # ── Zone 1b: Role requirements ──
        cprint("")
        render_role_bar()
        missing = check_minimums(selected)
        if missing:
            cprint("    [red]" + "  ✗ ".join([""] + missing) + "[/red]", style="red")
        else:
            cprint("    [green]✅ All minimum requirements met![/green]", style="green")
        
        # ── Zone 2: Your Squad ──
        cprint("\n  " + "─" * 55, style="dim")
        render_selected_squad()
        
        # ── Zone 3: Available Players ──
        cprint("\n  " + "─" * 55, style="dim")
        render_available_players()
        
        # ── Commands ──
        cprint("\n  [dim]Commands: <number>=pick  |  drop <#>=remove  |  done=finalize  |  help[/dim]", style="dim")
        
        try:
            cmd = input("\n  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        if cmd == "help":
            input("  Press Enter to continue...")
            continue

        if cmd == "done":
            missing = check_minimums(selected)
            if missing:
                cprint("  [red]❌ Can't start — missing requirements:[/red]", style="red")
                for m in missing:
                    cprint(f"      ✗ {m}", style="red")
                input("  Press Enter to continue building...")
                continue
            if len(selected) < MIN_TOTAL:
                cprint(f"  [red]❌ Need at least {MIN_TOTAL} players (have {len(selected)}).[/red]", style="red")
                input("  Press Enter to continue building...")
                continue
            break

        if cmd.startswith("drop "):
            try:
                idx = int(cmd.split()[1])
                if 0 <= idx < len(selected):
                    dropped = selected.pop(idx)
                    spent -= dropped.cost
                    cprint(f"\n  [green]Dropped {dropped.name}. Refunded {dropped.cost} coins.[/green]", style="green")
                    input("  Press Enter...")
                else:
                    cprint(f"\n  [red]Invalid squad index. Pick 0-{len(selected)-1}.[/red]", style="red")
                    input("  Press Enter...")
            except (ValueError, IndexError):
                cprint("\n  [red]Usage: drop <squad_index>[/red]", style="red")
                input("  Press Enter...")
            continue

        # Try picking by number
        try:
            pick_idx = int(cmd)
        except ValueError:
            cprint(f"\n  [red]Unknown command: '{cmd}'[/red]", style="red")
            input("  Press Enter...")
            continue

        available = build_available_list()
        if 0 <= pick_idx < len(available):
            player = available[pick_idx]
            remaining = BUDGET - spent
            if remaining < player.cost:
                cprint(f"\n  [red]❌ {player.name} costs {player.cost}, you only have {remaining} coins.[/red]", style="red")
                input("  Press Enter...")
                continue
            selected.append(player)
            spent += player.cost
            cprint(f"\n  [green]✅ Picked {player.name} [{player.position}] for {player.cost} coins.[/green]", style="green")
            input("  Press Enter...")
        else:
            cprint(f"\n  [red]Invalid number. Pick 0-{len(available)-1}.[/red]", style="red")
            input("  Press Enter...")

    # ── Done ──
    clear_screen()
    total = sum(p.cost for p in selected)
    cprint("  ╔═══════════════════════════════════════════════════╗", style="bold cyan")
    cprint("  ║           SQUAD FINALIZED                        ║", style="bold cyan")
    cprint("  ╚═══════════════════════════════════════════════════╝", style="bold cyan")
    cprint(f"\n  [bold]Your Squad ({len(selected)} players, {total} / {BUDGET} coins):[/bold]", style="bold")
    cprint(f"\n{format_squad_report(selected)}", style="bold")
    if BUDGET - total > 0:
        cprint(f"\n  Remaining budget: {BUDGET - total} coins (unused)", style="dim")
    input("\n  Press Enter to continue...")

    return selected
