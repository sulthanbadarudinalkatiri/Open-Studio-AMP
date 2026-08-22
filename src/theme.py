import html
from typing import Any, Dict, Optional

# ==============================================================================
# 1. CENTRALIZED DESIGN TOKENS
# ==============================================================================

DESIGN_TOKENS: Dict[str, Any] = {
    "colors": {
        # Brand & Hydrothermal Identity
        "abyss_950": "#070E1A",             # Deepest Oceanic Abyss
        "abyss_900": "#0A192F",             # Oceanic Header Base
        "abyss_800": "#172A45",             # Deep Blue-Teal Horizon
        "primary": "#0E8388",               # Clinical Tosca (Primary Brand)
        "primary_rgb": (14, 131, 136),      # FPDF RGB
        "primary_dark": "#2E4F4F",          # Deep Forest Teal
        "primary_dark_rgb": (46, 79, 79),
        "accent": "#00ABB3",                # Bioluminescent Cyan
        "accent_rgb": (0, 171, 179),
        "accent_light": "#38E54D",          # Bio-active Green
        "accent_glow": "rgba(0, 171, 179, 0.25)",

        # Semantics & Diagnostics
        "danger": "#EF4444",                # Inactive / Elimination / Baseline
        "danger_rgb": (239, 68, 68),
        "danger_glow": "rgba(239, 68, 68, 0.2)",
        "warning": "#F59E0B",               # Acid Food Matrix Indicator / Intermediate
        "warning_rgb": (245, 158, 11),
        "amber": "#F59E0B",                 # Hydrophobic 3D Residues
        "amber_rgb": (245, 158, 11),
        "success": "#0D9488",               # Qualified Food Biopreservative
        "success_rgb": (13, 148, 136),

        # Neutrals, Glass & Surfaces
        "white": "#FFFFFF",
        "white_rgb": (255, 255, 255),
        "glass_bg": "rgba(255, 255, 255, 0.88)",
        "glass_border": "rgba(203, 213, 225, 0.65)",
        "glass_hover_border": "rgba(14, 131, 136, 0.5)",
        "neutral_50": "#F8FAFC",            # Canvas Background
        "neutral_50_rgb": (248, 250, 252),
        "neutral_100": "#F1F5F9",           # Surface / Chart Grid
        "neutral_100_rgb": (241, 245, 249),
        "neutral_200": "#CBD5E1",           # Standard Borders
        "neutral_200_rgb": (203, 213, 225),
        "neutral_400": "#94A3B8",           # Subtitle / Muted
        "neutral_400_rgb": (148, 163, 184),
        "neutral_500": "#64748B",           # Captions / Secondary
        "neutral_500_rgb": (100, 116, 139),
        "neutral_700": "#334155",           # Body High-Density
        "neutral_700_rgb": (51, 65, 85),
        "neutral_900": "#0F172A",           # High-Contrast Headings
        "neutral_900_rgb": (15, 23, 42),
    },
    "radius": {
        "sm": "8px",                        # Badges, sequence boxes, inputs
        "md": "12px",                       # Cards, charts, 3D viewers
        "lg": "18px",                       # Main hero container
    },
    "shadows": {
        "elevation_1": "0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02)",
        "elevation_2": "0 8px 24px -4px rgba(14, 131, 136, 0.10), 0 2px 6px -1px rgba(0, 0, 0, 0.03)",
        "elevation_hover": "0 18px 36px -6px rgba(14, 131, 136, 0.22), 0 6px 12px -2px rgba(0, 0, 0, 0.05)",
        "hero_glow": "0 12px 36px -4px rgba(10, 25, 47, 0.35), 0 4px 14px 0 rgba(14, 131, 136, 0.25)",
    },
    "typography": {
        "font_family": "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "mono_family": "'JetBrains Mono', 'Fira Code', Menlo, monospace",
    }
}

C = DESIGN_TOKENS["colors"]
R = DESIGN_TOKENS["radius"]
S = DESIGN_TOKENS["shadows"]
TYPO = DESIGN_TOKENS["typography"]

