"""Load card data from TOML files into dataclass objects."""

import tomllib
from pathlib import Path

from src.cards import PlayerCard, SynergyCard

DATA_DIR = Path(__file__).parent.parent / "data"


def load_players() -> list[PlayerCard]:
    """Load all player cards from data/players.toml."""
    with open(DATA_DIR / "players.toml", "rb") as f:
        data = tomllib.load(f)

    players = []
    for p in data["players"]:
        players.append(PlayerCard(
            id=p["id"],
            name=p["name"],
            position=p["position"],
            atk=p["atk"],
            pac=p["pac"],
            pas=p["pas"],
            def_=p["def_"],
            spc=p["spc"],
            traits=p.get("traits", []),
            description=p.get("description", ""),
        ))
    return players


def load_synergies() -> list[SynergyCard]:
    """Load all synergy cards from data/synergies.toml."""
    with open(DATA_DIR / "synergies.toml", "rb") as f:
        data = tomllib.load(f)

    synergies = []
    for s in data["synergies"]:
        synergies.append(SynergyCard(
            id=s["id"],
            name=s["name"],
            rarity=s.get("rarity", "common"),
            trigger_type=s["trigger_type"],
            trigger=s["trigger"],
            alt_trigger=s.get("alt_trigger"),
            effect_type=s.get("effect_type", "multiply"),
            effect=s.get("effect", {}),
            description=s.get("description", ""),
            persistent=s.get("persistent", False),
        ))
    return synergies


def load_all():
    """Load all card types at once."""
    return {
        "players": load_players(),
        "synergies": load_synergies(),
    }
