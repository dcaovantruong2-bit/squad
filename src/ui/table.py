"""Aligned table renderer for scoring breakdowns."""

from src.ui.console import cprint


class Table:
    """Renders aligned columnar data."""
    
    @staticmethod
    def render_phase_breakdown(breakdown: list[dict]) -> None:
        """Render the phase scoring breakdown as an aligned table.
        
        Args:
            breakdown: List of per-player scoring entries
        """
        # Header
        header = (
            f"  {'Player':20s}  {'Pos':3s}  "
            f"{'Base':>4s}  {'+Syn':>4s}  {'×Mult':>5s}  {'×Fat':>5s}  "
            f"{'= Sub':>6s}"
        )
        cprint(header, style="bold cyan")
        cprint("  " + "─" * 58, style="dim")
        
        # Rows
        for entry in breakdown:
            base = entry['base_chips']
            add = entry['add_chips']
            mult = entry['multiply']
            fat = entry['fatigue']
            subtotal = entry['subtotal']
            
            # Color based on fatigue
            color = "cyan" if fat >= 1.0 else "yellow"
            
            line = (
                f"  {entry['player']:20s}  {entry['position']:3s}  "
                f"{base:4d}  {add:+4d}  "
                f"×{mult:.2f}  ×{fat:.2f}  "
                f"{subtotal:6d}"
            )
            cprint(line, style=color)
