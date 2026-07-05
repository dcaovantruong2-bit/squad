"""Compact player card display with fatigue and synergy info."""

from src.ui.console import cprint
from src.ui.colors import color_for_fatigue, fatigue_label
from src.scoring import calculate_chips


class PlayerCardView:
    """Renders a compact player card for selection screens."""
    
    @staticmethod
    def render_eligible(
        player,
        slot_pos: str,
        fatigue: float,
        chips: int,
        synergy_tags: list[str] = None,
        carryover_bonus: int = 0,
        show_index: bool = True,
        index: int = 0,
    ) -> None:
        """Render a player card for the eligible players list.
        
        Args:
            player: PlayerCard instance
            slot_pos: Position they'll play in this slot
            fatigue: Fatigue multiplier (1.0 = fresh)
            chips: Base chips for this position
            synergy_tags: List of synergy names this player would unlock
            carryover_bonus: Bonus chips from carryover (if applicable)
            show_index: Whether to show [index] prefix
            index: Player index number
        """
        effective = int(chips * fatigue)
        color = color_for_fatigue(fatigue)
        fat_label = fatigue_label(fatigue)
        
        # Build the line
        parts = []
        if show_index:
            parts.append(f"[{index}]")
        
        parts.append(f"{player.name:18s}")
        parts.append(f"{player.position}→{slot_pos:3s}")
        parts.append(f"{fat_label:5s}")
        parts.append(f"{effective:3d} chips")
        
        # Stats summary (most relevant for this position)
        stats = f"ATK:{player.atk} PAC:{player.pac} PAS:{player.pas} DEF:{player.def_} SPC:{player.spc}"
        parts.append(stats)
        
        # Synergy tags
        if synergy_tags:
            syn_str = ", ".join(synergy_tags[:2])
            parts.append(f"⚡{syn_str}")
            if len(synergy_tags) > 2:
                parts.append(f"+{len(synergy_tags) - 2}")
        
        # Carryover bonus
        if carryover_bonus > 0:
            parts.append(f"📦+{carryover_bonus}")
        
        line = "  ".join(parts)
        cprint(f"    {line}", style=color)
