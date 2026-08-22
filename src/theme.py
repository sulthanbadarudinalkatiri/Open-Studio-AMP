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

    /* Clinical Lab Banner: Clean, High-Precision Scientific Surface */
    .main-header {{
        background-color: #FFFFFF;
        padding: 24px 32px;
        border-radius: var(--radius-lg);
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-bottom: 2px solid #0E8388;
        position: relative;
        overflow: hidden;
    }}
    .main-header::after {{
        content: "";
        position: absolute;
        top: 50%;
        right: 28px;
        transform: translateY(-50%);
        width: 130px;
        height: 130px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' fill='none' stroke='%230E8388' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 15 C 40 35, 60 35, 80 15' /%3E%3Cpath d='M20 35 C 40 15, 60 15, 80 35' /%3E%3Cpath d='M20 55 C 40 75, 60 75, 80 55' /%3E%3Cpath d='M20 75 C 40 55, 60 55, 80 75' /%3E%3Cline x1='28' y1='22' x2='72' y2='22' /%3E%3Cline x1='20' y1='35' x2='80' y2='35' /%3E%3Cline x1='35' y1='45' x2='65' y2='45' /%3E%3Cline x1='20' y1='55' x2='80' y2='55' /%3E%3Cline x1='28' y1='68' x2='72' y2='68' /%3E%3Ccircle cx='20' cy='15' r='3' fill='%230E8388'/%3E%3Ccircle cx='80' cy='15' r='3' fill='%230E8388'/%3E%3Ccircle cx='20' cy='35' r='3' fill='%230E8388'/%3E%3Ccircle cx='80' cy='35' r='3' fill='%230E8388'/%3E%3Ccircle cx='20' cy='55' r='3' fill='%230E8388'/%3E%3Ccircle cx='80' cy='55' r='3' fill='%230E8388'/%3E%3Ccircle cx='20' cy='75' r='3' fill='%230E8388'/%3E%3Ccircle cx='80' cy='75' r='3' fill='%230E8388'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        opacity: 0.08;
        pointer-events: none;
    }}
    .main-header h1 {{
        font-size: 24px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.03em;
        color: #0F172A;
    }}
    .main-header p {{
        font-size: 13px;
        margin: 6px 0 0 0;
        font-weight: 400;
        line-height: 1.5;
        max-width: 90%;
        color: #64748B;
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

    /* Bio-Studio Precision Card Containers */
    .bio-card {{
        background: #FFFFFF;
        border: 1px solid rgba(226, 232, 240, 0.85);
        border-radius: var(--radius-md);
        padding: 18px 20px 14px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.02);
        margin-bottom: 20px;
    }}
    .bio-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #F1F5F9;
    }}
    .bio-card-title-group {{
        display: flex;
        flex-direction: column;
    }}
    .bio-card-tag {{
        font-size: 10.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #0E8388;
        margin-bottom: 2px;
    }}
    .bio-card-title {{
        font-size: 15px;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.01em;
    }}
    .bio-card-badge {{
        background: rgba(14, 131, 136, 0.08);
        color: #0E8388;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        border: 1px solid rgba(14, 131, 136, 0.2);
    }}

    /* Selected Candidate Hero Showcase Bar (Tab 2) */
    .target-hero-card {{
        background: #FFFFFF;
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-left: 4px solid var(--color-primary);
        border-radius: var(--radius-md);
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }}
    .target-hero-info {{
        display: flex;
        flex-direction: column;
    }}
    .target-hero-tag {{
        font-size: 10.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--color-primary);
    }}
    .target-hero-id {{
        font-size: 16px;
        font-weight: 800;
        color: #0F172A;
        font-family: var(--font-mono);
        letter-spacing: -0.01em;
    }}
    .target-hero-pills {{
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }}
    .target-stat-pill {{
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 12px;
        color: #334155;
        font-weight: 600;
    }}
    .target-stat-pill strong {{
        color: var(--color-primary);
    }}

    /* Export & Governance Hero Banner (Tab 3) */
    .export-hero-banner {{
        background: #FFFFFF;
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: var(--radius-md);
        padding: 18px 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
    }}
    .export-hero-title {{
        font-size: 16px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.01em;
        margin-bottom: 4px;
    }}
    .export-hero-desc {{
        font-size: 13px;
        color: #64748B;
        margin-bottom: 14px;
        line-height: 1.5;
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


def render_chart_header(tag: str, title: str, badge: str = "") -> str:
    """Renders a clinical card header with badge and uppercase category tag."""
    safe_tag = html.escape(str(tag))
    safe_title = html.escape(str(title))
    safe_badge = html.escape(str(badge))
    badge_html = f'<div class="bio-card-badge">{safe_badge}</div>' if safe_badge else ""
    return f"""
    <div class="bio-card-header">
        <div class="bio-card-title-group">
            <div class="bio-card-tag">{safe_tag}</div>
            <div class="bio-card-title">{safe_title}</div>
        </div>
        {badge_html}
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

        # Visualizations & Panels
        "chart_delta_title": "Keunggulan Relatif Top Kandidat vs Nisin A",
        "panel_delta_tag": "BENCHMARK NISIN A",
        "panel_delta_badge": "Standar E234 (0%)",
        "panel_funnel_tag": "AUDIT PIPELINE SELEKSI",
        "panel_funnel_badge": "7 Filter Pangan",
        "panel_titr_tag": "DINAMIKA ELEKTROSTATIK",
        "panel_titr_badge": "Kurva Henderson-Hasselbalch",
        "panel_mol_tag": "STRUKTUR 3D TERMODELKAN",
        "panel_mol_badge": "Heliks Amfifatik",
        "panel_table_tag": "DATABASE & GOVERNANSI DATA",
        "dossier_box_title": "Ekspor Laporan Resmi & Berkas Tabular",
        "dossier_box_desc": "Unduh berkas dossier PDF komprehensif berstandar publikasi laboratorium atau tabel dataset mentah (.CSV) untuk analisis bioinformatika lanjutan.",
        "target_hero_tag": "PEPTIDA AKTIF TERPILIH",
        "delta_x_axis": "% Keunggulan Relatif vs Kontrol Nisin A (Baseline = 0%)",
        "delta_trace_ai": "Δ Ketahanan Panas (AI)",
        "delta_trace_charge": "Δ Muatan Antibakteri (pH 6)",
        "delta_trace_score": "Δ Skor Biopreservasi (AS-35)",
        "delta_nisin_label": "Kontrol Nisin A (0%)",
        "funnel_expander_title": "Corong Penyaringan Bertingkat",
        "audit_caption": "Total disaring: {total}, Lolos: {passed} ({rate:.1f}%). Eliminasi terbesar pada tahap: {biggest_drop_reason}.",
        "funnel_crit_total": "Total Sekuens Awal",
        "funnel_crit_valid": "Lolos Validasi & Panjang",
        "funnel_crit_charge": "Lolos Muatan @ pH 6.0 (>= +2.0)",
        "funnel_crit_ai": "Lolos Ketahanan Panas (>= 60.0)",
        "funnel_crit_ii": "Lolos Stabilitas Larutan (< 40.0)",
        "funnel_crit_pi": "Lolos Titik Isoelektrik (>= 8.4)",
        "funnel_crit_hydro": "Lolos Rasio Hidrofobik (30-55%)",
        "funnel_crit_boman": "Lolos Indeks Boman (0.0-2.5 kcal/mol)",
        "funnel_crit_passed": "Kandidat Lolos Seluruh Kriteria",
        "funnel_caption": "📝 **Catatan Diagnostik**: Grafik ini melacak audisi awal (baseline) dari total {total} populasi data hingga tersaring menjadi {baseline} kandidat yang memenuhi 7 filter dasar pangan. Pengaturan parameter ketat Anda di panel Sidebar kemudian memangkas lagi populasi dasar tersebut menjadi **{active}** kandidat elit yang sedang dianalisis di layar saat ini.",

        # In-Depth Profile
        "cand_profile": "Profil Biofisik Peptida Terpilih",
        "primary_seq": "SEKUENS ASAM AMINO PRIMER",
        "titr_title": "Kurva Titrasi Muatan (pH 0 - 14)",
        "titr_ph4": "pH 4.0 (Pangan Asam)",
        "titr_ph6": "pH 6.0 (Pangan Rendah Asam)",
        "titr_ph7": "pH 7.4 (Matriks Netral)",
        "mol_title": "Model Struktur 3D Terprediksi",
        "mol_caption": "🟢 Tosca = Kationik (Arg, Lys, His) | 🟠 Oranye = Hidrofobik (Ala, Val, Leu, Ile, Phe, Trp, Met)",
        "table_title": "Eksplorasi Database Kandidat Lolos Seleksi",
        "btn_csv": "📥 Unduh Tabel Data Lengkap (.CSV)",
        "btn_pdf": "📄 Unduh Berkas Dossier Resmi (.PDF)",
        "glossary_title": "📖 Pelajari Metrik & Panduan Parameter",
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

        # Visualizations & Panels
        "chart_delta_title": "Relative Advantage: Top Candidates vs Nisin A",
        "panel_delta_tag": "NISIN A BENCHMARK",
        "panel_delta_badge": "E234 Standard (0%)",
        "panel_funnel_tag": "PIPELINE SELECTION AUDIT",
        "panel_funnel_badge": "7 Food Filters",
        "panel_titr_tag": "ELECTROSTATIC DYNAMICS",
        "panel_titr_badge": "Henderson-Hasselbalch Curve",
        "panel_mol_tag": "3D MODELED STRUCTURE",
        "panel_mol_badge": "Amphipathic Helix",
        "panel_table_tag": "DATABASE & DATA GOVERNANCE",
        "dossier_box_title": "Export Official Dossier & Tabular Dataset",
        "dossier_box_desc": "Download publication-grade scientific PDF dossiers for wet-lab validation or export full raw tabular datasets (.CSV) for advanced downstream bioinformatic workflows.",
        "target_hero_tag": "ACTIVE SELECTED PEPTIDE",
        "delta_x_axis": "% Relative Advantage vs Nisin A Control (Baseline = 0%)",
        "delta_trace_ai": "Δ Heat Stability (AI)",
        "delta_trace_charge": "Δ Antibacterial Charge (pH 6)",
        "delta_trace_score": "Δ Preservation Score (AS-35)",
        "delta_nisin_label": "Nisin A Baseline (0%)",
        "funnel_expander_title": "Multi-Stage Screening Funnel",
        "audit_caption": "Total screened: {total}, Passed: {passed} ({rate:.1f}%). Largest elimination stage: {biggest_drop_reason}.",
        "funnel_crit_total": "Total Starting Sequences",
        "funnel_crit_valid": "Passed Validation & Length",
        "funnel_crit_charge": "Passed Net Charge @ pH 6.0 (>= +2.0)",
        "funnel_crit_ai": "Passed Thermal Resistance (>= 60.0)",
        "funnel_crit_ii": "Passed Solution Stability (< 40.0)",
        "funnel_crit_pi": "Passed Isoelectric Point (>= 8.4)",
        "funnel_crit_hydro": "Passed Hydrophobic Ratio (30-55%)",
        "funnel_crit_boman": "Passed Boman Index (0.0-2.5 kcal/mol)",
        "funnel_crit_passed": "Candidates Passing All Criteria",
        "funnel_caption": "📝 **Diagnostic Note**: This chart tracks the initial baseline audition from the total dataset of {total} down to {baseline} candidates meeting the 7 basic food-grade filters. Your strict sidebar parameter settings then further refine this baseline down to the **{active}** elite candidates currently being analyzed on screen.",

        # In-Depth Profile
        "cand_profile": "Selected Peptide Biophysical Profile",
        "primary_seq": "PRIMARY AMINO ACID SEQUENCE",
        "titr_title": "Charge Titration Curve (pH 0 - 14)",
        "titr_ph4": "pH 4.0 (Acidic Food)",
        "titr_ph6": "pH 6.0 (Low-Acid Food)",
        "titr_ph7": "pH 7.4 (Neutral Matrix)",
        "mol_title": "Predicted 3D Molecular Model",
        "mol_caption": "🟢 Teal = Cationic (Arg, Lys, His) | 🟠 Orange = Hydrophobic (Ala, Val, Leu, Ile, Phe, Trp, Met)",
        "table_title": "Passed Candidates Screening Database",
        "btn_csv": "📥 Download Full Data Table (.CSV)",
        "btn_pdf": "📄 Download Official Dossier (.PDF)",
        "glossary_title": "📖 Learn Metrics & Reference Standards",
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
