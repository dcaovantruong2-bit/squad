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

# ─── Constants ──────────────────────────────────────────────────────────
BUDGET = 360
MIN_TOTAL = 10

# Pre-load all synergies for computing synergy potential in the builder
_ALL_SYNERGIES = load_synergies()

# Role groups — flexible buckets instead of rigid per-position minimums.
# You must fill each group with the specified minimum across any of its positions.
ROLE_GROUPS = {
    "GK": {"positions": ["GK"], "min": 1, "label": "1 GK"},
    "Defenders": {"positions": ["CB", "FB"], "min": 3, "label": "3+ Defenders (CB/FB)"},
    "Midfielders": {"positions": ["CM", "CDM", "CAM"], "min": 3, "label": "3+ Midfielders (CM/CDM/CAM)"},
    "Attackers": {"positions": ["ST", "LW", "RW"], "min": 2, "label": "2+ Attackers (ST/LW/RW)"},
}


def check_minimums(squad: list[PlayerCard]) -> list[str]:
    """Return list of unmet requirements (empty = squad is valid)."""
    pos_counts = Counter(p.position for p in squad)
    missing = []

    for group_name, cfg in ROLE_GROUPS.items():
        total = sum(pos_counts.get(pos, 0) for pos in cfg["positions"])
        if total < cfg["min"]:
            missing.append(f"{cfg['label']} (have {total})")

    if len(squad) < MIN_TOTAL:
        missing.append(f"10 players minimum (have {len(squad)})")

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

    position_order = ["GK", "CB", "FB", "CDM", "CM", "CAM", "LW", "RW", "ST"]

    def pos_label(pos):
        icons = {"GK": "🧤", "CB": "🛡️", "FB": "↔️", "CDM": "🔧", "CM": "🔄",
                 "CAM": "🎯", "LW": "⬅️", "RW": "➡️", "ST": "⚽"}
        return icons.get(pos, "")

    def clear():
        print("\033[2J\033[H", end="")

    def show_screen():
        clear()
        # ── Header ──
        remaining = BUDGET - spent
        bar_len = 20
        filled = int((spent / BUDGET) * bar_len) if BUDGET > 0 else 0
        bar = "█" * min(filled, bar_len) + "░" * (bar_len - min(filled, bar_len))

        print(f"  ╔═══════════════════════════════════════════════════╗")
        print(f"  ║           ⚽  BUILD YOUR SQUAD  ⚽              ║")
        print(f"  ╚═══════════════════════════════════════════════════╝")
        print(f"\n  Budget: {spent:3d} / {BUDGET} spent  [{bar}]  {remaining:3d} remaining")
        print(f"  Squad: {len(selected)} players  |  Minimum: {MIN_TOTAL} required")

        # ── Available players ──
        selected_ids = {p.id for p in selected}
        # Pre-compute synergy potential for each player (considering current selected squad)
        syn_cache = {}
        if selected:
            for p in by_pos.values():
                for player in p:
                    if player.id not in selected_ids:
                        syns = compute_synergy_potential(player, selected + [player], _ALL_SYNERGIES)
                        syn_cache[player.id] = len(syns)
        print(f"\n  [bold]AVAILABLE PLAYERS:[/bold]")
        idx = 0
        for pos in position_order:
            players = by_pos.get(pos, [])
            if not players:
                continue
            print(f"\n  {pos_label(pos)} {pos}:")
            for p in players:
                if p.id in selected_ids:
                    continue
                cost_display = f"{'*CAN AFFORD' if remaining >= p.cost else '⬆ TOO EXPENSIVE':14s}"
                syn_tag = ""
                if p.id in syn_cache:
                    sc = syn_cache[p.id]
                    if sc > 0:
                        syn_tag = f" ⚡{sc}"
                if remaining >= p.cost:
                    print(f"    [{idx:2d}] {p.name:22s}  cost:{p.cost:2d}  CAN AFFORD{syn_tag}  "
                           f"ATK:{p.atk} PAC:{p.pac} PAS:{p.pas} DEF:{p.def_} SPC:{p.spc}")
                else:
                    print(f"    [{idx:2d}] {p.name:22s}  cost:{p.cost:2d}  TOO EXPENSIVE{syn_tag}  "
                           f"ATK:{p.atk} PAC:{p.pac} PAS:{p.pas} DEF:{p.def_} SPC:{p.spc}")
                idx += 1

        # ── Selected players ──
        print(f"\n  [bold]YOUR SQUAD ({len(selected)} players, {spent} coins):[/bold]")
        if selected:
            for i, p in enumerate(selected):
                print(f"    [{i:2d}] {p.name:22s}  [{p.position:3s}]  cost:{p.cost:2d}")
        else:
            print(f"    (no players picked yet)")

        # ── Role-group requirements status ──
        missing = check_minimums(selected)
        if missing:
            print(f"\n  ⚠️  Unmet requirements:")
            for m in missing:
                print(f"      ✗ {m}")
        else:
            print(f"\n  ✅  Minimum requirements met! Type 'done' to proceed.")

        # Show a quick role-group summary
        pos_counts = Counter(p.position for p in selected)
        total_positions = sum(pos_counts.values())
        if total_positions > 0:
            print(f"\n  [bold]Role breakdown:[/bold]")
            for group_name, cfg in ROLE_GROUPS.items():
                total = sum(pos_counts.get(pos, 0) for pos in cfg["positions"])
                ok = total >= cfg["min"]
                icon = "✅" if ok else "⬜"
                positions_str = "/".join(cfg["positions"])
                print(f"    {icon} {cfg['label']:30s}  ({total}/{cfg['min']})  [{positions_str}]")

        print(f"\n  Commands:")
        print(f"    <number>  — Pick a player by their [number] above")
        print(f"    drop <#>  — Remove a player from your squad by index")
        print(f"    done      — Finalize squad and start match")
        print(f"    help      — Show this help")

    # Map flat index → player for picking
    def build_available_list():
        selected_ids = {p.id for p in selected}
        result = []
        for pos in position_order:
            for p in by_pos.get(pos, []):
                if p.id not in selected_ids:
                    result.append(p)
        return result

    # ── Main loop ──
    while True:
        show_screen()

        try:
            cmd = input("\n  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        if cmd == "help":
            input("\n  Press Enter to continue...")
            continue

        if cmd == "done":
            missing = check_minimums(selected)
            if missing:
                print(f"\n  ❌  Can't start — missing:")
                for m in missing:
                    print(f"      ✗ {m}")
                input("  Press Enter to continue building...")
                continue
            if len(selected) < MIN_TOTAL:
                print(f"\n  ❌  Need at least {MIN_TOTAL} players (have {len(selected)}).")
                input("  Press Enter to continue building...")
                continue
            break

        if cmd.startswith("drop "):
            try:
                idx = int(cmd.split()[1])
                if 0 <= idx < len(selected):
                    dropped = selected.pop(idx)
                    spent -= dropped.cost
                    print(f"\n  Dropped {dropped.name}. Refunded {dropped.cost} coins.")
                    input("  Press Enter...")
                else:
                    print(f"\n  Invalid squad index. Pick 0-{len(selected)-1}.")
                    input("  Press Enter...")
            except (ValueError, IndexError):
                print("\n  Usage: drop <squad_index>")
                input("  Press Enter...")
            continue

        # Try picking by number
        try:
            pick_idx = int(cmd)
        except ValueError:
            print(f"\n  Unknown command: '{cmd}'")
            input("  Press Enter...")
            continue

        available = build_available_list()
        if 0 <= pick_idx < len(available):
            player = available[pick_idx]
            remaining = BUDGET - spent
            if remaining < player.cost:
                print(f"\n  ❌  {player.name} costs {player.cost}, you only have {remaining} coins.")
                input("  Press Enter...")
                continue
            selected.append(player)
            spent += player.cost
            print(f"\n  ✅  Picked {player.name} [{player.position}] for {player.cost} coins.")
            input("  Press Enter...")
        else:
            print(f"\n  Invalid number. Pick 0-{len(available)-1}.")
            input("  Press Enter...")

    # ── Done ──
    clear()
    total = sum(p.cost for p in selected)
    print(f"\n  ╔═══════════════════════════════════════════════════╗")
    print(f"  ║           SQUAD FINALIZED                        ║")
    print(f"  ╚═══════════════════════════════════════════════════╝")
    print(f"\n  Your Squad ({len(selected)} players, {total} / {BUDGET} coins):")
    print(f"\n{format_squad_report(selected)}")
    print(f"\n  Remaining budget: {BUDGET - total} coins (unused)")
    input("\n  Press Enter to continue...")

    return selected
