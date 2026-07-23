"""Shared test fixtures for Squad — updated with GK + 3rd CB."""

import pytest
from src.cards import PlayerCard, SynergyCard, FormationCard


@pytest.fixture
def terry_henri():
    return PlayerCard(
        id="terry_henri", name="Terry Henri", position="ST",
        atk=9, pac=9, pas=6, def_=1, spc=8,
        traits=["pacey", "clinical"], description="Clinical speedster"
    )


@pytest.fixture
def big_zlat():
    return PlayerCard(
        id="big_zlat", name="Big Zlat", position="ST",
        atk=8, pac=5, pas=7, def_=2, spc=10,
        traits=["physical", "technical"]
    )


@pytest.fixture
def kun_kun():
    return PlayerCard(
        id="kun_kun", name="El Caníbal", position="ST",
        atk=8, pac=8, pas=5, def_=1, spc=7,
        traits=["pacey", "poacher"]
    )


@pytest.fixture
def the_waz():
    return PlayerCard(
        id="the_waz", name="The Waz", position="ST",
        atk=8, pac=6, pas=7, def_=5, spc=6,
        traits=["physical", "leader"]
    )


@pytest.fixture
def rob_cutter():
    return PlayerCard(
        id="rob_cutter", name="Arjen Cutback", position="RW",
        atk=8, pac=9, pas=6, def_=1, spc=8,
        traits=["pacey", "clinical"]
    )


@pytest.fixture
def bale_out():
    return PlayerCard(
        id="bale_out", name="Bale Out", position="LW",
        atk=8, pac=10, pas=6, def_=3, spc=7,
        traits=["pacey", "physical"]
    )


@pytest.fixture
def maestro_xav():
    return PlayerCard(
        id="maestro_xav", name="The Puppet Master", position="CM",
        atk=3, pac=4, pas=10, def_=6, spc=7,
        traits=["playmaker", "technical"]
    )


@pytest.fixture
def don_andres():
    return PlayerCard(
        id="don_andres", name="Don Andres", position="CM",
        atk=6, pac=7, pas=9, def_=3, spc=10,
        traits=["technical", "playmaker"]
    )


@pytest.fixture
def captain_stevie():
    return PlayerCard(
        id="captain_stevie", name="Captain Stevie", position="CM",
        atk=8, pac=6, pas=8, def_=6, spc=8,
        traits=["leader", "physical"]
    )


@pytest.fixture
def wall_claude():
    return PlayerCard(
        id="wall_claude", name="N'Golo Kanteen", position="CDM",
        atk=2, pac=4, pas=6, def_=10, spc=3,
        traits=["destroyer", "technical"]
    )


@pytest.fixture
def il_capitano():
    return PlayerCard(
        id="il_capitano", name="El Capitán", position="CB",
        atk=3, pac=6, pas=7, def_=10, spc=5,
        traits=["leader", "technical"]
    )


@pytest.fixture
def jt_rock():
    return PlayerCard(
        id="jt_rock", name="Campbell-Soup", position="CB",
        atk=4, pac=3, pas=4, def_=10, spc=4,
        traits=["physical", "aerial"]
    )


@pytest.fixture
def rolls_royce():
    return PlayerCard(
        id="rolls_royce", name="The Rolls Royce", position="CB",
        atk=2, pac=8, pas=6, def_=9, spc=6,
        traits=["technical", "leader"]
    )


@pytest.fixture
def el_tren():
    return PlayerCard(
        id="el_tren", name="Dani Elvis", position="FB",
        atk=5, pac=9, pas=7, def_=7, spc=5,
        traits=["pacey", "physical"]
    )


@pytest.fixture
def mr_reliable():
    return PlayerCard(
        id="mr_reliable", name="Lahm-burger", position="FB",
        atk=3, pac=7, pas=8, def_=9, spc=4,
        traits=["technical", "leader"]
    )


@pytest.fixture
def gigi_wall():
    return PlayerCard(
        id="gigi_wall", name="Gigi The Wall", position="GK",
        atk=1, pac=3, pas=5, def_=10, spc=8,
        traits=["leader", "aerial"]
    )


