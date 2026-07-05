"""Synergy info panel — shows fired synergies with contributors and rules."""

from main import cprint


class SynergyBox:
    """Renders synergy information in a dedicated panel."""
    
    @staticmethod
    def render_phase_synergies(
        fired_synergies: list[str],
        contributors: dict[str, list[str]],
        descriptions: dict[str, str],
    ) -> None:
        """Render phase-specific synergies that fired.
        
        Args:
            fired_synergies: List of synergy names (may include "(persistent)")
            contributors: Dict of synergy_name → list of player names
            descriptions: Dict of synergy_name → rule description
        """
        # Filter out persistent synergies
        phase_syns = [s for s in fired_synergies if "(persistent)" not in s]
        
        if not phase_syns:
            return
        
        cprint("\n  [bold yellow]⚡ SYNERGIES FIRED[/bold yellow]", style="bold yellow")
        cprint("  " + "┌" + "─" * 52 + "┐", style="dim")
        
        for syn_name in phase_syns:
            clean_name = syn_name.split(" (")[0]
            
            # Get contributors
            players = contributors.get(clean_name, [])
            players_str = " + ".join(players) if players else "—"
            
            # Get description
            desc = descriptions.get(clean_name, "")
            
            # Render
            cprint(f"  │  [bold]{clean_name:22s}[/bold]  {players_str:25s}│", style="yellow")
            if desc:
                cprint(f"  │  {'':22s}  [dim]{desc:25s}[/dim]│", style="dim")
        
        cprint("  " + "└" + "─" * 52 + "┘", style="dim")
