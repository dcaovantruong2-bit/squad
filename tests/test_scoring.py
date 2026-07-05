"""Tests for scoring engine — chips calculation."""

import pytest
from src.scoring import calculate_chips, CHIPS_FORMULA


class TestChipsFormula:
    """Test that each position weights the right stats."""

    def test_striker_chips(self, terry_henri):
        """ST: atk*3 + pac*2 + spc*1 = 9*3 + 9*2 + 8*1 = 27+18+8 = 53"""
        assert calculate_chips(terry_henri, "ST") == 53

    def test_winger_chips(self, bale_out):
        """LW: atk*2 + pac*3 + pas*1 = 8*2 + 10*3 + 6*1 = 16+30+6 = 52"""
        assert calculate_chips(bale_out, "LW") == 52

    def test_rw_chips(self, rob_cutter):
        """RW: atk*2 + pac*3 + pas*1 = 8*2 + 9*3 + 6*1 = 16+27+6 = 49"""
        assert calculate_chips(rob_cutter, "RW") == 49

    def test_cm_chips(self, maestro_xav):
        """CM: pas*3 + atk*1 + def*2 = 10*3 + 3*1 + 6*2 = 30+3+12 = 45"""
        assert calculate_chips(maestro_xav, "CM") == 45

    def test_cdm_chips(self, wall_claude):
        """CDM: def*3 + pas*2 + atk*1 = 10*3 + 6*2 + 2*1 = 30+12+2 = 44"""
        assert calculate_chips(wall_claude, "CDM") == 44

    def test_cb_chips(self, il_capitano):
        """CB: def*4 + spc*1 + pac*1 = 10*4 + 5*1 + 6*1 = 40+5+6 = 51"""
        assert calculate_chips(il_capitano, "CB") == 51

    def test_fb_chips(self, el_tren):
        """FB: def*2 + pac*3 + pas*1 = 7*2 + 9*3 + 7*1 = 14+27+7 = 48"""
        assert calculate_chips(el_tren, "FB") == 48

    def test_unknown_position_raises(self, terry_henri):
        with pytest.raises(KeyError):
            calculate_chips(terry_henri, "GOALKEEPER")


class TestChipsScaling:
    """Verify that better stats = more chips."""

    def test_higher_atk_more_chips(self):
        from src.cards import PlayerCard
        weak = PlayerCard("x", "X", "ST", atk=1, pac=5, pas=5, def_=1, spc=5, traits=[])
        strong = PlayerCard("y", "Y", "ST", atk=10, pac=5, pas=5, def_=1, spc=5, traits=[])
        assert calculate_chips(strong, "ST") > calculate_chips(weak, "ST")

    def test_same_player_different_positions(self, captain_stevie):
        """Captain Stevie (ATK 8, PAS 8, DEF 6) at CM vs CDM should differ."""
        cm_chips = calculate_chips(captain_stevie, "CM")
        cdm_chips = calculate_chips(captain_stevie, "CDM")
        # CM: pas*3+atk*1+def*2=24+8+12=44. CDM: def*3+pas*2+atk*1=18+16+8=42
        assert cm_chips != cdm_chips