@pytest.fixture
def frenkie_de_con():
    return PlayerCard(
        id="frenkie_de_con", name="Toni Cruise", position="CDM",
        atk=4, pac=7, pas=10, def_=7, spc=7,
        traits=["technical", "playmaker"]
    )


@pytest.fixture
def cafu_express():
    return PlayerCard(
        id="cafu_express", name="Kyle Jogger", position="FB",
        atk=6, pac=10, pas=7, def_=6, spc=5,
        traits=["pacey", "physical"]
    )


@pytest.fixture
def el_mago():
    return PlayerCard(
        id="el_mago", name="Juan Maestro", position="CAM",
        atk=6, pac=5, pas=10, def_=2, spc=9,
        traits=["technical", "playmaker"]
    )


@pytest.fixture
def sergio_muro():
    return PlayerCard(
        id="sergio_muro", name="Saint Lloris", position="GK",
        atk=1, pac=2, pas=3, def_=10, spc=5,
        traits=["destroyer", "leader"]
    )


@pytest.fixture
def kylian_express():
    return PlayerCard(
        id="kylian_express", name="Dictator Kylian", position="LW",
        atk=7, pac=10, pas=5, def_=2, spc=7,
        traits=["pacey", "clinical"]
    )


@pytest.fixture
def jimmy_journey():
    return PlayerCard(
        id="jimmy_journey", name="Park Ji-zoom", position="CM",
        atk=2, pac=3, pas=5, def_=4, spc=2,
        traits=["physical", "leader", "journeyman"]
    )


@pytest.fixture
def flash_forward():
    return PlayerCard(
        id="flash_forward", name="Theo Walk-not", position="ST",
        atk=4, pac=7, pas=1, def_=1, spc=2,
        traits=["pacey", "poacher"]
    )


@pytest.fixture
def old_man_dan():
    return PlayerCard(
        id="old_man_dan", name="Per Merterslower", position="CB",
        atk=1, pac=1, pas=4, def_=7, spc=2,
        traits=["leader", "aerial"]
    )


@pytest.fixture
def rabona_ron():
    return PlayerCard(
        id="rabona_ron", name="El Shaa-ra-wrong", position="RW",
        atk=4, pac=5, pas=4, def_=1, spc=5,
        traits=["pacey", "clinical"]
    )


@pytest.fixture
def sweaty_keeper():
    return PlayerCard(
        id="sweaty_keeper", name="Claudio Bra-voops", position="GK",
        atk=1, pac=4, pas=3, def_=6, spc=3,
        traits=["aerial"]
    )


@pytest.fixture
def the_crab():
    return PlayerCard(
        id="the_crab", name="The Tank", position="FB",
        atk=1, pac=5, pas=3, def_=6, spc=1,
        traits=["destroyer", "leader"]
    )


@pytest.fixture
def bog_bob():
    return PlayerCard(
        id="bog_bob", name="Nigel de Wrong", position="CDM",
        atk=1, pac=3, pas=4, def_=6, spc=2,
        traits=["destroyer", "physical"]
    )


@pytest.fixture
def cult_carl():
    return PlayerCard(
        id="cult_carl", name="Wilfried Za-ha-ha", position="LW",
        atk=3, pac=6, pas=4, def_=2, spc=3,
        traits=["pacey", "clinical"]
    )


@pytest.fixture
def formation_442():
    return FormationCard(
        id="4-4-2", name="4-4-2",
        slots=["CB", "CB", "FB", "FB", "CM", "CM", "ST", "ST"],
        hand_size=11, global_mult=1.0
    )


@pytest.fixture
def formation_433():
    return FormationCard(
        id="4-3-3", name="4-3-3",
        slots=["CB", "CB", "FB", "FB", "CDM", "CM", "CM", "LW", "RW", "ST"],
        hand_size=12, global_mult=1.2
    )


@pytest.fixture
def clean_sheet_synergy():
    return SynergyCard(
        id="clean_sheet", name="Clean Sheet", rarity="common",
        trigger_type="clean_sheet",
        trigger={"pos_a": "GK", "pos_b": "CB", "stat": "def_", "threshold": 18},
        effect_type="add_chips",
        effect={"add_chips": 20}
    )


