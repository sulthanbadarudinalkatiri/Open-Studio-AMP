import math
from typing import Dict, Optional, Tuple
import requests

# 20 Standard Amino Acids 3-Letter Codes
AA_3_LETTER: Dict[str, str] = {
    "A": "ALA", "C": "CYS", "D": "ASP", "E": "GLU", "F": "PHE",
    "G": "GLY", "H": "HIS", "I": "ILE", "K": "LYS", "L": "LEU",
    "M": "MET", "N": "ASN", "P": "PRO", "Q": "GLN", "R": "ARG",
    "S": "SER", "T": "THR", "V": "VAL", "W": "TRP", "Y": "TYR"
}


def generate_ideal_alpha_helix_pdb(sequence: str) -> str:
    """
    Generates canonical right-handed alpha-helix PDB coordinates (100% offline).
    Alpha helix geometry: 3.6 residues per turn, 1.5 Angstrom rise per residue.
    """
    lines = [
        "HEADER    IDEALIZED AMP ALPHA-HELIX BACKBONE",
        f"COMPND    {sequence}",
        "AUTHOR    OPEN STUDIO AMP COMPUTATIONAL ENGINE"
    ]
    atom_id = 1
    for i, aa in enumerate(sequence):
        res_num = i + 1
        aa_3 = AA_3_LETTER.get(aa, "ALA")
        theta = i * (2.0 * math.pi / 3.6)
        z_ca = i * 1.5
        r_ca = 2.3
        x_ca = r_ca * math.cos(theta)
        y_ca = r_ca * math.sin(theta)

        # N atom
        theta_n = theta - 0.5
        x_n = (r_ca - 0.5) * math.cos(theta_n)
        y_n = (r_ca - 0.5) * math.sin(theta_n)
        z_n = z_ca - 0.5
        lines.append(f"ATOM  {atom_id:5d}  N   {aa_3:3s} A{res_num:4d}    {x_n:8.3f}{y_n:8.3f}{z_n:8.3f}  1.00 80.00           N")
        atom_id += 1

        # CA atom
        lines.append(f"ATOM  {atom_id:5d}  CA  {aa_3:3s} A{res_num:4d}    {x_ca:8.3f}{y_ca:8.3f}{z_ca:8.3f}  1.00 85.00           C")
        atom_id += 1

        # C atom
        theta_c = theta + 0.5
        x_c = (r_ca - 0.3) * math.cos(theta_c)
        y_c = (r_ca - 0.3) * math.sin(theta_c)
        z_c = z_ca + 0.6
        lines.append(f"ATOM  {atom_id:5d}  C   {aa_3:3s} A{res_num:4d}    {x_c:8.3f}{y_c:8.3f}{z_c:8.3f}  1.00 85.00           C")
        atom_id += 1

        # O atom
        lines.append(f"ATOM  {atom_id:5d}  O   {aa_3:3s} A{res_num:4d}    {x_c+0.5:8.3f}{y_c+0.5:8.3f}{z_c+0.2:8.3f}  1.00 80.00           O")
        atom_id += 1

    lines.append("END")
    return "\n".join(lines)


def fetch_peptide_3d_pdb(sequence: str, timeout_sec: int = 3) -> Tuple[str, str]:
    """
    Attempts to fetch folded structure from ESMFold API with a reliable local fallback.
    Returns (pdb_string, source_description).
    """
    url = "https://api.esmatlas.com/v1/prediction/"
    try:
        response = requests.post(
            url,
            data=sequence,
            headers={"Content-Type": "text/plain", "User-Agent": "OpenStudioAMP/1.0"},
            timeout=timeout_sec
        )
        if response.status_code == 200 and "ATOM" in response.text:
            return response.text, "ESMFold AI Prediction"
    except Exception:
        pass

    return generate_ideal_alpha_helix_pdb(sequence), "Idealized Alpha-Helix (Local Fallback)"


def build_3dmol_html(
    pdb_data: str,
    height: int = 380,
    primary_color: str = "#0E8388",
    hydrophobic_color: str = "#F97316",
    border_radius: str = "12px",
    border_color: str = "#E2E8F0"
) -> str:
    """
    Constructs clean, self-contained HTML for 3Dmol.js rendering with amphipathic coloring.
    - Cationic (Arg, Lys, His) highlighted in Primary Brand Color (Tosca/Teal)
    - Hydrophobic (Ala, Val, Leu, Ile, Phe, Trp, Met) highlighted in Amber/Orange
    """
    import json
    pdb_clean = json.dumps(pdb_data).replace("<", "\\u003c")
    html_code = f"""
    <div id="container-3d" style="height: {height}px; width: 100%; position: relative; border-radius: {border_radius}; border: 1px solid {border_color}; overflow: hidden; background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);" role="region" aria-label="3D Molecular Model"></div>
    <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    <script>
        let element = document.getElementById("container-3d");
        let viewer = $3Dmol.createViewer(element, {{backgroundColor: "white"}});
        let pdbData = {pdb_clean};
        viewer.addModel(pdbData, "pdb");
        
        viewer.setStyle({{}}, {{cartoon: {{color: 'spectrum', thickness: 0.4}}}});
        viewer.setStyle({{resn: ['ARG', 'LYS', 'HIS']}}, {{cartoon: {{color: '{primary_color}'}}, stick: {{colorscheme: 'cyanCarbon', radius: 0.15}}}});
        viewer.setStyle({{resn: ['ALA', 'VAL', 'LEU', 'ILE', 'PHE', 'TRP', 'MET']}}, {{cartoon: {{color: '{hydrophobic_color}'}}}});

        viewer.zoomTo();
        viewer.render();
        viewer.spin("y", 0.6);
    </script>
    """
    return html_code
