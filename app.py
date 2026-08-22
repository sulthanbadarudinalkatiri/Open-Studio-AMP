import html
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import re

SMART_LABEL_PATTERN = re.compile(r"^(?:#|RANK\s*|TOP\s*)?(\d+)$")

from src.theme import (
    DESIGN_TOKENS,
    CUSTOM_CSS,
    I18N,
    render_kpi_card,
    get_base_chart_layout,
    C, R, S, TYPO,
    build_smart_label
)
from src.reporter import generate_dossier_pdf
from src.structure import fetch_peptide_3d_pdb, build_3dmol_html
from src.filters import (
    FilterConfig,
    evaluate_peptide,
    evaluate_peptide_batch,
    calculate_net_charge,
    calculate_isoelectric_point,
    PKA_LEHNINGER,
    HYDROPHOBIC_RESIDUES
)
from src.extractor import extract_from_custom_fasta
from engine import run_pipeline, NISIN_A_SEQUENCE


def _safe(value: Any, max_len: int = 100) -> str:
    if not isinstance(value, str):
        value = str(value)
    return html.escape(value[:max_len])


@st.cache_data(show_spinner=False)
def get_cached_pdf(candidate: dict, top10_df: pd.DataFrame, nisin_res: dict, lang: str, organism_info: str) -> bytes:
    return generate_dossier_pdf(
        candidate=candidate,
        top10_df=top10_df,
        nisin_res=nisin_res,
        lang=lang,
        organism_info=organism_info
    )

# ==============================================================================
# 1. PAGE SETUP & THEME INITIALIZATION
# ==============================================================================