# ==============================================================================
# 2. CUSTOM CSS STYLESHEET
# ==============================================================================

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {{
        --color-primary: {C["primary"]};
        --color-primary-dark: {C["primary_dark"]};
        --color-accent: {C["accent"]};
        --color-danger: {C["danger"]};
        --color-neutral-50: {C["neutral_50"]};
        --color-neutral-100: {C["neutral_100"]};
        --color-neutral-200: {C["neutral_200"]};
        --color-neutral-500: {C["neutral_500"]};
        --color-neutral-900: {C["neutral_900"]};
        --radius-sm: {R["sm"]};
        --radius-md: {R["md"]};
        --radius-lg: {R["lg"]};
        --font-sans: {TYPO["font_family"]};
        --font-mono: {TYPO["mono_family"]};
    }}

    /* Global Spatial Canvas */
    .stApp {{
        background: radial-gradient(at 0% 0%, rgba(14, 131, 136, 0.04) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(0, 171, 179, 0.04) 0px, transparent 50%),
                    #F8FAFC;
        font-family: var(--font-sans);
        color: var(--color-neutral-900);
    }}

    /* Hero Banner: Deep Abyss & Bioluminescent Spatial Depth */
    .main-header {{
        background: linear-gradient(135deg, {C["abyss_900"]} 0%, {C["abyss_800"]} 45%, {C["primary"]} 100%);
        padding: 24px 32px;
        border-radius: var(--radius-lg);
        color: #FFFFFF;
        margin-bottom: 20px;
        box-shadow: {S["hero_glow"]};
        border: 1px solid rgba(255, 255, 255, 0.12);
        position: relative;
        overflow: hidden;
    }}
    .main-header::after {{
        content: "";
        position: absolute;
        top: -50%;
        right: -20%;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(0, 171, 179, 0.25) 0%, transparent 70%);
        pointer-events: none;
    }}
    .main-header h1 {{
        font-size: 24px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }}
    .main-header p {{
        font-size: 13px;
        opacity: 0.94;
        margin: 6px 0 0 0;
        font-weight: 400;
        line-height: 1.5;
        max-width: 95%;
        color: #E2E8F0;
    }}
    .header-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 10.5px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 8px;
        color: {C["accent"]};
    }}

    /* Weightless KPI Cards (Glassmorphism + Elevation) */
    .kpi-card {{
        background: {C["glass_bg"]};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid {C["glass_border"]};
        border-left: 4px solid var(--color-primary);
        border-radius: var(--radius-md);
        padding: 16px 20px;
        box-shadow: {S["elevation_2"]};
        margin-bottom: 12px;
        transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), 
                    box-shadow 0.28s ease, 
                    border-color 0.28s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: {S["elevation_hover"]};
        border-color: {C["glass_hover_border"]};
    }}
    .kpi-title {{
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--color-neutral-500);
    }}
    .kpi-value {{
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: var(--color-primary);
        margin-top: 2px;
        line-height: 1.15;
    }}
    .kpi-sub {{
        font-size: 11px;
        color: var(--color-neutral-500);
        margin-top: 3px;
        font-weight: 500;
    }}

    /* Sequence Monospace Terminal Box */
    .seq-box {{
        font-family: var(--font-mono);
        background: #FFFFFF;
        border: 1px solid {C["neutral_200"]};
        padding: 12px 16px;
        border-radius: var(--radius-sm);
        font-size: 12.5px;
        word-break: break-all;
        color: var(--color-neutral-900);
        box-shadow: {S["elevation_1"]};
        line-height: 1.6;
        letter-spacing: 0.02em;
    }}

    /* Swiss Precision Summary Box */
    .summary-card {{
        background: {C["glass_bg"]};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid {C["glass_border"]};
        border-radius: var(--radius-sm);
        padding: 14px 16px;
        margin-top: 10px;
        font-size: 12.5px;
        line-height: 1.6;
        color: var(--color-neutral-900);
        box-shadow: {S["elevation_1"]};
    }}

    /* Modern Tabs & Button Accents */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
        padding-bottom: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: var(--radius-sm);
        padding: 8px 18px;
        font-weight: 600;
        font-size: 13.5px;
        color: {C["neutral_700"]};
        transition: all 0.2s ease;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {C["white"]};
        box-shadow: {S["elevation_1"]};
        color: {C["primary"]};
    }}
