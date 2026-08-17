import pytest
from src.filters import (
    clean_sequence,
    calculate_net_charge,
    calculate_isoelectric_point,
    calculate_aliphatic_index,
    calculate_instability_index,
    calculate_hydrophobic_ratio,
    calculate_gravy,
    calculate_boman_index,
    calculate_as35_score,
    evaluate_peptide,
    evaluate_peptide_batch,
    FilterConfig,
)


# ==============================================================================
# 1. ATOMIC BIOCHEMICAL FUNCTION TESTS
# ==============================================================================

class TestAtomicBiochemicalFormulas:
    """Verifies precision of underlying biophysical and mathematical formulas."""

    def test_clean_sequence_standard(self):
        cleaned, valid, err = clean_sequence("  itsislctpgck   ")
        assert valid is True
        assert cleaned == "ITSISLCTPGCK"
        assert err == ""

    def test_clean_sequence_terminal_stop_codon(self):
        cleaned, valid, err = clean_sequence("MKTATCHCSIHVSK*")
        assert valid is True
        assert cleaned == "MKTATCHCSIHVSK"
        assert err == ""

    def test_clean_sequence_invalid_residues(self):
        cleaned, valid, err = clean_sequence("MKTATXHCSIJBVSZ*")
        assert valid is False
        assert "non-canonical" in err
        assert "X" in err and "J" in err and "B" in err and "Z" in err

    def test_clean_sequence_empty(self):
        cleaned, valid, err = clean_sequence("")
        assert valid is False
        assert cleaned == ""

    def test_henderson_hasselbalch_charge_trends(self):
        # Poly-Lysine (KKKKK): strongly cationic at acidic/neutral pH, deprotonates at alkaline pH
        poly_k = "KKKKK"
        charge_ph2 = calculate_net_charge(poly_k, ph=2.0)
        charge_ph7 = calculate_net_charge(poly_k, ph=7.0)
        charge_ph13 = calculate_net_charge(poly_k, ph=13.0)
        
        assert charge_ph2 > +5.5  # 5 Lys + N-term (+1) - C-term (~0) ~= +6.0
        assert charge_ph7 > +4.5  # 5 Lys + N-term (+1) - C-term (-1) ~= +5.0
        assert charge_ph13 < 0.0  # Fully deprotonated N-term and Lys, C-term ionized (-1)

    def test_isoelectric_point_precision(self):
        # For a neutral Gly-Ala dipeptide: (pKa_Nterm 9.69 + pKa_Cterm 2.34) / 2 = 6.015
        dipeptide = "GA"
        pi = calculate_isoelectric_point(dipeptide)
        assert pytest.approx(pi, 0.01) == 6.015
        # Charge at pI should be approximately 0.0
        assert abs(calculate_net_charge(dipeptide, pi)) < 0.001

    def test_aliphatic_index_formula(self):
        # Ala (A)=1, Val (V)=1, Ile (I)=1, Leu (L)=1 -> Total L=4
        # AI = (1 + 2.9*1 + 3.9*(1+1)) / 4 * 100 = (1 + 2.9 + 7.8) / 4 * 100 = 11.7 / 4 * 100 = 292.5
        seq = "AVIL"
        ai = calculate_aliphatic_index(seq)
        assert pytest.approx(ai, 0.01) == 292.5

    def test_instability_index_formula(self):
        # Peptide with known stable dipeptides
        stable_seq = "AAAAA"
        ii = calculate_instability_index(stable_seq)
        assert ii < 40.0

    def test_hydrophobic_ratio_and_gravy(self):
        # AVIL = 100% hydrophobic
        seq = "AVIL"
        assert calculate_hydrophobic_ratio(seq) == 100.0
        # Kyte-Doolittle GRAVY: (A:1.8 + V:4.2 + I:4.5 + L:3.8) / 4 = 14.3 / 4 = 3.575
        assert pytest.approx(calculate_gravy(seq), 0.001) == 3.575

    def test_boman_index(self):
        # Arg (R: +14.92), Pro (P: 0.0) -> (14.92 + 0.0) / 2 = 7.46
        seq = "RP"
        bi = calculate_boman_index(seq)
        assert pytest.approx(bi, 0.01) == 7.46


# ==============================================================================
# 2. BENCHMARK POSITIVE CONTROLS (PRD.md Table 6)
# ==============================================================================