st.set_page_config(
    page_title="Open Studio AMP",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# 2. DATA INGESTION & CACHING
# ==============================================================================

@st.cache_data(show_spinner=False)
def load_screening_data() -> pd.DataFrame:
    target = Path("data/processed/pls47_candidates.parquet")
    
    # If the user is running the app for the first time and hasn't run the backend
    if not target.exists():
        with st.spinner("Initializing bio-screening pipeline... (First run only)"):
            df_all, _ = run_pipeline(
                bioproject="PRJDB8096",
                prefix="pls47",
                mode="all",
                preset="tropical",
                output_parquet=str(target)
            )
            return df_all

    df = pd.read_parquet(target, engine="pyarrow")
    
    # Backward compatibility for old schemas
    if "extremopreserve_score" in df.columns:
        df = df.rename(columns={"extremopreserve_score": "as35_score"})

    return df


@st.cache_data(show_spinner=False)
def process_custom_fasta_data(fasta_content: str, filename: str = "custom.fasta") -> pd.DataFrame:
    """
    Extracts and evaluates peptide candidates in-memory from user-provided FASTA text.
    Handles auto-detection of protein (.faa) vs DNA (.fna via 6-frame translation).
    Returns unified 17-column DataFrame schema matching load_screening_data.
    """
    if not fasta_content or not fasta_content.strip():
        return pd.DataFrame()

    prefix = filename[:10].replace(" ", "_").replace(".", "_")
    extracted = list(extract_from_custom_fasta(fasta_content, organism_prefix=prefix))
    if not extracted:
        return pd.DataFrame()

    peptides = [(c["id"], c["sequence"]) for c in extracted]
    evaluated = evaluate_peptide_batch(peptides, FilterConfig.tropical_preset())
    
    df_custom = pd.DataFrame(evaluated)
    df_custom["source"] = [c["source"] for c in extracted]
    return df_custom


# ==============================================================================
# 3. MAIN APPLICATION CONTROLLER
# ==============================================================================

def main():
    nisin_res = evaluate_peptide("Nisin_A_Baseline", NISIN_A_SEQUENCE)

    # Language Switcher
    lang_choice = st.sidebar.radio(
        "🌐 Language / Bahasa:",
        ["🇮🇩 Bahasa Indonesia", "🇬🇧 English"],
        index=0
    )
    lang_key = "id" if "Indonesia" in lang_choice else "en"
    t = I18N[lang_key]

    st.sidebar.title(f"🧬 {t['sidebar_title']}")
    
    # Dynamic Subtitle based on active dataset
    is_custom_source = st.session_state.get("data_source_radio") == t["src_custom_label"]
    custom_active_name = st.session_state.get("custom_org_name", "").strip() or st.session_state.get("custom_active_filename", t["custom_data_name"])
    
    if is_custom_source and custom_active_name:
        st.sidebar.markdown(t["sidebar_sub_custom"].format(name=_safe(custom_active_name, 28)))
    else:
        st.sidebar.markdown(t["sidebar_sub_default"])
        
    st.sidebar.markdown(
        f"""
        <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 10px; line-height: 1.3;">
        {t['sidebar_methodology_note']}
        </div>
        """, unsafe_allow_html=True
    )
    st.sidebar.divider()

    # 1. Genomic Data Source Selector
    st.sidebar.subheader(t["src_selector_title"])
    src_choice = st.sidebar.radio(
        "Pilihan Sumber Data:",
        [t["src_default_label"], t["src_custom_label"]],
        index=0,
        key="data_source_radio",
        label_visibility="collapsed"
    )

    df_raw = None
    active_dataset_name = "PLS47_PRJDB8096"

    if src_choice == t["src_default_label"]:
        df_raw = load_screening_data()
        active_dataset_name = "Geobacillus thermocatenulatus PLS47 (NCBI PRJDB8096)"
    else:
        # Custom FASTA Input Tabs
        upload_tab1, upload_tab2 = st.sidebar.tabs([t["upload_tab_file"], t["upload_tab_paste"]])
        custom_files_data = []
        custom_name_display = ""

        with upload_tab1:
            uploaded_files = st.file_uploader(
                t["uploader_label"],
                type=["faa", "fna", "fasta", "txt"],
                key="custom_fasta_file",
                accept_multiple_files=True
            )
            if uploaded_files:
                valid_files = []
                for uf in uploaded_files:
                    size_mb = uf.size / (1024 * 1024)
                    if size_mb > 10.0:
                        st.sidebar.warning(t["upload_too_large"].format(name=_safe(uf.name), size=size_mb))
                        continue
                    
                    custom_files_data.append({
                        "name": uf.name,
                        "content": uf.getvalue().decode("utf-8", errors="replace")
                    })
                    valid_files.append(uf)
                
                if valid_files:
                    custom_name_display = ", ".join(uf.name for uf in valid_files)
                    st.session_state["custom_active_filename"] = _safe(custom_name_display)

        with upload_tab2:
            pasted_text = st.text_area(
                t["paste_label"],
                height=110,
                placeholder=">Sample_Peptide_1\nMGGERVTIQNLKIVKVDPERNLLLIKGNVPGPRKGLVIVKSAVKAAKKAK",
                key="custom_fasta_paste"
            )
            if pasted_text and pasted_text.strip() and not custom_files_data:
                custom_files_data.append({
                    "name": "Input_Manual_FASTA",
                    "content": pasted_text.strip()
                })
                custom_name_display = "Input_Manual_FASTA"
                st.session_state["custom_active_filename"] = _safe(custom_name_display)

        if custom_files_data:
            with st.sidebar:
                with st.spinner(t["spinner_process"]):
                    dfs = []
                    for fdata in custom_files_data:
                        df_f = process_custom_fasta_data(fdata["content"], filename=fdata["name"])
                        if not df_f.empty:
                            dfs.append(df_f)
                    
                    if dfs:
                        df_custom = pd.concat(dfs, ignore_index=True)
                    else:
                        df_custom = pd.DataFrame()

            if len(df_custom) > 0:
                df_raw = df_custom
                active_dataset_name = _safe(custom_name_display)
                disp_name = _safe(custom_name_display, 27) + ("..." if len(custom_name_display) > 27 else "")
                st.sidebar.success(t["custom_success"].format(n=len(df_custom), name=disp_name))
            else:
                st.sidebar.warning(t["custom_empty"])
                df_raw = load_screening_data()
        else:
            st.sidebar.info(t["info_upload_paste"])
            df_raw = load_screening_data()
        
        st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        custom_organism_name = st.sidebar.text_input(
            t["input_org_name"],
            placeholder=t["input_org_ph"],
            key="custom_org_name_input"
        )
        custom_environment = st.sidebar.text_input(
            t["input_env_name"],
            placeholder=t["input_env_ph"],
            key="custom_env_input"
        )
        st.session_state['custom_org_name'] = _safe(custom_organism_name)
        st.session_state['custom_env'] = _safe(custom_environment)

    # 2. Collapsible Filter Expander (Ergonomic Friction Reduction)
    with st.sidebar.expander(t["filter_expander_title"], expanded=False):
        st.caption(t["filter_help_note"])
        preset_label = st.radio(
            t["sidebar_preset"],
            [t["preset_strict"], t["preset_permissive"]],
            index=0
        )

        if preset_label == t["preset_strict"]:
            default_min_score = 60.0
            default_min_charge = 2.0
            default_min_ai = 60.0
            default_max_ii = 40.0
        else:
            default_min_score = 30.0
            default_min_charge = 1.0
            default_min_ai = 35.0
            default_max_ii = 70.0

        slider_score = st.slider(t["slider_score"], 0.0, 100.0, default_min_score, 1.0)
        slider_charge = st.slider(t["slider_charge"], 0.0, 10.0, default_min_charge, 0.5)
        slider_ai = st.slider(t["slider_ai"], 0.0, 160.0, default_min_ai, 5.0)
        slider_ii = st.slider(t["slider_ii"], 10.0, 100.0, default_max_ii, 5.0)
        slider_hydro = st.slider(t["slider_hydro"], 0.0, 100.0, (25.0, 60.0), 1.0)
        slider_boman = st.slider(t["slider_boman"], -2.0, 8.0, (0.0, 2.5), 0.1)

        available_sources = list(df_raw["source"].unique()) if "source" in df_raw.columns and len(df_raw) > 0 else ["CDS", "sORF"]
        source_filter = st.multiselect(t["origin_filter"], available_sources, default=available_sources)

    # 3. Dynamic Filter Computation
    filtered_df = df_raw[
        (df_raw["as35_score"] >= slider_score) &
        (df_raw["charge_ph6"] >= slider_charge) &
        (df_raw["aliphatic_index"] >= slider_ai) &
        (df_raw["instability_index"] <= slider_ii) &
        (df_raw["hydrophobic_ratio"] >= slider_hydro[0]) &
        (df_raw["hydrophobic_ratio"] <= slider_hydro[1]) &
        (df_raw["boman_index"] >= slider_boman[0]) &
        (df_raw["boman_index"] <= slider_boman[1]) &
        (df_raw["source"].isin(source_filter)) &
        (df_raw["passed_all_filters"] == True)
    ].sort_values(by="as35_score", ascending=False).reset_index(drop=True)

    # 4. Candidate Selector Toolbar (Sort + Search + Smart Labels)
    st.sidebar.divider()
    st.sidebar.subheader(t["target_header"])

    sort_options = [
        t["sort_opt_score"],
        t["sort_opt_ai"],
        t["sort_opt_charge"],
        t["sort_opt_len_asc"]
    ]
    sort_choice = st.sidebar.selectbox(t["sort_label"], sort_options, index=0)

    if sort_choice == t["sort_opt_score"]:
        filtered_df = filtered_df.sort_values(by="as35_score", ascending=False).reset_index(drop=True)
    elif sort_choice == t["sort_opt_ai"]:
        filtered_df = filtered_df.sort_values(by="aliphatic_index", ascending=False).reset_index(drop=True)
    elif sort_choice == t["sort_opt_charge"]:
        filtered_df = filtered_df.sort_values(by="charge_ph6", ascending=False).reset_index(drop=True)
    elif sort_choice == t["sort_opt_len_asc"]:
        filtered_df = filtered_df.sort_values(by="length", ascending=True).reset_index(drop=True)

    search_query = st.sidebar.text_input(t["search_label"], placeholder=t["search_placeholder"]).strip()

    search_filtered_df = filtered_df
    if search_query and len(filtered_df) > 0:
        query_clean = search_query.strip()
        query_upper = query_clean.upper()
        
        # 1. ID matching (case-insensitive literal substring)
        id_match = search_filtered_df["id"].astype(str).str.contains(query_clean, regex=False, case=False, na=False)
        
        # 2. Sequence motif matching (case-insensitive literal substring)
        seq_match = search_filtered_df["sequence"].astype(str).str.contains(query_upper, regex=False, case=False, na=False)
        
        # 3. Smart label / substring matching
        label_match = search_filtered_df.apply(lambda row: query_clean.lower() in build_smart_label(row).lower(), axis=1)
        
        # 4. Rank matching: e.g. "#1", "Rank 1", "Top 5", "1", "10"
        rank_match = pd.Series(False, index=search_filtered_df.index)
        rank_search = SMART_LABEL_PATTERN.search(query_upper)
        if rank_search:
            rank_num = int(rank_search.group(1))
            if 1 <= rank_num <= len(search_filtered_df):
                rank_match.iloc[rank_num - 1] = True
        
        search_filtered_df = search_filtered_df[id_match | seq_match | label_match | rank_match].reset_index(drop=True)

    if len(search_filtered_df) > 0:
        if search_query:
            st.sidebar.caption(t["search_match_info"].format(n=len(search_filtered_df)))

        candidate_indices = list(range(len(search_filtered_df)))
        display_options = [build_smart_label(row) for _, row in search_filtered_df.iterrows()]

        selected_idx = st.sidebar.selectbox(
            t["select_cand"],
            options=candidate_indices,
            format_func=lambda i: display_options[i],
            index=0
        )
        selected_candidate = search_filtered_df.iloc[selected_idx]
        selected_cand_id = selected_candidate["id"]
    else:
        if search_query:
            st.sidebar.warning(t["search_no_match"])
        else:
            st.sidebar.warning(t["no_match"])

        if len(filtered_df) > 0:
            selected_candidate = filtered_df.iloc[0]
            selected_cand_id = filtered_df.iloc[0]["id"]
        elif len(df_raw) > 0:
            selected_candidate = df_raw.iloc[0]
            selected_cand_id = df_raw.iloc[0]["id"]
        else:
            selected_candidate = pd.Series(nisin_res)
            selected_cand_id = "Nisin_A_Baseline"

    # --------------------------------------------------------------------------
    # MAIN HEADER BANNER (ANTIGRAVITY BIOLUMINESCENT DEPTH)
    # --------------------------------------------------------------------------
    safe_app_title = html.escape(t['app_title'])
    safe_app_sub = html.escape(t['app_sub'])
    safe_badge_env = html.escape(t['badge_env'])
    st.markdown(
        f"""
        <header class="main-header" role="banner">
            <div class="header-badge">⚡ {safe_badge_env}</div>
            <h1>{safe_app_title}</h1>
            <p>{safe_app_sub}</p>
        </header>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------------------------
    # ACTIVE FILTERS GLOBAL INDICATOR
    # --------------------------------------------------------------------------
    pill_style = "background: rgba(0, 171, 179, 0.25); border: 1px solid rgba(0, 171, 179, 0.8); padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; color: #FFFFFF; text-shadow: 0px 1px 2px rgba(0,0,0,0.5);"
    pills_html = f"""
    <div style='display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; margin-bottom: 24px; align-items: center;'>
        <span style='font-size: 13px; font-weight: 600; color: #CBD5E1; margin-right: 4px;'>Active Filters:</span>
        <span style='{pill_style}'>AS-35 ≥ {slider_score}</span>
        <span style='{pill_style}'>Charge ≥ {slider_charge}</span>
        <span style='{pill_style}'>AI ≥ {slider_ai}</span>
        <span style='{pill_style}'>II ≤ {slider_ii}</span>
        <span style='{pill_style}'>Hydro: {slider_hydro[0]}-{slider_hydro[1]}%</span>
        <span style='{pill_style}'>Boman: {slider_boman[0]:.1f} to {slider_boman[1]:.1f}</span>
    </div>
    """
    st.markdown(pills_html, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 3 INTERACTIVE WORKSPACE TABS
    # --------------------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs([t["tab1_title"], t["tab2_title"], t["tab3_title"]])

    # ==========================================================================
    # TAB 1: DISCOVERY DASHBOARD
    # ==========================================================================
    with tab1:
        total_screened = len(df_raw)
        total_passed = len(filtered_df)
        pass_rate = (total_passed / total_screened * 100.0) if total_screened > 0 else 0.0
        top_score = filtered_df["as35_score"].max() if total_passed > 0 else 0.0

        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        with col_kpi1:
            st.markdown(render_kpi_card(t["kpi_total"], f"{total_screened:,}", t["kpi_total_sub"]), unsafe_allow_html=True)
        with col_kpi2:
            st.markdown(render_kpi_card(t["kpi_passed"], f"{total_passed:,}", t["kpi_passed_sub"]), unsafe_allow_html=True)
        with col_kpi3:
            st.markdown(render_kpi_card(t["kpi_rate"], f"{pass_rate:.2f}%", t["kpi_rate_sub"]), unsafe_allow_html=True)
        with col_kpi4:
            st.markdown(render_kpi_card(t["kpi_top"], f"{top_score:.2f}", t["kpi_top_sub"]), unsafe_allow_html=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        with st.expander(t.get("glossary_title", "ℹ️ Glossary")):
            st.markdown(f"**{t.get('glossary_nisin_title', '')}**")
            st.write(t.get("glossary_nisin_desc", ""))
            st.markdown(f"**{t.get('glossary_7filters_title', '')}**")
            st.markdown(t.get("glossary_7filters_desc", ""))

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        if total_passed == 0:
            st.info(f"**{t.get('empty_state_title', '')}**\n\n{t.get('empty_state_desc', '')}", icon="ℹ️")
        else:
            # 1. Scatter Plot (Hero Chart)
            st.subheader(t["chart_scatter_title_short"])
            
            scatter_plot_df = filtered_df.copy()
            color_map = {
                "Thermophilic": "#F97316",
                "Mesophilic": "#0E8388"
            }
            fig_scatter = px.scatter(
                scatter_plot_df,
                x="aliphatic_index",
                y="charge_ph6",
                color="thermostability_tier",
                hover_name="id",
                hover_data={"aliphatic_index": ":.1f", "charge_ph6": ":.2f", "as35_score": ":.2f", "source": True},
                color_discrete_map=color_map,
                labels={"aliphatic_index": t["scatter_x"], "charge_ph6": t["scatter_y"], "thermostability_tier": t["tab1_top10_col_tier"]}
            )
            
            # Nisin A Control Point
            fig_scatter.add_trace(go.Scatter(
                x=[nisin_res["aliphatic_index"]],
                y=[nisin_res["charge_ph6"]],
                mode="markers+text",
                marker=dict(size=14, color=C["danger"], symbol="diamond", line=dict(width=2, color="#FFFFFF")),
                name="Nisin A Control",
                text=["Nisin A (E234)"],
                textposition="top right",
                textfont=dict(family=TYPO["font_family"], color=C["danger"], size=12),
                showlegend=False
            ))

            # Selected Candidate Point
            if selected_candidate is not None:
                fig_scatter.add_trace(go.Scatter(
                    x=[selected_candidate["aliphatic_index"]],
                    y=[selected_candidate["charge_ph6"]],
                    mode="markers",
                    marker=dict(size=18, color="#FFFFFF", symbol="star", line=dict(width=2, color=C["primary"])),
                    name="Selected Target",
                    hoverinfo="skip",
                    showlegend=False
                ))

            fig_scatter.update_layout(**get_base_chart_layout(height=420))
            fig_scatter.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False)
            fig_scatter.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False)
            st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})

            # 2. Funnel logic & Audit Caption
            if total_screened > 0:
                all_fail_lists = df_raw["failed_reasons"].tolist()
                
                def count_cumulative(*reasons):
                    return sum(1 for r in all_fail_lists if not isinstance(r, list) or not any(sub in item for sub in reasons for item in r))

                funnel_nums = [
                    total_screened,
                    count_cumulative("Charge @ pH 6.0"),
                    count_cumulative("Charge @ pH 6.0", "Aliphatic Index"),
                    count_cumulative("Charge @ pH 6.0", "Aliphatic Index", "Instability Index"),
                    count_cumulative("Charge @ pH 6.0", "Aliphatic Index", "Instability Index", "Isoelectric Point"),
                    count_cumulative("Charge @ pH 6.0", "Aliphatic Index", "Instability Index", "Isoelectric Point", "Hydrophobic Ratio"),
                    count_cumulative("Charge @ pH 6.0", "Aliphatic Index", "Instability Index", "Isoelectric Point", "Hydrophobic Ratio", "Boman Index"),
                    int((df_raw["passed_all_filters"] == True).sum())
                ]
                
                funnel_stages = [
                    t["funnel_crit_total"],
                    t["funnel_crit_charge"],
                    t["funnel_crit_ai"],
                    t["funnel_crit_ii"],
                    t["funnel_crit_pi"],
                    t["funnel_crit_hydro"],
                    t["funnel_crit_boman"],
                    t["funnel_crit_passed"]
                ]
                
                # Find biggest drop
                drops = [funnel_nums[i] - funnel_nums[i+1] for i in range(len(funnel_nums)-1)]
                max_drop_idx = drops.index(max(drops)) if drops else 0
                biggest_drop_reason = funnel_stages[max_drop_idx + 1]
                
                audit_text = t["audit_caption"].format(
                    total=f"{total_screened:,}",
                    passed=f"{total_passed:,}",
                    rate=pass_rate,
                    biggest_drop_reason=biggest_drop_reason
                )
                st.caption(audit_text)
                
                # 3. Funnel Expander
                with st.expander(t["funnel_expander_title"]):
                    funnel_data = dict(number=funnel_nums, stage=funnel_stages)
                    fig_funnel = px.funnel(
                        funnel_data,
                        y="stage",
                        x="number",
                        color_discrete_sequence=["#0E8388"]
                    )
                    funnel_layout = get_base_chart_layout(height=410, margin=dict(l=10, r=10, t=10, b=10))
                    funnel_layout["yaxis"] = dict(title="", tickfont=dict(size=10, family=TYPO["font_family"]))
                    fig_funnel.update_layout(**funnel_layout)
                    st.plotly_chart(fig_funnel, use_container_width=True)



    # ==========================================================================
    # TAB 2: 3D STRUCTURE & TITRATION CURVES
    # ==========================================================================
    with tab2:
        st.subheader(f"{t['cand_profile']}: {selected_candidate['id']}")
        
        # Primary sequence box
        st.caption(t["primary_seq"])
        safe_seq = html.escape(str(selected_candidate['sequence']))
        st.markdown(f'<div class="seq-box">{safe_seq}</div>', unsafe_allow_html=True)
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        col_titr, col_3d = st.columns([1.1, 1.1])

        # Henderson-Hasselbalch Titration Curve
        with col_titr:
            st.subheader(t["titr_title"])
            ph_range = np.linspace(0, 14, 141)
            cand_charges = [calculate_net_charge(selected_candidate['sequence'], float(ph)) for ph in ph_range]
            nisin_charges = [calculate_net_charge(NISIN_A_SEQUENCE, float(ph)) for ph in ph_range]

            fig_titr = go.Figure()
            fig_titr.add_trace(go.Scatter(
                x=ph_range, y=cand_charges,
                mode="lines",
                name=f"{selected_candidate['id'][:20]}...",
                line=dict(color=C["primary"], width=3)
            ))
            fig_titr.add_trace(go.Scatter(
                x=ph_range, y=nisin_charges,
                mode="lines",
                name="Nisin A Control",
                line=dict(color=C["danger"], width=2, dash="dash")
            ))

            # pH Milestones
            fig_titr.add_vline(x=4.0, line_dash="dot", line_color=C["warning"], annotation_text="pH 4.0", annotation_position="top left")
            fig_titr.add_vline(x=6.0, line_dash="dot", line_color=C["primary"], annotation_text="pH 6.0", annotation_position="top left")
            fig_titr.add_vline(x=7.4, line_dash="dot", line_color=C["neutral_400"], annotation_text="pH 7.4", annotation_position="top right")
            fig_titr.add_hline(y=0.0, line_color=C["neutral_200"], line_width=1)

            titr_layout = get_base_chart_layout(height=380)
            titr_layout["xaxis"]["title"] = "Environmental pH"
            titr_layout["yaxis"]["title"] = "Net Electrical Charge (z)"
            titr_layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            fig_titr.update_layout(**titr_layout)
            st.plotly_chart(fig_titr, use_container_width=True)

        # 3D Molecular Viewport
        with col_3d:
            st.subheader(t["mol_title"])
            pdb_str, model_source = fetch_peptide_3d_pdb(selected_candidate['sequence'])
            st.caption(f"Model: **{model_source}** | {t['mol_caption']}")
            html_3d = build_3dmol_html(pdb_str, height=340, primary_color=C["primary"], hydrophobic_color=C["amber"])
            components.html(html_3d, height=350)

    # ==========================================================================
    # TAB 3: EXPORT & OFFICIAL R&D DOSSIER
    # ==========================================================================
    with tab3:
        st.subheader(t["table_title"])
        
        # Summary & Export Buttons
        col_btn1, col_btn2 = st.columns([1, 1])
        
        with col_btn1:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=t["btn_csv"],
                data=csv_data,
                file_name=f"Open_Studio_AMP_Screening_{_safe(active_dataset_name, 12)}.csv",
                mime="text/csv",
                use_container_width=True,
                key="tab3_csv_download"
            )

        with col_btn2:
            custom_org = st.session_state.get('custom_org_name', '').strip()
            custom_env = st.session_state.get('custom_env', '').strip()
            if custom_org:
                organism_info = f"{custom_org} (Habitat: {custom_env})" if custom_env else custom_org
            else:
                organism_info = ""

            pdf_bytes = get_cached_pdf(
                candidate=selected_candidate,
                top10_df=filtered_df if len(filtered_df) > 0 else df_raw,
                nisin_res=nisin_res,
                lang=lang_key,
                organism_info=organism_info
            )
            st.download_button(
                label=t["btn_pdf"],
                data=pdf_bytes,
                file_name=f"AMP_Report_{selected_candidate['id'][:25]}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="tab3_pdf_download"
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        display_df = filtered_df[[
            "id", "source", "length", "charge_ph6", "isoelectric_point",
            "aliphatic_index", "instability_index", "hydrophobic_ratio",
            "boman_index", "as35_score"
        ]].copy()
        
        column_mapping_id = {
            "id": "ID Peptida",
            "source": "Asal Genom",
            "length": "Panjang (aa)",
            "charge_ph6": "Muatan @ pH 6",
            "isoelectric_point": "Titik Isoelektrik (pI)",
            "aliphatic_index": "Stabilitas Termal (AI)",
            "instability_index": "Stabilitas Larutan (II)",
            "hydrophobic_ratio": "Rasio Hidrofobik (%)",
            "boman_index": "Indeks Boman (kcal/mol)",
            "as35_score": "AliphaScore-35 (0-100)"
        }
        column_mapping_en = {
            "id": "Peptide ID",
            "source": "Genomic Origin",
            "length": "Length (aa)",
            "charge_ph6": "Charge @ pH 6",
            "isoelectric_point": "Isoelectric Point (pI)",
            "aliphatic_index": "Thermal Stability (AI)",
            "instability_index": "Solution Stability (II)",
            "hydrophobic_ratio": "Hydrophobic Ratio (%)",
            "boman_index": "Boman Index (kcal/mol)",
            "as35_score": "AliphaScore-35 (0-100)"
        }
        mapping = column_mapping_id if lang_key == "id" else column_mapping_en
        display_df = display_df.rename(columns=mapping)
        st.dataframe(display_df, use_container_width=True, height=380)


if __name__ == "__main__":
    main()
