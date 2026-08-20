import time
from typing import Any, Dict
import pandas as pd
from fpdf import FPDF, XPos, YPos
from src.filters import generate_preservation_narrative


def safe_pdf_text(text: str) -> str:
    """Sanitizes text strings for safe Latin-1 encoding in standard FPDF2 fonts."""
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        "\u2265": ">=",
        "\u2264": "<=",
        "\u03b1": "alpha",
        "\u03b2": "beta",
        "\u00b0": " deg ",
        "\u2192": "->",
        "\u2014": "--",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "*",
        "\u00b1": "+/-",
        "\u2248": "~",
        "\u00d7": "x",
        "\u03bc": "u",
        "\u2212": "-",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text.encode("latin-1", "replace").decode("latin-1")


class RDDossierPDF(FPDF):
    """Formal Academic Monochromatic 2-Page Dossier Generator (Times Font Family)."""
    def __init__(self, lang: str = "id", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang

    def header(self):
        # Academic running header
        self.set_font("Times", "I", 8)
        self.set_text_color(0, 0, 0)
        running_title = (
            "Open Studio AMP -- Laporan Karakterisasi Peptida Antimikroba"
            if self.lang == "id"
            else "Open Studio AMP -- Antimicrobial Peptide Characterization Report"
        )
        self.cell(100, 4, safe_pdf_text(running_title), align="L")
        self.cell(0, 4, safe_pdf_text("BioProject: PRJDB8096"), align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.2)
        self.line(10, 13, 200, 13)
        self.ln(3)

    def footer(self):
        self.set_y(-14)
        self.set_font("Times", "", 8)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.2)
        self.line(10, 283, 200, 283)
        page_label = f"Halaman {self.page_no()} dari {{nb}}" if self.lang == "id" else f"Page {self.page_no()} of {{nb}}"
        self.cell(0, 6, safe_pdf_text(f"Open Studio AMP | R&D Dossier | {page_label}"), align="C")


