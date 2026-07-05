"""Console output — shared cprint/clear_screen used by all UI components."""

# ─── Rich formatting (optional) ──────────────────────────────────────
try:
    from rich.console import Console
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def cprint(text: str, style: str = "", end: str = "\n") -> None:
    """Print with optional Rich styling."""
    if HAS_RICH:
        console.print(text, style=style, end=end)
    else:
        print(text, end=end)


def clear_screen() -> None:
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="")
