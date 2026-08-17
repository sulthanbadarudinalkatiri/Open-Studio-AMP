"""
Unit Tests for Modular Architecture Decoupling (reporter, structure, theme)
Module: tests/test_modular_architecture.py
"""

import pytest
import pandas as pd
from src.reporter import generate_dossier_pdf, safe_pdf_text
from src.structure import generate_ideal_alpha_helix_pdb, fetch_peptide_3d_pdb, build_3dmol_html
from src.theme import DESIGN_TOKENS, I18N, render_kpi_card, get_base_chart_layout
from src.filters import generate_preservation_narrative


class TestReporterModuleDecoupling:
    def test_safe_pdf_text_unicode_replacements(self):
        raw = "Temperature \u2265 60\u00b0C \u2014 \u03b1-helix"
        safe = safe_pdf_text(raw)
        assert ">=" in safe
        assert "deg" in safe
        assert "alpha" in safe
        assert "--" in safe

    def test_generate_preservation_narrative_id(self):
        cand = {
            "aliphatic_index": 85.0,
            "charge_ph6": 3.5,
            "instability_index": 22.0,
            "boman_index": 1.2,
            "hydrophobic_ratio": 42.0,
            "as35_score": 88.5,
            "length": 50
        }
        narrative = generate_preservation_narrative(cand, lang="id")
        assert "Aliphatic Index" in narrative
        assert "85.0" in narrative
        assert "Bacillus cereus" in narrative
        assert "AliphaScore-35" in narrative

    def test_generate_preservation_narrative_en(self):
        cand = {
            "aliphatic_index": 85.0,
            "charge_ph6": 3.5,
            "instability_index": 22.0,
            "boman_index": 1.2,
            "hydrophobic_ratio": 42.0,
            "as35_score": 88.5,
            "length": 50
        }
        narrative = generate_preservation_narrative(cand, lang="en")
        assert "Aliphatic Index" in narrative
        assert "pasteurization" in narrative
        assert "AliphaScore-35" in narrative

    def test_generate_dossier_pdf_pls47_auto_detection(self):
        candidate = {
            "id": "PLS47_sORF_0001",
            "sequence": "MGGERVTIQNLKIVKVDPERNLLLIKGNVPGPRKGLVIVKSAVKAAKKAK",
            "source": "sORF",
            "length": 50,
            "charge_ph6": 4.5,
            "isoelectric_point": 10.2,
            "aliphatic_index": 85.0,
            "instability_index": 22.0,
            "hydrophobic_ratio": 42.0,
            "boman_index": 1.2,
            "as35_score": 88.5,
            "thermostability_tier": "Gold Standard"
        }
        top10_df = pd.DataFrame([candidate])
        nisin_res = {
            "aliphatic_index": 71.76,
            "instability_index": 27.52,
            "charge_ph6": 3.98,
            "as35_score": 41.22
        }
        pdf_bytes = generate_dossier_pdf(candidate, top10_df, nisin_res, lang="id")
        assert isinstance(pdf_bytes, (bytes, bytearray))
        assert len(pdf_bytes) > 2000
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_dossier_pdf_with_custom_organism(self):
        candidate = {
            "id": "Custom_Peptide_001",
            "sequence": "MGGERVTIQNLKIVKVDPERNLLLIKGNVPGPRKGLVIVKSAVKAAKKAK",
            "source": "CDS",
            "length": 50,
            "charge_ph6": 4.5,
            "isoelectric_point": 10.2,
            "aliphatic_index": 85.0,
            "instability_index": 22.0,
            "hydrophobic_ratio": 42.0,
            "boman_index": 1.2,
            "as35_score": 88.5,
            "thermostability_tier": "Gold Standard"
        }
        top10_df = pd.DataFrame([candidate])
        nisin_res = {
            "aliphatic_index": 71.76,
            "instability_index": 27.52,
            "charge_ph6": 3.98,
            "as35_score": 41.22
        }
        pdf_bytes = generate_dossier_pdf(
            candidate,
            top10_df,
            nisin_res,
            lang="id",
            organism_info="Lactobacillus plantarum (Habitat: Susu fermentasi)"
        )
        assert isinstance(pdf_bytes, (bytes, bytearray))
        assert len(pdf_bytes) > 2000
        assert pdf_bytes.startswith(b"%PDF")


class TestStructureModuleDecoupling:
    def test_generate_ideal_alpha_helix_pdb(self):
        seq = "MGGERVTIQNLKIV"
        pdb_str = generate_ideal_alpha_helix_pdb(seq)
        assert "HEADER" in pdb_str
        assert "ATOM" in pdb_str
        assert "END" in pdb_str
        assert pdb_str.count("ATOM") == len(seq) * 4

    def test_fetch_peptide_3d_pdb_fallback(self):
        seq = "LFIHLHRLIPNELK"
        pdb_str, source = fetch_peptide_3d_pdb(seq, timeout_sec=1)
        assert len(pdb_str) > 0
        assert "ATOM" in pdb_str
        assert ("ESMFold" in source) or ("Alpha-Helix" in source)

    def test_build_3dmol_html(self):
        seq = "MGGERVTIQNLKIV"
        pdb_str = generate_ideal_alpha_helix_pdb(seq)
        html_code = build_3dmol_html(pdb_str, height=350)
        assert "3Dmol.org" in html_code
        assert "container-3d" in html_code
        assert "viewer.render()" in html_code


class TestThemeModuleDecoupling:
    def test_design_tokens_structure(self):
        assert "colors" in DESIGN_TOKENS
        assert "primary" in DESIGN_TOKENS["colors"]
        assert "radius" in DESIGN_TOKENS
        assert "shadows" in DESIGN_TOKENS

    def test_i18n_keys_parity(self):
        id_keys = set(I18N["id"].keys())
        en_keys = set(I18N["en"].keys())
        assert id_keys == en_keys

    def test_render_kpi_card_html(self):
        card_html = render_kpi_card("Total Diskrining", "241,409", "CDS & sORF")
        assert "kpi-card" in card_html
        assert "Total Diskrining" in card_html
        assert "241,409" in card_html

    def test_get_base_chart_layout(self):
        layout = get_base_chart_layout(height=400)
        assert layout["height"] == 400
        assert "plot_bgcolor" in layout
        assert "xaxis" in layout