@pytest.fixture
def organised_defence_synergy():
    return SynergyCard(
        id="organised_defence", name="Organised Defence", rarity="common",
        trigger_type="organised_defence",
        trigger={"positions": ["CB", "CB"], "stat": "def_", "threshold": 18},
        effect_type="add_chips",
        effect={"add_chips": 20}
    )


@pytest.fixture
def wingback_overlap_synergy():
    return SynergyCard(
        id="wingback_overlap", name="Wingback Overlap", rarity="common",
        trigger_type="wingback_overlap",
        trigger={"pos_a": "FB", "stat_a": "pac", "pos_b": "CM", "stat_b": "pas", "threshold": 15},
        effect_type="add_chips",
        effect={"add_chips": 25}
    )


@pytest.fixture
def overload_synergy():
    return SynergyCard(
        id="overload", name="Overload", rarity="common",
        trigger_type="overload",
        trigger={"min_duplicates": 2},
        effect_type="add_mult",
        effect={"add_mult": 3}
    )


@pytest.fixture
def stretch_backline_synergy():
    return SynergyCard(
        id="stretch_backline", name="Stretch the Backline", rarity="common",
        trigger_type="stretch_backline",
        trigger={"pos_a": "FB", "stat_a": "pac", "pos_b": "LW", "stat_b": "pac", "threshold": 17},
        effect_type="multiply",
        effect={"multiply": 1.5}
    )


@pytest.fixture
def route_one_synergy():
    return SynergyCard(
        id="route_one", name="Route One", rarity="uncommon",
        trigger_type="route_one",
        trigger={"pos_a": "CB", "stat_a": "pas", "pos_b": "ST", "stat_b": "pac", "threshold": 14},
        effect_type="add_chips",
        effect={"add_chips": 30, "target": "ST"}
    )


@pytest.fixture
def battering_ram_synergy():
    return SynergyCard(
        id="battering_ram", name="Battering Ram", rarity="common",
        trigger_type="battering_ram",
        trigger={"pos_a": "CB", "stat_a": "def_", "pos_b": "ST", "stat_b": "atk", "threshold": 17},
        effect_type="add_chips",
        effect={"add_chips": 20}
    )


@pytest.fixture
def defensive_duo_synergy():
    return SynergyCard(
        id="defensive_duo", name="Defensive Duo", rarity="uncommon",
        trigger_type="defensive_duo",
        trigger={"stat": "def_", "threshold": 18},
        effect_type="add_mult",
        effect={"add_mult": 5}
    )


@pytest.fixture
def back_three_synergy():
    return SynergyCard(
        id="back_three", name="Back Three", rarity="rare",
        trigger_type="back_three",
        trigger={"stat": "def_", "threshold": 8},
        effect_type="multiply",
        effect={"multiply": 1.2}
    )


@pytest.fixture
def midfield_engine_synergy():
    return SynergyCard(
        id="midfield_engine", name="Midfield Engine", rarity="common",
        trigger_type="midfield_engine",
        trigger={"positions": ["CM", "CM"], "stat_a": "pas", "stat_b": "def_", "threshold": 17},
        effect_type="add_mult",
        effect={"add_mult": 4}
    )


@pytest.fixture
def double_pivot_synergy():
    return SynergyCard(
        id="double_pivot", name="Double Pivot", rarity="uncommon",
        trigger_type="double_pivot",
        trigger={"positions": ["CM", "CM"], "stat": "pas", "threshold": 18},
        effect_type="carryover",
        effect={"add_chips": 25, "target_role": "attacker"}
    )


@pytest.fixture
def trio_synergy():
    return SynergyCard(
        id="trio", name="Trio", rarity="rare",
        trigger_type="trio",
        trigger={"position": "CM", "stat": "pas", "threshold": 8},
        effect_type="chain_multiply",
        effect={"multipliers": [1.2, 1.25, 1.2]}
    )


