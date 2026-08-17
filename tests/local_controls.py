import pytest
from src.filters import evaluate_peptide, FilterConfig

# ==============================================================================
# INDONESIAN & TROPICAL FOOD BIOACTIVE CONTROLS
# ==============================================================================

# 1. Fermented Soybean / Tempeh Bioactive Peptide Fragment (Glycinin hydrophobic core)
TEMPEH_GLYCININ_PEPTIDE = "VLIVVPK"  # 7 aa

# 2. Casocidin-I (Bovine Milk Beta-Casein Antimicrobial Fragment 165-203)
# Sequence: KTKLTEEEKNRLNFLKKISQRYQKFALPQYLKTVYQHQK (39 aa)
CASOCIDIN_I = "KTKLTEEEKNRLNFLKKISQRYQKFALPQYLKTVYQHQK"

# 3. Hen Egg White Lysozyme Active Antimicrobial Helix (Residues 87-115)
# Sequence: DITASVNCAKKIVSDGNGMNAWVAWRNRCK (30 aa)
LYSOZYME_HELIX_FRAGMENT = "DITASVNCAKKIVSDGNGMNAWVAWRNRCK"

# 4. Coconut / Plant Defensin-like Antimicrobial Segment
COCONUT_DEFENSIN_FRAGMENT = "RTCESQSHKFKGPCASDHNCASVCQTERFSGGHCRGFRRRCFCTTHC"


class TestLocalFoodBioactivePeptides:
    """Evaluates behavioral profiling of food-derived peptides in tropical matrices."""

    def test_tempeh_glycinin_short_peptide(self):
        """Tempeh peptide has high aliphatic index due to Val/Leu/Ile density."""
        res = evaluate_peptide("Tempeh_Glycinin_F1", TEMPEH_GLYCININ_PEPTIDE)
        
        assert res["length"] == 7
        # Highly aliphatic (Val, Leu, Ile = 6/7 residues)
        assert res["aliphatic_index"] > 180.0
        assert res["thermostability_tier"] == "Gold Standard (AI >= 80)"

    def test_casocidin_antimicrobial_peptide(self):
        """Casocidin-I from milk is an established natural food antimicrobial."""
        config_amp = FilterConfig.permissive_amp_preset()
        res = evaluate_peptide("Milk_Casocidin_I", CASOCIDIN_I, config=config_amp)

        assert res["charge_ph6"] >= 3.0
        assert res["isoelectric_point"] >= 9.5
        assert res["passed_all_filters"] is True

    def test_lysozyme_fragment_membrane_affinity(self):
        """Lysozyme helix fragment possesses high cationic charge and membrane selectivity."""
        config_amp = FilterConfig.permissive_amp_preset()
        res = evaluate_peptide("Lysozyme_Helix_87_115", LYSOZYME_HELIX_FRAGMENT, config=config_amp)

        assert res["charge_ph6"] >= 2.0
        assert 0.0 <= res["boman_index"] <= 2.5
        assert res["passed_all_filters"] is True

    def test_comparative_profiling_output(self):
        """Verifies that all local controls return valid data contracts without runtime exception."""
        test_peptides = [
            ("Tempeh_Glycinin", TEMPEH_GLYCININ_PEPTIDE),
            ("Milk_Casocidin", CASOCIDIN_I),
            ("Egg_Lysozyme", LYSOZYME_HELIX_FRAGMENT),
            ("Plant_Defensin", COCONUT_DEFENSIN_FRAGMENT)
        ]
        for pid, seq in test_peptides:
            res = evaluate_peptide(pid, seq)
            assert "id" in res
            assert "as35_score" in res
            assert isinstance(res["failed_reasons"], list)