</style>
"""

# ==============================================================================
# 3. COMPONENT HELPERS
# ==============================================================================

def render_kpi_card(title: str, value: Any, sub: str, is_alert: bool = False) -> str:
    """Renders an accessible, weightless glassmorphic KPI card with ARIA roles."""
    safe_title = html.escape(str(title))
    safe_value = html.escape(str(value))
    safe_sub = html.escape(str(sub))

    border_color = C["danger"] if is_alert else C["primary"]
    val_color = C["danger"] if is_alert else C["primary"]

    return f"""
    <div class="kpi-card" style="border-left-color: {border_color};" role="region" aria-label="{safe_title}">
        <div class="kpi-title">{safe_title}</div>
        <div class="kpi-value" style="color: {val_color};">{safe_value}</div>
        <div class="kpi-sub">{safe_sub}</div>
    </div>
    """


def get_base_chart_layout(height: int = 420, margin: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """Centralized Plotly layout generator maintaining Antigravity SSoT design tokens."""
    return dict(
        height=height,
        margin=margin or dict(l=10, r=10, t=25, b=10),
        plot_bgcolor=C["white"],
        paper_bgcolor=C["white"],
        font=dict(family=TYPO["font_family"], color=C["neutral_900"], size=12),
        xaxis=dict(
            gridcolor=C["neutral_100"],
            zeroline=False,
            tickfont=dict(family=TYPO["font_family"], color=C["neutral_500"], size=11),
            title_font=dict(family=TYPO["font_family"], color=C["neutral_900"], size=12)
        ),
        yaxis=dict(
            gridcolor=C["neutral_100"],
            zeroline=False,
            tickfont=dict(family=TYPO["font_family"], color=C["neutral_500"], size=11),
            title_font=dict(family=TYPO["font_family"], color=C["neutral_900"], size=12)
        )
    )

# ==============================================================================
# 4. TOSS-INSPIRED BILINGUAL UX MICROCOPY (INDONESIAN & ENGLISH)
# ==============================================================================

I18N: Dict[str, Dict[str, str]] = {
    "id": {
        "app_title": "Open Studio AMP · Penambangan Peptida Preservasi Pangan",
        "app_sub": "Eksplorasi kandidat peptida antimikroba (AMP) tahan panas untuk perlindungan pangan alami tanpa ketergantungan rantai dingin. Mendukung dataset acuan tanah Indonesia (G. thermocatenulatus PLS47) maupun genom kustom laboratorium Anda.",
        "badge_env": "SUMBER ISOLAT ACUAN: TANAH GEOTERMAL INDONESIA (NCBI: PRJDB8096)",
        
        # Sidebar Structure
        "sidebar_title": "Open Studio AMP",
        "sidebar_sub": "**Penambangan Peptida Antimikroba**",
        "sidebar_sub_default": "🌿 *Dataset Acuan: G. thermocatenulatus PLS47*",
        "sidebar_sub_custom": "📂 *Dataset Aktif: {name}*",
        "sidebar_methodology_note": "<b>Catatan Metodologis:</b> AliphaScore-35 adalah model heuristik prioritisasi komputasional, bukan bukti aktivitas antimikroba aktual. Kandidat terpilih wajib menjalani validasi eksperimental di laboratorium basah (wet-lab).",
        "sidebar_lang": "🌐 Pilihan Bahasa / Language:",
        "src_selector_title": "Pilih Sumber Data Sekuens:",
        "src_default_label": "🔬 Dataset Acuan (PLS47 Tanah Indonesia - 241k Sekuens)",
        "src_custom_label": "📂 Unggah / Paste Genom Sendiri (.faa / .fna / .fasta)",
        "upload_tab_file": "📁 Unggah Berkas FASTA",
        "upload_tab_paste": "✍️ Tempel Sekuens Manual",
        "uploader_label": "Pilih berkas sekuens (.faa, .fna, .fasta, .txt) bisa lebih dari satu:",
        "paste_label": "Tempel sekuens FASTA di sini (Contoh: >ID\nSEKUENS):",
        "custom_success": "✅ Berhasil memproses {n} kandidat peptida dari {name}.",
        "upload_too_large": "⚠️ File {name} berukuran lebih dari 10 MB ({size:.1f} MB) dan akan dilewati untuk menjaga performa.",
        "custom_empty": "⚠️ Tidak ditemukan sekuens valid. Menampilkan dataset acuan PLS47.",
        "spinner_db": "Membangun database dari genom G. thermocatenulatus PLS47...",
        "spinner_process": "Memproses sekuens...",
        "custom_data_name": "Data Kustom",
        "info_upload_paste": "💡 Unggah .faa/.fna atau paste sekuens di atas.",
        "input_org_name": "Nama Organisme Sumber (untuk PDF):",
        "input_org_ph": "Contoh: Lactobacillus plantarum",
        "input_env_name": "Asal Lingkungan/Habitat (opsional):",
        "input_env_ph": "Contoh: Susu fermentasi",

        # Candidate Selector Toolbar
        "target_header": "Pilih Peptida untuk Dianalisis",
        "sort_label": "Urutkan Daftar Kandidat Berdasarkan:",
        "sort_opt_score": "🏆 Potensi Biopreservasi Tertinggi (AliphaScore-35)",
        "sort_opt_ai": "🔥 Stabilitas Termal Tertinggi (Aliphatic Index)",
        "sort_opt_charge": "⚡ Muatan Antibakteri Terkuat (Net Charge @ pH 6.0)",
        "sort_opt_len_asc": "📏 Panjang Sekuens Paling Efisien (Sintesis SPPS)",
        "search_label": "🔍 Cari ID, Motif Asam Amino, atau Peringkat:",
        "search_placeholder": "Cth: #1, 23852, RKK, FLI, atau CDS_...",
        "search_match_info": "Ditemukan {n} kandidat sesuai kata kunci.",
        "search_no_match": "💡 Tidak ada kandidat yang cocok. Coba perpendek kata kunci pencarian.",
        "select_cand": "Peptida Aktif Terpilih:",
        "no_match": "💡 Kriteria filter terlalu ketat. Coba turunkan slider skor untuk melihat kandidat.",

        # Filter Expander (Ergonomics)
        "filter_expander_title": "⚙️ Persempit & Seleksi Kandidat Lolos",
        "filter_help_note": "💡 Slider ini berfungsi mempersempit & memprioritaskan kandidat yang telah lolos kriteria standar biopreservasi tropis.",
        "sidebar_preset": "Pilihan Preset Skrining Cepat:",
        "preset_strict": "Biopreservasi Tropis Ketat (AI >= 60, II < 40)",
        "preset_permissive": "Skrining AMP Umum (Kationik Permisif)",
        "slider_score": "Batas Skor Kelayakan Minimum (AliphaScore-35)",
        "slider_charge": "Muatan Kationik Min @ pH 6.0 (Daya Penetrasi)",
        "slider_ai": "Ketahanan Suhu Panas Min (Aliphatic Index)",
        "slider_ii": "Batas Kerusakan Masa Simpan (Instability Index < 40)",
        "slider_hydro": "Rentang Rasio Hidrofobik (%) (Insersi Membran)",
        "slider_boman": "Prediksi Sitotoksisitas Rendah (Indeks Boman 0.0 - 2.5)",
        "origin_filter": "Asal Sekuens Genomik:",

        # Tabs
        "tab1_title": "📊 1. Dashboard Eksplorasi",
        "tab2_title": "🧬 2. Struktur 3D & Profil Biofisik",
        "tab3_title": "📥 3. Laporan Resmi & Ekspor Data",

        # KPI Metrics
        "kpi_total": "Total Peptida Disaring",
        "kpi_total_sub": "CDS Anotasi & sORF 6-Frame",
        "kpi_passed": "Kandidat Lolos Seleksi",
        "kpi_passed_sub": "Memenuhi 7 filter pangan",
        "kpi_rate": "Laju Kelulusan",
        "kpi_rate_sub": "Tingkat selektivitas biologis",
        "kpi_top": "Skor Preservasi Tertinggi",
        "kpi_top_sub": "Standar Nisin A = 41.22",

        # Visualizations
        "scatter_title": "Pemetaan Biofisik: Ketahanan Panas vs Daya Penetrasi Bakteri",
        "scatter_x": "Ketahanan Suhu Panas (Aliphatic Index)",
        "scatter_y": "Daya Penetrasi Dinding Sel (Muatan Bersih @ pH 6.0)",
        "hist_title": "Distribusi Ketahanan Termal (Aliphatic Index)",
        "hist_x": "Aliphatic Index (AI)",
        "funnel_title": "📊 Corong Standar Tropis (Baseline)",
        "chart_scatter_title_short": "Distribusi Suhu vs Muatan",
        "tab1_top10_title": "🏆 Top 10 Kandidat Tersaring",
        "tab1_top10_col_rank": "Peringkat",
        "tab1_top10_col_id": "ID",
        "tab1_top10_col_score": "Skor AS-35",
        "tab1_top10_col_tier": "Kelas Suhu",
        "tab1_top10_col_len": "Panjang",
        "tab1_top10_col_reason": "Profil Utama",
        "funnel_expander_title": "🔎 Lihat Detail Corong Penyaringan",
        "audit_caption": "Total disaring: {total}, Lolos: {passed} ({rate:.1f}%). Eliminasi terbesar pada tahap: {biggest_drop_reason}.",
        "funnel_crit_total": "Total Sekuens Awal",
        "funnel_crit_charge": "Gagal Muatan @ pH 6.0 (< +2.0)",
        "funnel_crit_ai": "Gagal Ketahanan Panas (< 60.0)",
        "funnel_crit_ii": "Gagal Stabilitas Larutan (>= 40.0)",
        "funnel_crit_pi": "Gagal Titik Isoelektrik (< 8.4)",
        "funnel_crit_hydro": "Gagal Rasio Hidrofobik (Di luar 30-55%)",
        "funnel_crit_boman": "Gagal Indeks Boman (Di luar 0.0-2.5 kcal/mol)",
        "funnel_crit_passed": "Kandidat Lolos Seluruh Kriteria",
        "funnel_caption": "📝 **Catatan Diagnostik**: Grafik ini melacak audisi awal (baseline) dari total {total} populasi data hingga tersaring menjadi {baseline} kandidat yang memenuhi 7 filter dasar pangan. Pengaturan parameter ketat Anda di panel Sidebar kemudian memangkas lagi populasi dasar tersebut menjadi **{active}** kandidat elit yang sedang dianalisis di layar saat ini.",

        # In-Depth Profile
        "cand_profile": "Profil Biofisik Peptida Terpilih",
        "primary_seq": "SEKUENS ASAM AMINO PRIMER",
        "titr_title": "Kurva Titrasi Muatan Henderson-Hasselbalch (pH 0 - 14)",
        "titr_ph4": "pH 4.0 (Pangan Asam)",
        "titr_ph6": "pH 6.0 (Pangan Rendah Asam)",
        "titr_ph7": "pH 7.4 (Matriks Netral)",
        "mol_title": "Model Struktur 3D (Heliks Amfifatik)",
        "mol_caption": "🟢 Tosca = Kationik (Arg, Lys, His) | 🟠 Oranye = Hidrofobik (Ala, Val, Leu, Ile, Phe, Trp, Met)",
        "table_title": "Database Hasil Skrining & Generator Berkas Dossier",
        "btn_csv": "📥 Unduh Tabel Data Lengkap (.CSV)",
        "btn_pdf": "📄 Unduh Berkas Dossier Resmi (.PDF)",
        "glossary_title": "ℹ️ Pelajari Metrik & Standar Acuan",
        "glossary_nisin_title": "Apa itu Nisin A (E234)?",
        "glossary_nisin_desc": "Nisin A adalah bakteriosin alami yang digunakan sebagai standar pengawet pangan komersial global (E234). Nisin sangat efektif, namun sering mengalami degradasi (rusak) pada suhu tinggi di iklim tropis, sehingga diperlukan alternatif peptida yang lebih stabil terhadap panas.",
        "glossary_7filters_title": "Daftar 7 Parameter Skrining",
        "glossary_7filters_desc": "• **Muatan pH 6.0 (Charge)**: Kemampuan penetrasi ke membran bakteri pada kondisi pangan berasam rendah.\n• **Aliphatic Index (AI)**: Indikator stabilitas termal (tahan panas).\n• **Isoelectric Point (pI)**: Titik pH di mana peptida bersifat netral.\n• **Instability Index (II)**: Prediksi masa simpan (shelf-life); < 40 berarti stabil.\n• **Rasio Hidrofobik**: Proporsi asam amino hidrofobik untuk interaksi membran lipid.\n• **Indeks Boman**: Potensi interaksi protein total.\n• **Panjang Sekuens**: < 40 asam amino agar ekonomis disintesis secara kimiawi (SPPS).",
        "empty_state_title": "Belum Ada Data atau Filter Terlalu Ketat",
        "empty_state_desc": "Sesuaikan pengaturan parameter di sidebar sebelah kiri, atau unggah data FASTA Anda jika berada dalam mode Custom Genome."
    },
    "en": {
        "app_title": "Open Studio AMP · Food Biopreservation Peptide Mining",
        "app_sub": "Mining thermostable antimicrobial peptides (AMPs) for clean-label food protection without cold-chain dependence. Supports native Indonesian soil benchmark (G. thermocatenulatus PLS47) and custom laboratory genomes.",
        "badge_env": "BENCHMARK ISOLATE: INDONESIAN GEOTHERMAL SOIL (NCBI: PRJDB8096)",
        
        # Sidebar Structure
        "sidebar_title": "Open Studio AMP",
        "sidebar_sub": "**Antimicrobial Peptide Mining**",
        "sidebar_sub_default": "🌿 *Benchmark Dataset: G. thermocatenulatus PLS47*",
        "sidebar_sub_custom": "📂 *Active Dataset: {name}*",
        "sidebar_methodology_note": "<b>Methodological Note:</b> AliphaScore-35 is a computational prioritization heuristic, not empirical proof of actual antimicrobial activity. Selected candidates must undergo experimental validation in a wet laboratory (wet-lab).",
        "sidebar_lang": "🌐 Language / Pilihan Bahasa:",
        "src_selector_title": "Select Sequence Data Source:",
        "src_default_label": "🔬 Benchmark Dataset (PLS47 Indonesian Soil - 241k Seqs)",
        "src_custom_label": "📂 Upload / Paste Custom Genome (.faa / .fna / .fasta)",
        "upload_tab_file": "📁 Upload FASTA File",
        "upload_tab_paste": "✍️ Paste Manual Sequence",
        "uploader_label": "Select sequence files (.faa, .fna, .fasta, .txt) multiple allowed:",
        "paste_label": "Paste FASTA formatted sequence here (Example: >ID\nSEQUENCE):",
        "custom_success": "✅ Successfully processed {n} candidate peptides from {name}.",
        "upload_too_large": "⚠️ File {name} is larger than 10 MB ({size:.1f} MB) and will be skipped to preserve performance.",
        "custom_empty": "⚠️ No valid sequences found in input. Displaying benchmark dataset.",
        "spinner_db": "Generating database from G. thermocatenulatus PLS47 genome...",
        "spinner_process": "Processing sequences...",
        "custom_data_name": "Custom Data",
        "info_upload_paste": "💡 Upload .faa/.fna or paste sequences above.",
        "input_org_name": "Source Organism Name (for PDF):",
        "input_org_ph": "e.g., Lactobacillus plantarum",
        "input_env_name": "Environmental Origin/Habitat (optional):",
        "input_env_ph": "e.g., Fermented dairy",

        # Candidate Selector Toolbar
        "target_header": "Select Active Peptide Target",
        "sort_label": "Sort Candidate List By:",
        "sort_opt_score": "🏆 Highest Biopreservation Potential (AliphaScore-35)",
        "sort_opt_ai": "🔥 Highest Thermal Stability (Aliphatic Index)",
        "sort_opt_charge": "⚡ Strongest Antibacterial Charge (Net Charge @ pH 6.0)",
        "sort_opt_len_asc": "📏 Most Cost-Efficient Length (SPPS Synthesis)",
        "search_label": "🔍 Search ID, Amino Acid Motif, or Rank:",
        "search_placeholder": "E.g., #1, 23852, RKK, FLI, or CDS_...",
        "search_match_info": "Found {n} candidates matching search query.",
        "search_no_match": "💡 No candidates match this query. Try shortening search keywords.",
        "select_cand": "Active Selected Peptide:",
        "no_match": "💡 Filter criteria are too strict. Try lowering score slider to view candidates.",

        # Filter Expander (Ergonomics)
        "filter_expander_title": "⚙️ Refine & Narrow Passed Candidates",
        "filter_help_note": "💡 These sliders narrow down and prioritize top candidates from the pool that already passed tropical food standards.",
        "sidebar_preset": "Quick Screening Preset Selection:",
        "preset_strict": "Strict Tropical Biopreservation (AI >= 60, II < 40)",
        "preset_permissive": "General AMP Screening (Permissive Cationic)",
        "slider_score": "Minimum Preservation Score (AliphaScore-35)",
        "slider_charge": "Min Cationic Charge @ pH 6.0 (Membrane Penetration)",
        "slider_ai": "Min Heat Stability (Aliphatic Index)",
        "slider_ii": "Max Degradation Threshold (Instability Index < 40)",
        "slider_hydro": "Hydrophobic Ratio Range (%) (Membrane Insertion)",
        "slider_boman": "Predicted Low Cytotoxicity (Boman Index 0.0 - 2.5)",
        "origin_filter": "Genomic Sequence Origin:",

        # Tabs
        "tab1_title": "📊 1. Discovery Dashboard",
        "tab2_title": "🧬 2. 3D Structure & Biophysical Profile",
        "tab3_title": "📥 3. Official Dossier & Data Export",

        # KPI Metrics
        "kpi_total": "Total Peptides Screened",
        "kpi_total_sub": "Annotated CDS & 6-Frame sORFs",
        "kpi_passed": "Candidates Passed Selection",
        "kpi_passed_sub": "Passed all 7 preservation criteria",
        "kpi_rate": "Pass Rate",
        "kpi_rate_sub": "High biological selectivity",
        "kpi_top": "Top Preservation Score",
        "kpi_top_sub": "Nisin A Baseline = 41.22",

        # Visualizations
        "scatter_title": "Biophysical Profile: Thermal Resistance vs Bacterial Penetration",
        "scatter_x": "Thermal Heat Resistance (Aliphatic Index)",
        "scatter_y": "Bacterial Penetration (Net Charge @ pH 6.0)",
        "hist_title": "Thermal Resistance Distribution (Aliphatic Index)",
        "hist_x": "Aliphatic Index (AI)",
        "funnel_title": "📊 Tropical Standard Funnel (Baseline)",
        "chart_scatter_title_short": "Thermal vs Charge Distribution",
        "tab1_top10_title": "🏆 Top 10 Filtered Candidates",
        "tab1_top10_col_rank": "Rank",
        "tab1_top10_col_id": "ID",
        "tab1_top10_col_score": "AS-35 Score",
        "tab1_top10_col_tier": "Thermoclass",
        "tab1_top10_col_len": "Length",
        "tab1_top10_col_reason": "Key Profile",
        "funnel_expander_title": "🔎 View Screening Funnel Details",
        "audit_caption": "Total screened: {total}, Passed: {passed} ({rate:.1f}%). Largest elimination stage: {biggest_drop_reason}.",
        "funnel_crit_total": "Total Starting Sequences",
        "funnel_crit_charge": "Failed Net Charge @ pH 6.0 (< +2.0)",
        "funnel_crit_ai": "Failed Thermal Resistance (< 60.0)",
        "funnel_crit_ii": "Failed Solution Stability (>= 40.0)",
        "funnel_crit_pi": "Failed Isoelectric Point (< 8.4)",
        "funnel_crit_hydro": "Failed Hydrophobic Ratio (Outside 30-55%)",
        "funnel_crit_boman": "Failed Boman Index (Outside 0.0-2.5 kcal/mol)",
        "funnel_crit_passed": "Candidates Passing All Criteria",
        "funnel_caption": "📝 **Diagnostic Note**: This chart tracks the initial baseline audition from the total dataset of {total} down to {baseline} candidates meeting the 7 basic food-grade filters. Your strict sidebar parameter settings then further refine this baseline down to the **{active}** elite candidates currently being analyzed on screen.",

        # In-Depth Profile
        "cand_profile": "Selected Peptide Biophysical Profile",
        "primary_seq": "PRIMARY AMINO ACID SEQUENCE",
        "titr_title": "Henderson-Hasselbalch Charge Titration Curve (pH 0 - 14)",
        "titr_ph4": "pH 4.0 (Acidic Food)",
        "titr_ph6": "pH 6.0 (Low-Acid Food)",
        "titr_ph7": "pH 7.4 (Neutral Matrix)",
        "mol_title": "3D Structural Model (Amphipathic Helix)",
        "mol_caption": "🟢 Teal = Cationic (Arg, Lys, His) | 🟠 Orange = Hydrophobic (Ala, Val, Leu, Ile, Phe, Trp, Met)",
        "table_title": "Screening Database & Dossier File Generator",
        "btn_csv": "📥 Download Full Data Table (.CSV)",
        "btn_pdf": "📄 Download Official Dossier (.PDF)",
        "glossary_title": "ℹ️ Learn Metrics & Reference Standards",
        "glossary_nisin_title": "What is Nisin A (E234)?",
        "glossary_nisin_desc": "Nisin A is a natural bacteriocin used as the global commercial food preservative standard (E234). It is highly effective but often degrades at high temperatures in tropical climates, necessitating more thermostable peptide alternatives.",
        "glossary_7filters_title": "The 7 Screening Parameters",
        "glossary_7filters_desc": "• **Charge at pH 6.0**: Penetration ability into bacterial membranes in low-acid foods.\n• **Aliphatic Index (AI)**: Indicator of thermal stability (heat resistance).\n• **Isoelectric Point (pI)**: The pH at which the peptide is neutral.\n• **Instability Index (II)**: Predicts shelf-life; < 40 indicates stability.\n• **Hydrophobic Ratio**: Proportion of hydrophobic amino acids for lipid membrane interaction.\n• **Boman Index**: Potential for overall protein interaction.\n• **Sequence Length**: < 40 amino acids for cost-effective chemical synthesis (SPPS).",
        "empty_state_title": "No Data or Filters Too Strict",
        "empty_state_desc": "Adjust the parameter settings in the left sidebar, or upload your FASTA data if you are in Custom Genome mode."
    }
}


def build_smart_label(row: Any) -> str:
    score = row.get("as35_score", 0.0)
    ai = row.get("aliphatic_index", 0.0)
    charge = row.get("charge_ph6", 0.0)
    cid = row.get("id", "Unknown")
    return f"[{score:.1f} | AI:{ai:.0f} | Q:{charge:+.1f}] {cid}"
