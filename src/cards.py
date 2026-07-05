"""Card dataclasses for Squad — football card roguelike."""

from dataclasses import dataclass, field


@dataclass
class PlayerCard:
    """A player that can be placed on the field."""
    id: str
    name: str
    position: str  # ST, RW, LW, CM, CDM, CB, FB, GK
    atk: int       # 1-10
    pac: int       # 1-10
    pas: int       # 1-10
    def_: int      # 1-10
    spc: int       # 1-10 (special — flair, set pieces, technique)
    traits: list[str] = field(default_factory=list)
    description: str = ""

    def has_trait(self, trait: str) -> bool:
        return trait in self.traits

    @property
    def cost(self) -> int:
        """Player cost = sum of all stats (for squad budget)."""
        return self.atk + self.pac + self.pas + self.def_ + self.spc


@dataclass
class SynergyCard:
    """A permanent passive modifier card (like Balatro's Jokers)."""
    id: str
    name: str
    rarity: str  # common, uncommon, rare
    trigger_type: str
    trigger: dict
    alt_trigger: dict | None = None
    effect_type: str = "multiply"
    effect: dict = field(default_factory=dict)
    description: str = ""
    persistent: bool = False  # Squad-persistent (trait-based) vs phase-specific


@dataclass
class FormationCard:
    """Determines field slots and global multiplier."""
    id: str
    name: str
    slots: list[str]       # ordered list of position slots
    hand_size: int         # cards drawn per round
    global_mult: float     # formation multiplier (e.g. 1.0 for 4-4-2, 1.2 for 4-3-3)
    position_bonus: dict[str, int] = field(default_factory=dict)  # e.g. {"CB": 20, "LW": 5}
    description: str = ""
