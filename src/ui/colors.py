"""Semantic color helpers for consistent visual language."""

SEMANTIC_COLORS = {
    "fresh": "green",
    "fatigued": "yellow",
    "exhausted": "red",
    "info": "cyan",
    "synergy": "yellow",
    "good": "green",
    "warning": "yellow",
    "danger": "red",
    "neutral": "dim",
    "highlight": "bold yellow",
}


def color_for_fatigue(mult: float) -> str:
    """Return color based on fatigue level."""
    if mult >= 1.0:
        return SEMANTIC_COLORS["fresh"]
    elif mult >= 0.7:
        return SEMANTIC_COLORS["fatigued"]
    else:
        return SEMANTIC_COLORS["exhausted"]


def color_for_value(value: float, thresholds: tuple[float, float]) -> str:
    """Return color based on value vs thresholds (low, high).
    
    Example: color_for_value(75, (50, 80)) → "yellow" (between 50-80)
    """
    low, high = thresholds
    if value >= high:
        return SEMANTIC_COLORS["good"]
    elif value >= low:
        return SEMANTIC_COLORS["warning"]
    else:
        return SEMANTIC_COLORS["danger"]


def fatigue_label(mult: float) -> str:
    """Return human-readable fatigue label."""
    if mult >= 1.0:
        return "FRESH"
    elif mult >= 0.7:
        return f"{int(mult * 100)}%"
    else:
        return f"{int(mult * 100)}%"
