"""Persistent context bar — always-visible game state at top of screen."""

from src.ui.console import cprint


class ContextBar:
    """Renders the persistent top bar showing round/score/target/phase."""
    
    def __init__(self, match_state):
        self.match = match_state
    
    def render(self) -> None:
        """Show the context bar."""
        round_num = self.match.current_round + 1
        phase_idx = self.match.current_phase_idx + 1
        score = self.match.round_score
        target = self.match.current_target
        won = self.match.rounds_won
        lost = self.match.rounds_lost
        
        # Format: R1/3 │ Score: 187/500 │ 1-0 │ Phase 2/6
        bar = (
            f"  [bold]R{round_num}/3[/bold]  │  "
            f"Score: [bold cyan]{score}/{target}[/bold cyan]  │  "
            f"[bold]{won}-{lost}[/bold]  │  "
            f"Phase {phase_idx}/6"
        )
        
        cprint("", style="")  # blank line
        cprint(bar, style="bold")
        cprint("  " + "─" * 55, style="dim")