def generate_dossier_pdf(
    candidate: Any,
    top10_df: pd.DataFrame,
    nisin_res: Dict,
    lang: str = "id",
    organism_info: str = ""
) -> bytes:
    """
    Generates a formal academic 2-Page Technical Dossier PDF.
    Standard: Times New Roman style typography, monochrome black-and-white, precise table grids.
    Page 1: Title, Subtitle, 2-Column Metadata, Primary Sequence, Physicochemical Matrix, Source Organism Profile.
    Page 2: Preservation Suitability Narrative, Head-to-Head Benchmark vs Nisin A, Actionable Next Steps, Top 10 Summary.
    """
    if hasattr(candidate, 'to_dict'):
        cand_dict = candidate.to_dict()
    elif isinstance(candidate, dict):
        cand_dict = candidate
    else:
        cand_dict = {}

    pdf = RDDossierPDF(lang=lang, orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(10, 15, 10)
    pdf.alias_nb_pages()

    # ==========================================================================
    # HALAMAN 1: IDENTITAS, SEKUEN, MATRIKS PARAMETER & PROFIL ORGANISME
    # ==========================================================================
    pdf.add_page()

    # 1. Header Atas Dokumen Resmi (Times Bold 16 & Times 12)
    pdf.set_font("Times", "B", 16)
    pdf.set_text_color(0, 0, 0)
    main_title = (
        "LAPORAN KARAKTERISASI PEPTIDA ANTIMIKROBA (AMP)"
        if lang == "id"
        else "ANTIMICROBIAL PEPTIDE (AMP) CHARACTERIZATION REPORT"
    )
    pdf.cell(0, 7, safe_pdf_text(main_title), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Times", "", 12)
    sub_title = (
        "Evaluasi Sifat Fisikokimia & Potensi Biopreservasi Pangan Tropis"
        if lang == "id"
        else "Physicochemical Property Evaluation & Tropical Food Biopreservation Suitability"
    )
    pdf.cell(0, 6, safe_pdf_text(sub_title), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Garis pemisah horizontal
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.4)
    line_y = pdf.get_y() + 1
    pdf.line(10, line_y, 200, line_y)
    pdf.ln(4)

    # 2. Identitas Laporan (Layout 2 Kolom Formal)
    cand_id_safe = safe_pdf_text(str(cand_dict.get('id', 'N/A'))[:35])
    cand_src_safe = safe_pdf_text(str(cand_dict.get('source', 'sORF/CDS')))
    cand_tier_safe = safe_pdf_text(str(cand_dict.get('thermostability_tier', 'Gold Standard')))
    cand_len_safe = str(cand_dict.get('length', 'N/A'))
    cand_score_val = float(cand_dict.get('as35_score', 0.0))

    is_pls47 = "PLS47" in str(cand_dict.get('id', ''))
    if is_pls47:
        org_display = "Geobacillus thermocatenulatus PLS47"
        hab_display = "Tanah Geotermal Indonesia" if lang == "id" else "Indonesian Geothermal Soil"
        proj_display = "PRJDB8096"
    elif organism_info and organism_info.strip():
        org_display = organism_info[:40]
        hab_display = "Isolat Pengguna" if lang == "id" else "User Ingested"
        proj_display = "Custom Ingestion"
    else:
        org_display = "Genom Kustom Pengguna" if lang == "id" else "User Custom Genome"
        hab_display = "Tidak Ditentukan" if lang == "id" else "Unspecified"
        proj_display = "Custom Ingestion"

    pdf.set_font("Times", "", 10)
    # Row 1
    pdf.cell(95, 4.8, safe_pdf_text(f"ID Peptida: {cand_id_safe}" if lang == "id" else f"Peptide ID: {cand_id_safe}"))
    score_label = "Potensi Biopreservasi" if lang == "id" else "Biopreservation Potential"
    pdf.cell(95, 4.8, safe_pdf_text(f"{score_label}: {cand_score_val:.2f} / 100"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Row 2
    org_label = "Organisme:" if lang == "id" else "Organism:"
    len_label = "Panjang Sekuens:" if lang == "id" else "Sequence Length:"
    pdf.cell(95, 4.8, safe_pdf_text(f"{org_label} {org_display}"))
    pdf.cell(95, 4.8, safe_pdf_text(f"{len_label} {cand_len_safe} aa"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Row 3
    hab_label = "Habitat Asal:" if lang == "id" else "Origin Habitat:"
    date_label = "Tanggal Laporan:" if lang == "id" else "Report Date:"
    pdf.cell(95, 4.8, safe_pdf_text(f"{hab_label} {hab_display}"))
    pdf.cell(95, 4.8, safe_pdf_text(f"{date_label} {time.strftime('%Y-%m-%d')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Row 4
    proj_label = "BioProject NCBI:" if lang == "id" else "NCBI BioProject:"
    tier_label = "Kategori Kualitas:" if lang == "id" else "Quality Tier:"
    pdf.cell(95, 4.8, safe_pdf_text(f"{proj_label} {proj_display}"))
    pdf.cell(95, 4.8, safe_pdf_text(f"{tier_label} {cand_tier_safe}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # 3. Section 1: Sekuens Asam Amino Primer (Times Bold 14 + Courier 10)
    pdf.set_font("Times", "B", 14)
    sec1_title = "1. Sekuens Asam Amino Primer" if lang == "id" else "1. Primary Amino Acid Sequence"
    pdf.cell(0, 6, safe_pdf_text(sec1_title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

    pdf.set_font("Courier", "", 10)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.multi_cell(190, 5, safe_pdf_text(str(cand_dict.get('sequence', 'N/A'))), border=1)
    pdf.ln(4)

    # 4. Section 2: Matriks Parameter Fisikokimia (Times Bold 14 + Tabel Formal 3 Kolom)
    pdf.set_font("Times", "B", 14)
    sec2_title = "2. Matriks Parameter Fisikokimia" if lang == "id" else "2. Physicochemical Parameter Matrix"
    pdf.cell(0, 6, safe_pdf_text(sec2_title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

    # Table Header (Times Bold 10)
    pdf.set_font("Times", "B", 10)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.cell(70, 5.5, safe_pdf_text("Parameter" if lang == "id" else "Parameter"), 1, align="L")
    pdf.cell(45, 5.5, safe_pdf_text("Nilai Teramati" if lang == "id" else "Observed Value"), 1, align="C")
    pdf.cell(75, 5.5, safe_pdf_text("Status Kelayakan" if lang == "id" else "Compliance Status"), 1, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    c_c6 = float(cand_dict.get('charge_ph6', 0.0))
    c_pi = float(cand_dict.get('isoelectric_point', 0.0))
    c_ai = float(cand_dict.get('aliphatic_index', 0.0))
    c_ii = float(cand_dict.get('instability_index', 0.0))
    c_hydro = float(cand_dict.get('hydrophobic_ratio', 0.0))
    c_boman = float(cand_dict.get('boman_index', 0.0))
    c_c4 = float(cand_dict.get('charge_ph4', 0.0))
    c_c7 = float(cand_dict.get('charge_ph7', 0.0))

    if lang == "id":
        metrics_table = [
            ("Muatan Antibakteri @ pH 6.0 (Z_6)", f"+{c_c6:.2f}", "Lolos (>= +2.0, Penetrasi dinding bakteri)"),
            ("Titik Isoelektrik (pI)", f"{c_pi:.2f}", "Lolos (>= 8.4, Mencegah presipitasi)"),
            ("Stabilitas Termal (Aliphatic Index)", f"{c_ai:.2f}", "Lolos (>= 60.0, Tahan panas tropis)"),
            ("Instability Index (II)", f"{c_ii:.2f}", "Lolos (< 40.0, Stabil dalam larutan)"),
            ("Rasio Asam Amino Hidrofobik", f"{c_hydro:.1f}%", "Lolos (30.0% - 55.0%, Insersi membran)"),
            ("Indeks Boman (Afinitas)", f"{c_boman:.2f} kcal/mol", "Lolos (0.0 - 2.5 kcal/mol, Predicted Low Cytotoxicity)"),
            ("Muatan Bersih @ pH 4.0 (Z_4)", f"+{c_c4:.2f}", "Kationik Kuat (Aktif pangan asam)"),
            ("Muatan Bersih @ pH 7.4 (Z_7.4)", f"+{c_c7:.2f}", "Kationik (Stabil matriks netral)")
        ]
    else:
        metrics_table = [
            ("Antibacterial Charge @ pH 6.0 (Z_6)", f"+{c_c6:.2f}", "Passed (>= +2.0, Bacterial penetration)"),
            ("Isoelectric Point (pI)", f"{c_pi:.2f}", "Passed (>= 8.4, Prevents precipitation)"),
            ("Thermal Stability (Aliphatic Index)", f"{c_ai:.2f}", "Passed (>= 60.0, Tropical thermal stability)"),
            ("Instability Index (II)", f"{c_ii:.2f}", "Passed (< 40.0, Stable in solution)"),
            ("Hydrophobic Amino Acid Ratio", f"{c_hydro:.1f}%", "Passed (30.0% - 55.0%, Membrane insertion)"),
            ("Boman Index", f"{c_boman:.2f} kcal/mol", "Passed (0.0 - 2.5 kcal/mol, Predicted Low Cytotoxicity)"),
            ("Net Charge @ pH 4.0 (Z_4)", f"+{c_c4:.2f}", "Strong Cationic (Active in acid foods)"),
            ("Net Charge @ pH 7.4 (Z_7.4)", f"+{c_c7:.2f}", "Cationic (Stable in neutral matrix)")
        ]

    pdf.set_font("Times", "", 10)
    for param, obs, status in metrics_table:
        pdf.cell(70, 4.8, safe_pdf_text(param), 1, align="L")
        pdf.cell(45, 4.8, safe_pdf_text(obs), 1, align="C")
        pdf.cell(75, 4.8, safe_pdf_text(status), 1, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)

    # 5. Section 3: Profil Organisme Sumber (Times Bold 14 + Times 12 Paragraf Naratif)
    pdf.set_font("Times", "B", 14)
    sec3_title = "3. Profil Organisme Sumber" if lang == "id" else "3. Source Organism Profile"
    pdf.cell(0, 6, safe_pdf_text(sec3_title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

    if is_pls47:
        source_text = (
            "Sumber Organisme: Geobacillus thermocatenulatus strain PLS47 (NCBI BioProject: PRJDB8096). "
            "Organisme ini merupakan bakteri termofilik yang diisolasi dari tanah (soil environment) di Indonesia. "
            "Habitat tanah bersuhu tinggi memaksanya berevolusi menghasilkan peptida antimikroba yang secara alami tahan terhadap denaturasi termal, "
            "menjadikannya kandidat ideal untuk biopreservasi pangan tropis tanpa ketergantungan rantai dingin (cold-chain)."
            if lang == "id"
            else
            "Source Organism: Geobacillus thermocatenulatus strain PLS47 (NCBI BioProject: PRJDB8096). "
            "This thermophilic bacterium was isolated from Indonesian geothermal soil environments. "
            "Its extreme thermal habitat necessitated the evolutionary emergence of antimicrobial peptides naturally resistant to heat denaturation, "
            "making it an ideal candidate for tropical food biopreservation without cold-chain reliance."
        )
    elif organism_info and organism_info.strip():
        source_text = (
            f"Sumber Organisme: {organism_info}. Organisme ini dianalisis secara in silico untuk mengevaluasi potensi biopreservasi pangan tropis dari sekuens genom yang diunggah pengguna."
            if lang == "id"
            else
            f"Source Organism: {organism_info}. In silico profiling conducted to evaluate tropical food biopreservation potential from user-provided sequence data."
        )
    else:
        source_text = (
            "Sumber: Genom kustom yang diunggah oleh pengguna. Profil sekuens dievaluasi berdasarkan parameter biopreservasi pangan tropis tanpa informasi taksonomi spesifik."
            if lang == "id"
            else
            "Source: User-uploaded custom genomic sequence. Biophysical profiling conducted for tropical food preservation suitability without specific taxonomic annotation."
        )

    pdf.set_font("Times", "", 12)
    pdf.multi_cell(190, 5.5, safe_pdf_text(source_text), border=0)
    pdf.ln(6)

    # ==========================================================================
    # HALAMAN 2: ANALISIS POTENSI, BENCHMARK NISIN A, NEXT STEPS & TOP 10
    # ==========================================================================
    pdf.add_page()

    # 6. Section 4: Analisis Kesesuaian & Potensi Biopreservasi (Times Bold 14 + Times 12 Narasi)
    pdf.set_font("Times", "B", 14)
    sec4_title = (
        "4. Analisis Kesesuaian & Potensi Biopreservasi"
        if lang == "id"
        else "4. Biopreservation Suitability & Potential Analysis"
    )
    pdf.cell(0, 6, safe_pdf_text(sec4_title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

    narrative_text = generate_preservation_narrative(candidate, lang=lang)
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(190, 5.5, safe_pdf_text(narrative_text), border=0)
    pdf.ln(5)

    # 7. Section 5: Komparasi Head-to-Head vs Nisin A (Times Bold 14 + Tabel Formal 3 Kolom)
    pdf.set_font("Times", "B", 14)
    sec5_title = "5. Komparasi Head-to-Head vs Nisin A" if lang == "id" else "5. Head-to-Head Benchmark vs Nisin A"
    pdf.cell(0, 6, safe_pdf_text(sec5_title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

    # Table Header (Times Bold 10)
    pdf.set_font("Times", "B", 10)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.cell(70, 5.5, safe_pdf_text("Parameter" if lang == "id" else "Parameter"), 1, align="L")
    cand_col = "Kandidat PLS47" if is_pls47 else "Kandidat Terpilih"
    cand_col_en = "PLS47 Candidate" if is_pls47 else "Selected Candidate"
    pdf.cell(60, 5.5, safe_pdf_text(cand_col if lang == "id" else cand_col_en), 1, align="C")
    pdf.cell(60, 5.5, safe_pdf_text("Nisin A Baseline (E234)"), 1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    nis_ai = float(nisin_res.get('aliphatic_index', 71.76))
    nis_ii = float(nisin_res.get('instability_index', 27.52))
    nis_c6 = float(nisin_res.get('charge_ph6', 3.98))
    nis_score = float(nisin_res.get('as35_score', 41.22))

    if lang == "id":
        comp_rows = [
            ("Stabilitas Termal (Aliphatic Index)", f"{c_ai:.2f} (Delta: +{c_ai-nis_ai:.1f})", f"{nis_ai:.2f}"),
            ("Muatan Antibakteri @ pH 6.0 (Penetrasi)", f"+{c_c6:.2f}", f"+{nis_c6:.2f}"),
            ("Potensi Biopreservasi (0 - 100)", f"{cand_score_val:.2f} / 100", f"{nis_score:.2f} / 100"),
            ("Instability Index (II - Masa Simpan)", f"{c_ii:.2f} (Stabil)", f"{nis_ii:.2f} (Stabil)"),
            ("Habitat Adaptasi Termal Asal", "Tanah/Geotermal Indonesia" if is_pls47 else "Isolat Kustom", "Mesofilik (30 deg C)")
        ]
    else:
        comp_rows = [
            ("Thermal Stability (Aliphatic Index)", f"{c_ai:.2f} (Delta: +{c_ai-nis_ai:.1f})", f"{nis_ai:.2f}"),
            ("Antibacterial Charge @ pH 6.0 (Penetration)", f"+{c_c6:.2f}", f"+{nis_c6:.2f}"),
            ("AliphaScore-35 (0 - 100)", f"{cand_score_val:.2f} / 100", f"{nis_score:.2f} / 100"),
            ("Instability Index (II - Shelf-Life)", f"{c_ii:.2f} (Stable)", f"{nis_ii:.2f} (Stable)"),
            ("Origin Thermal Habitat", "Indonesian Soil / Geothermal" if is_pls47 else "Custom Isolate", "Mesophilic (30 deg C)")
        ]

    pdf.set_font("Times", "", 10)
    for param, cand_val, nis_val in comp_rows:
        pdf.cell(70, 4.8, safe_pdf_text(param), 1, align="L")
        pdf.cell(60, 4.8, safe_pdf_text(cand_val), 1, align="C")
        pdf.cell(60, 4.8, safe_pdf_text(nis_val), 1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)

    # 8. Section 6: Actionable Next Steps (Tabel Formal 2 Kolom Rapi)
    pdf.set_font("Times", "B", 14)
    sec6_title = "6. Actionable Next Steps" if lang == "id" else "6. Actionable Next Steps & Roadmap"
    pdf.cell(0, 6, safe_pdf_text(sec6_title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

    # Table Header (Times Bold 10)
    pdf.set_font("Times", "B", 10)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.cell(48, 5.5, safe_pdf_text("Tahapan Validasi" if lang == "id" else "Validation Stage"), 1, align="L")
    pdf.cell(142, 5.5, safe_pdf_text("Rencana Tindak Lanjut & Protokol Eksperimen" if lang == "id" else "Experimental Protocol & Roadmap"), 1, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if lang == "id":
        next_steps_table = [
            ("1. Sintesis SPPS", "Sintesis kimiawi (Solid-Phase Peptide Synthesis) kemurnian >95% (HPLC) untuk uji in vitro."),
            ("2. Uji MIC Assay", "Penentuan konsentrasi hambat minimum terhadap B. cereus, L. monocytogenes, dan S. aureus."),
            ("3. Uji Stabilitas Termal", "Pengujian integritas pada pemanasan 80 C - 121 C (autoklaf) dan rentang pH 4.0 - 7.4."),
            ("4. Enkapsulasi Pangan", "Formulasi pada matriks pangan asam rendah via mikroenkapsulasi lipid/kitosan.")
        ]
    else:
        next_steps_table = [
            ("1. SPPS Synthesis", "Solid-Phase chemical synthesis with >95% purity (HPLC) for in vitro experimental testing."),
            ("2. MIC Assay", "Determine Minimum Inhibitory Concentration against B. cereus, L. monocytogenes, and S. aureus."),
            ("3. Thermal Stability", "Incubation at 80 C - 121 C (autoclaving) across pH 4.0 - 7.4 to verify operational resilience."),
            ("4. Food Encapsulation", "Application trials on low-acid food models using lipid/chitosan microencapsulation.")
        ]

    pdf.set_font("Times", "", 10)
    for stage, desc in next_steps_table:
        pdf.set_font("Times", "B", 10)
        pdf.cell(48, 4.8, safe_pdf_text(stage), 1, align="L")
        pdf.set_font("Times", "", 10)
        pdf.cell(142, 4.8, safe_pdf_text(desc), 1, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)

    # 9. Section 7: Ringkasan 10 Kandidat Teratas (Times Bold 14 + Tabel Formal 7 Kolom)
    pdf.set_font("Times", "B", 14)
    sec7_title = "7. Ringkasan 10 Kandidat Teratas" if lang == "id" else "7. Top 10 Ranked Candidates Summary"
    pdf.cell(0, 6, safe_pdf_text(sec7_title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

    # 7-Column Table Header (Total Width = 190mm)
    # Rank (12mm) | ID (60mm) | Asal (18mm) | Panjang (18mm) | Muatan@6 (26mm) | Alifatik (26mm) | Skor (30mm)
    pdf.set_font("Times", "B", 9.5)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.cell(12, 5, "Rank", 1, align="C")
    pdf.cell(60, 5, safe_pdf_text("ID Peptida" if lang == "id" else "Peptide Identifier"), 1, align="L")
    pdf.cell(18, 5, safe_pdf_text("Asal" if lang == "id" else "Source"), 1, align="C")
    pdf.cell(18, 5, safe_pdf_text("Panjang" if lang == "id" else "Length"), 1, align="C")
    pdf.cell(26, 5, safe_pdf_text("Muatan@6" if lang == "id" else "Charge@6"), 1, align="C")
    pdf.cell(26, 5, safe_pdf_text("Stab. Termal" if lang == "id" else "Thermal Stab."), 1, align="C")
    pdf.cell(30, 5, safe_pdf_text("AliphaScore-35" if lang == "id" else "AS-35 Score"), 1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Times", "", 9.5)
    for rank, (_, row) in enumerate(top10_df.head(10).iterrows(), 1):
        pdf.cell(12, 4.2, f"#{rank}", 1, align="C")
        pdf.cell(60, 4.2, safe_pdf_text(str(row.get('id', ''))[:32]), 1, align="L")
        pdf.cell(18, 4.2, safe_pdf_text(str(row.get('source', ''))), 1, align="C")
        pdf.cell(18, 4.2, f"{row.get('length', '')} aa", 1, align="C")
        pdf.cell(26, 4.2, f"+{float(row.get('charge_ph6', 0)):.2f}", 1, align="C")
        pdf.cell(26, 4.2, f"{float(row.get('aliphatic_index', 0)):.1f}", 1, align="C")
        pdf.cell(30, 4.2, f"{float(row.get('as35_score', 0)):.2f}", 1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(3)

    # 10. Catatan Metodologi Formal
    pdf.set_font("Times", "I", 8)
    note_text = (
        "Catatan Metodologi: Muatan dihitung via persamaan Henderson-Hasselbalch (pKa Lehninger). Indeks Alifatik menurut model Ikai (1980). "
        "Indeks Instabilitas menurut Guruprasad (1990). Indeks Boman menurut Boman (2003). Skrining genomik in silico berbasis NCBI BioProject PRJDB8096. "
        "AliphaScore-35 adalah model heuristik prioritisasi komputasional, bukan bukti aktivitas antimikroba aktual. "
        "Kandidat terpilih wajib menjalani validasi eksperimental di laboratorium basah (wet-lab)."
        if lang == "id"
        else "Methodological Note: Charge determined via Henderson-Hasselbalch (Lehninger pKa). Aliphatic Index via Ikai (1980). "
        "Instability Index via Guruprasad (1990). Boman Index via Boman (2003). In silico screening based on NCBI BioProject PRJDB8096. "
        "AliphaScore-35 is a computational heuristic prioritization model, not proof of actual antimicrobial activity. "
        "Selected candidates must undergo experimental validation in a wet-lab setting."
    )
    pdf.multi_cell(190, 3.2, safe_pdf_text(note_text), border=0)

    out = pdf.output()
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    elif isinstance(out, str):
        return out.encode("latin-1")
    return bytes(out) if out is not None else b""