@pytest.fixture
def set_piece_synergy():
    return SynergyCard(
        id="set_piece_threat", name="Set Piece Threat", rarity="uncommon",
        trigger_type="set_piece_threat",
        trigger={"stat_a": "def_", "threshold_a": 9, "stat_b": "spc", "threshold_b": 8, "different_players": True},
        effect_type="add_chips",
        effect={"add_chips": 50, "global": True}
    )


@pytest.fixture
def full_squad(terry_henri, big_zlat, kun_kun, the_waz,
                rob_cutter, bale_out,
                maestro_xav, don_andres, captain_stevie,
                wall_claude, frenkie_de_con,
                il_capitano, jt_rock, rolls_royce,
                el_tren, mr_reliable, cafu_express,
                gigi_wall, sergio_muro,
                el_mago, kylian_express,
                jimmy_journey, flash_forward, old_man_dan,
                rabona_ron, sweaty_keeper, the_crab, bog_bob, cult_carl):
    """The complete 29-player squad."""
    return [
        terry_henri, big_zlat, kun_kun, the_waz,
        rob_cutter, bale_out,
        maestro_xav, don_andres, captain_stevie,
        wall_claude, frenkie_de_con,
        il_capitano, jt_rock, rolls_royce,
        el_tren, mr_reliable, cafu_express,
        gigi_wall, sergio_muro,
        el_mago, kylian_express,
        jimmy_journey, flash_forward, old_man_dan,
        rabona_ron, sweaty_keeper, the_crab, bog_bob, cult_carl,
    ]


@pytest.fixture
def all_persistent_synergies():
    """Return ALL persistent synergies from the data file."""
    from src.loader import load_synergies
    return [s for s in load_synergies() if s.persistent]


@pytest.fixture
def pacey_squad(terry_henri, bale_out, el_tren, cafu_express, kylian_express):
    """Squad with 5 pacey players (≥4 threshold for Pace in Behind)."""
    return [terry_henri, bale_out, el_tren, cafu_express, kylian_express]


@pytest.fixture
def physical_squad(captain_stevie, jt_rock, bale_out, the_waz, big_zlat):
    """Squad with 5 physical players (≥3 threshold for Iron Wall)."""
    return [captain_stevie, jt_rock, bale_out, the_waz, big_zlat]


@pytest.fixture
def leader_squad(il_capitano, gigi_wall, captain_stevie, mr_reliable, the_waz):
    """Squad with 5 leader players (≥3 threshold for Leadership Council)."""
    return [il_capitano, gigi_wall, captain_stevie, mr_reliable, the_waz]


@pytest.fixture
def technical_squad(maestro_xav, don_andres, il_capitano, rolls_royce, big_zlat):
    """Squad with 4 technical players (≥3 threshold for Tiki-Taka)."""
    return [maestro_xav, don_andres, il_capitano, rolls_royce, big_zlat]


@pytest.fixture
def clinical_squad(terry_henri, kylian_express, rob_cutter):
    """Squad with 3 clinical players (≥2 threshold for Clinical Edge)."""
    return [terry_henri, kylian_express, rob_cutter]


@pytest.fixture
def destroyer_squad(wall_claude, the_crab, bog_bob, sergio_muro):
    """Squad with 4 destroyer players (≥2 threshold for Double Destroyer)."""
    return [wall_claude, the_crab, bog_bob, sergio_muro]


@pytest.fixture
def poacher_squad(kun_kun, flash_forward):
    """Squad with 2 poacher STs (≥2 threshold for Two Up Top)."""
    return [kun_kun, flash_forward]


@pytest.fixture
def journeyman_squad(jimmy_journey):
    """Squad with the journeyman."""
    return [jimmy_journey]


@pytest.fixture
def pace_power_squad(bale_out, el_tren, cafu_express):
    """Squad with 3 players with both pacey+physical (≥2 threshold)."""
    return [bale_out, el_tren, cafu_express]


@pytest.fixture
def silent_killers_squad(terry_henri, kylian_express, rob_cutter):
    """Squad with 3 players with both clinical+pacey (≥2 threshold)."""
    return [terry_henri, kylian_express, rob_cutter]