class TestPositiveControls:
    """
    Validates global reference antimicrobial peptides (AMPs).
    - Nisin A (Core): Gold standard food biopreservative -> 100% PASS on Tropical Preset.
    - Pediocin PA-1: Class IIa mesophilic bacteriocin -> 100% PASS on Permissive AMP Preset.
    - Lactoferricin B: High-charge mammalian AMP -> 100% PASS on Permissive AMP Preset.
    """

    def test_nisin_a_core_passes_tropical_filter(self):
        """Nisin A is the FDA/WHO-approved commercial biopreservative (E234)."""
        seq_nisin = "ITSISLCTPGCKTGALMGCNMKTATCHCSIHVSK"
        result = evaluate_peptide("Positive_Ctrl_Nisin_A", seq_nisin)

        assert result["passed_all_filters"] is True
        assert len(result["failed_reasons"]) == 0
        assert result["length"] == 34
        assert result["charge_ph6"] >= 2.0
        assert result["isoelectric_point"] >= 8.4
        assert result["aliphatic_index"] >= 60.0  # Nisin AI is ~71.76
        assert result["instability_index"] < 40.0   # Nisin II is ~27.52 (Stable)
        assert 28.0 <= result["hydrophobic_ratio"] <= 55.0
        assert 0.0 <= result["boman_index"] <= 2.5
        assert result["as35_score"] > 35.0
        assert result["thermostability_tier"] in ["Moderate (AI >= 60)", "Gold Standard (AI >= 80)"]

    def test_pediocin_pa1_passes_permissive_amp_preset(self):
        """Pediocin PA-1 is an active antilisterial bacteriocin from mesophilic Pediococcus."""
        seq_pediocin = "KYYGNGVTCGKHSCSVDWGKATTCIINNGAMAWATGGHQGNHKC"
        config_amp = FilterConfig.permissive_amp_preset()
        result = evaluate_peptide("Positive_Ctrl_Pediocin_PA1", seq_pediocin, config=config_amp)

        assert result["passed_all_filters"] is True
        assert len(result["failed_reasons"]) == 0
        assert result["charge_ph6"] >= 2.0
        assert result["isoelectric_point"] >= 8.0

    def test_lactoferricin_b_passes_permissive_amp_preset(self):
        """Lactoferricin B is a potent cationic antimicrobial peptide from bovine milk."""
        seq_lactoferricin = "FKCRRWQWRMKKLGAPSITCVRRAF"
        config_amp = FilterConfig.permissive_amp_preset()
        result = evaluate_peptide("Positive_Ctrl_Lactoferricin_B", seq_lactoferricin, config=config_amp)

        assert result["passed_all_filters"] is True
        assert len(result["failed_reasons"]) == 0
        assert result["charge_ph6"] >= +6.0  # Very high cationic charge (~+7.99)
        assert result["isoelectric_point"] >= 11.0


# ==============================================================================
# 3. BENCHMARK NEGATIVE CONTROLS (PRD.md Table 6)
# ==============================================================================

class TestNegativeControls:
    """
    Validates that non-AMP, toxic, or unstable sequences fail with clear audit trails.
    """

    def test_casein_cmp_fails_on_charge(self):
        """Casein Glycomacropeptide (CMP) fragment is non-cationic in neutral/mildly acidic food."""
        seq_casein = "MAIPPKKNQDKTEIPTINTI"
        result = evaluate_peptide("Negative_Ctrl_Casein_CMP", seq_casein)

        assert result["passed_all_filters"] is False
        assert len(result["failed_reasons"]) > 0
        # Expected failure: Net Charge @ pH 6.0 is only ~1.02 (< 2.0)
        assert any("Net Charge @ pH 6.0" in r for r in result["failed_reasons"])

    def test_melittin_fails_on_instability_and_toxicity(self):
        """Melittin (bee venom) is non-selective, hemolytic, and thermally fragile."""
        seq_melittin = "GIGAVLKVLTTGLPALISWIKRKRQQ"
        result = evaluate_peptide("Negative_Ctrl_Melittin", seq_melittin)

        assert result["passed_all_filters"] is False
        assert len(result["failed_reasons"]) > 0
        # Melittin has Instability Index ~44.73 (>= 40.0)
        assert any("Instability Index" in r for r in result["failed_reasons"])

    def test_unstable_poly_acidic_fails_comprehensively(self):
        """Artificially designed highly acidic & thermally labile peptide fragment."""
        seq_unstable = "PSDDPEEDDSEEP"
        result = evaluate_peptide("Negative_Ctrl_Unstable", seq_unstable)

        assert result["passed_all_filters"] is False
        # Fails net charge, pI, AI, II, and Hydrophobic ratio
        assert len(result["failed_reasons"]) >= 3
        reasons_text = " ".join(result["failed_reasons"])
        assert "Net Charge" in reasons_text
        assert "Aliphatic Index" in reasons_text
        assert "Instability Index" in reasons_text


# ==============================================================================
# 4. CONFIGURATION OVERRIDES & BATCH PROCESSING
# ==============================================================================

class TestConfigurationAndBatch:
    """Tests dynamic FilterConfig override and batch execution helper."""

    def test_custom_filter_config_stricter(self):
        seq = "ITSISLCTPGCKTGALMGCNMKTATCHCSIHVSK"
        # Stricter config requiring AI >= 90
        strict_config = FilterConfig(min_aliphatic_index=90.0)
        result = evaluate_peptide("Nisin_Strict", seq, config=strict_config)

        assert result["passed_all_filters"] is False
        assert any("Aliphatic Index too low" in r for r in result["failed_reasons"])

    def test_evaluate_peptide_batch(self):
        batch_input = [
            ("P1", "ITSISLCTPGCKTGALMGCNMKTATCHCSIHVSK"),
            ("P2", "MAIPPKKNQDKTEIPTINTI")
        ]
        results = evaluate_peptide_batch(batch_input)

        assert len(results) == 2
        assert results[0]["id"] == "P1"
        assert results[0]["passed_all_filters"] is True
        assert results[1]["id"] == "P2"
        assert results[1]["passed_all_filters"] is False
