from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, Union
from collections import Counter

# ==============================================================================
# 1. BIOCHEMICAL CONSTANTS & SCALES
# ==============================================================================

# Standard pKa values based on Lehninger Principles of Biochemistry (METHODOLOGY.md Sec 2)
PKA_LEHNINGER: Dict[str, float] = {
    "N_term": 9.69,
    "C_term": 2.34,
    "R": 12.48,  # Arginine (Guanidino)
    "K": 10.53,  # Lysine (epsilon-amino)
    "H": 6.00,   # Histidine (Imidazole)
    "D": 3.86,   # Aspartate (beta-carboxyl)
    "E": 4.25,   # Glutamate (gamma-carboxyl)
    "C": 8.33,   # Cysteine (Thiol)
    "Y": 10.07,  # Tyrosine (Phenol)
}

# Kyte-Doolittle Hydropathy Scale (Kyte & Doolittle, 1982) for GRAVY calculation
KYTE_DOOLITTLE: Dict[str, float] = {
    "A": 1.8, "C": 2.5, "D": -3.5, "E": -3.5, "F": 2.8,
    "G": -0.4, "H": -3.2, "I": 4.5, "K": -3.9, "L": 3.8,
    "M": 1.9, "N": -3.5, "P": -1.6, "Q": -3.5, "R": -4.5,
    "S": -0.8, "T": -0.7, "V": 4.2, "W": -0.9, "Y": -1.3
}

# Boman Protein-Binding / Membrane Solubility Scale (kcal/mol) (Boman, 2003)
BOMAN_SCALE: Dict[str, float] = {
    "L": -4.92, "I": -4.92, "V": -4.04, "F": -2.98, "M": -2.35, "W": -2.33,
    "A": -1.81, "C": -1.28, "G": -0.94, "Y": -0.14, "T": 2.57,  "S": 3.40,
    "H": 4.66,  "Q": 5.54,  "K": 5.55,  "N": 6.64,  "E": 6.81,  "D": 8.72,
    "R": 14.92, "P": 0.0
}

# Hydrophobic core residues defined in METHODOLOGY.md Sec 5
HYDROPHOBIC_RESIDUES = frozenset({"A", "V", "I", "L", "F", "W", "M"})

# 20 Standard Canonical Amino Acids
STANDARD_AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")

# Dipeptide Instability Weight Values (DIWV) Matrix (Guruprasad et al., 1990)
# Complete 20x20 matrix for Instability Index calculation
DIWV_MATRIX: Dict[str, Dict[str, float]] = {
    "A": {"A": 1.00, "C": 44.94, "D": -7.49, "E": 1.00, "F": 1.00, "G": 1.00, "H": -7.49, "I": 1.00, "K": 1.00, "L": 1.00, "M": 1.00, "N": 1.00, "P": 20.26, "Q": 1.00, "R": 1.00, "S": 1.00, "T": 1.00, "V": 1.00, "W": 1.00, "Y": 1.00},
    "C": {"A": 1.00, "C": 1.00, "D": 20.26, "E": 1.00, "F": 1.00, "G": 1.00, "H": 33.60, "I": 1.00, "K": 1.00, "L": 20.26, "M": 33.60, "N": 1.00, "P": 20.26, "Q": -6.54, "R": 1.00, "S": 1.00, "T": 33.60, "V": -6.54, "W": 24.68, "Y": 1.00},
    "D": {"A": 1.00, "C": 1.00, "D": 1.00, "E": 1.00, "F": -6.54, "G": 1.00, "H": 1.00, "I": 1.00, "K": -7.49, "L": 1.00, "M": 1.00, "N": 1.00, "P": 1.00, "Q": 1.00, "R": -6.54, "S": 20.26, "T": -14.03, "V": 1.00, "W": 1.00, "Y": 1.00},
    "E": {"A": 1.00, "C": 44.94, "D": 20.26, "E": 33.60, "F": 1.00, "G": 1.00, "H": -6.54, "I": 20.26, "K": 1.00, "L": 1.00, "N": 1.00, "P": 20.26, "Q": 20.26, "R": 1.00, "S": 20.26, "T": 1.00, "V": 1.00, "W": -14.03, "Y": 1.00, "M": 1.00},
    "F": {"A": 1.00, "C": 1.00, "D": 1.00, "E": 1.00, "F": 1.00, "G": 1.00, "H": 1.00, "I": 1.00, "K": -7.49, "L": 1.00, "M": 1.00, "N": 1.00, "P": 20.26, "Q": 1.00, "R": 1.00, "S": 1.00, "T": 1.00, "V": 1.00, "W": 1.00, "Y": 33.60},
    "G": {"A": -7.49, "C": 1.00, "D": 1.00, "E": -6.54, "F": 1.00, "G": 13.34, "H": 1.00, "I": -7.49, "K": -7.49, "L": 1.00, "M": 1.00, "N": -7.49, "P": 1.00, "Q": 1.00, "R": 1.00, "S": 1.00, "T": -7.49, "V": 1.00, "W": 13.34, "Y": -7.49},
    "H": {"A": 1.00, "C": 1.00, "D": 1.00, "E": 1.00, "F": -9.37, "G": -9.37, "H": 1.00, "I": 44.94, "K": 24.68, "L": 1.00, "M": 1.00, "N": 24.68, "P": -1.88, "Q": 1.00, "R": 1.00, "S": 1.00, "T": -6.54, "V": 1.00, "W": -1.88, "Y": 44.94},
    "I": {"A": 1.00, "C": 1.00, "D": 1.00, "E": 44.94, "F": 1.00, "G": 1.00, "H": 13.34, "I": 1.00, "K": -7.49, "L": 1.00, "M": 1.00, "N": 1.00, "P": -1.88, "Q": 1.00, "R": 1.00, "S": 1.00, "T": 1.00, "V": -6.54, "W": 1.00, "Y": 1.00},
    "K": {"A": 1.00, "C": 1.00, "D": 1.00, "E": 1.00, "F": 1.00, "G": -7.49, "H": 1.00, "I": -7.49, "K": 1.00, "L": -7.49, "M": 33.60, "N": 1.00, "P": -6.54, "Q": 24.68, "R": 33.60, "S": 1.00, "T": 1.00, "V": -7.49, "W": 1.00, "Y": 1.00},
    "L": {"A": 1.00, "C": 1.00, "D": 1.00, "E": 1.00, "F": 1.00, "G": 1.00, "H": 1.00, "I": 1.00, "K": -7.49, "L": 1.00, "M": 1.00, "N": 1.00, "P": 20.26, "Q": 33.60, "R": 20.26, "S": 1.00, "T": 1.00, "V": 1.00, "W": 24.68, "Y": 1.00},
    "M": {"A": 13.34, "C": 1.00, "D": 1.00, "E": 1.00, "F": 1.00, "G": 1.00, "H": 1.00, "I": 1.00, "K": 1.00, "L": 1.00, "M": -1.88, "N": 1.00, "P": 44.94, "Q": -6.54, "R": -6.54, "S": 44.94, "T": -1.88, "V": 1.00, "W": 1.00, "Y": 24.68},
    "N": {"A": 1.00, "C": -1.88, "D": 1.00, "E": 1.00, "F": -14.03, "G": -14.03, "H": 1.00, "I": 44.94, "K": 24.68, "L": 1.00, "M": 1.00, "N": 1.00, "P": -1.88, "Q": -6.54, "R": 1.00, "S": 1.00, "T": -7.49, "V": 1.00, "W": -9.37, "Y": 1.00},
    "P": {"A": 20.26, "C": -6.54, "D": -6.54, "E": 18.38, "F": 20.26, "G": 1.00, "H": 1.00, "I": 1.00, "K": 1.00, "L": 1.00, "M": -6.54, "N": 1.00, "P": 20.26, "Q": 20.26, "R": -6.54, "S": 20.26, "T": 1.00, "V": 20.26, "W": -1.88, "Y": 1.00},
    "Q": {"A": 1.00, "C": -6.54, "D": 20.26, "E": 20.26, "F": -6.54, "G": 1.00, "H": 1.00, "I": 1.00, "K": 1.00, "L": 1.00, "M": 1.00, "N": 1.00, "P": 20.26, "Q": 20.26, "R": 1.00, "S": 44.94, "T": 1.00, "V": -6.54, "W": 1.00, "Y": -6.54},
    "R": {"A": 1.00, "C": 1.00, "D": 1.00, "E": 1.00, "F": 1.00, "G": -7.49, "H": 20.26, "I": 1.00, "K": 1.00, "L": 1.00, "M": 1.00, "N": 1.00, "P": 20.26, "Q": 20.26, "R": 33.60, "S": 44.94, "T": 1.00, "V": 1.00, "W": 1.00, "Y": -6.54},
    "S": {"A": 1.00, "C": 33.60, "D": 1.00, "E": 1.00, "F": 1.00, "G": 1.00, "H": 1.00, "I": 1.00, "K": 1.00, "L": 1.00, "M": 1.00, "N": 1.00, "P": 44.94, "Q": 20.26, "R": 20.26, "S": 1.00, "T": 1.00, "V": 1.00, "W": 1.00, "Y": 1.00},
    "T": {"A": 1.00, "C": 1.00, "D": 1.00, "E": 20.26, "F": 13.34, "G": -7.49, "H": 1.00, "I": 1.00, "K": 1.00, "L": 1.00, "M": 1.00, "N": -14.03, "P": 1.00, "Q": 1.00, "R": 1.00, "S": 1.00, "T": 1.00, "V": 1.00, "W": -14.03, "Y": 1.00},
    "V": {"A": 1.00, "C": 1.00, "D": -14.03, "E": 1.00, "F": 1.00, "G": -7.49, "H": 1.00, "I": 1.00, "K": -7.49, "L": 1.00, "M": 1.00, "N": 1.00, "P": 20.26, "Q": 1.00, "R": 1.00, "S": 1.00, "T": 1.00, "V": 1.00, "W": 1.00, "Y": -6.54},
    "W": {"A": -14.03, "C": 1.00, "D": 1.00, "E": 1.00, "F": 1.00, "G": -7.49, "H": 1.00, "I": 1.00, "K": 1.00, "L": 13.34, "M": 1.00, "N": 13.34, "P": 1.00, "Q": 1.00, "R": 1.00, "S": 1.00, "T": -7.49, "V": -7.49, "W": 1.00, "Y": 1.00},
    "Y": {"A": 24.68, "C": 1.00, "D": 24.68, "E": -6.54, "F": 1.00, "G": -7.49, "H": 13.34, "I": 1.00, "K": 1.00, "L": 1.00, "M": 44.94, "N": 1.00, "P": 13.34, "Q": 1.00, "R": -14.03, "S": 1.00, "T": 1.00, "V": 1.00, "W": -9.37, "Y": 13.34}
}


# ==============================================================================
# 2. CONFIGURATION DATACLASS
# ==============================================================================

@dataclass
class FilterConfig:
    """
    Configuration parameters and thresholds for tropical food biopreservation screening.
    Default parameters reflect PRD.md Section 5 criteria.
    """
    min_length: int = 5
    max_length: int = 100
    min_charge_ph6: float = 2.0
    min_pi: float = 8.4          # 8.4 allows natural Nisin A (pI 8.48) to pass
    min_aliphatic_index: float = 60.0
    gold_aliphatic_index: float = 80.0
    max_instability_index: float = 40.0
    min_hydrophobic_ratio: float = 28.0   # 28.0% allows Nisin A (29.41%) to pass
    max_hydrophobic_ratio: float = 55.0
    min_gravy: float = -0.8
    max_gravy: float = 0.8
    min_boman_index: float = 0.0
    max_boman_index: float = 2.5

    @classmethod
    def tropical_preset(cls) -> "FilterConfig":
        """Strict extremophile tropical food preservation preset."""
        return cls()

    @classmethod
    def permissive_amp_preset(cls) -> "FilterConfig":
        """Permissive preset for general cationic AMP screening (e.g. mesophilic bacteriocins)."""
        return cls(
            min_aliphatic_index=35.0,
            max_instability_index=80.0,
            min_hydrophobic_ratio=20.0,
            max_boman_index=3.0,
            min_pi=8.0
        )


# ==============================================================================
# 3. ATOMIC BIOCHEMICAL CALCULATION FUNCTIONS
# ==============================================================================

def clean_sequence(raw_sequence: str) -> Tuple[str, bool, str]:
    """
    Cleans and validates a raw amino acid sequence.
    - Strips whitespace and uppercase conversion.
    - Removes terminal stop codon '*'.
    - Validates that only standard 20 amino acids are present.

    Returns:
        (clean_sequence, is_valid, error_message)
    """
    if not raw_sequence or not isinstance(raw_sequence, str):
        return "", False, "Empty or non-string sequence"

    cleaned = raw_sequence.strip().upper()
    if cleaned.endswith("*"):
        cleaned = cleaned[:-1]

    # Check for non-standard amino acid characters
    invalid_chars = set(cleaned) - STANDARD_AMINO_ACIDS
    if invalid_chars:
        return cleaned, False, f"Contains non-canonical amino acids: {', '.join(sorted(invalid_chars))}"

    if len(cleaned) == 0:
        return "", False, "Sequence is empty after cleaning"

    return cleaned, True, ""


def calculate_net_charge(sequence: str, ph: float) -> float:
    """
    Calculates net charge at a specific pH using the continuous Henderson-Hasselbalch equation
    and standard Lehninger pKa values (METHODOLOGY.md Section 2).

    Z(pH) = N_term_pos - C_term_neg + sum(Arg, Lys, His)_pos - sum(Asp, Glu, Cys, Tyr)_neg
    """
    if not sequence:
        return 0.0

    counts = Counter(sequence)

    # Positive contributions (N-terminal + Basic residues)
    pos = 1.0 / (1.0 + 10.0 ** (ph - PKA_LEHNINGER["N_term"]))
    pos += counts.get("R", 0) / (1.0 + 10.0 ** (ph - PKA_LEHNINGER["R"]))
    pos += counts.get("K", 0) / (1.0 + 10.0 ** (ph - PKA_LEHNINGER["K"]))
    pos += counts.get("H", 0) / (1.0 + 10.0 ** (ph - PKA_LEHNINGER["H"]))

    # Negative contributions (C-terminal + Acidic/neutral ionizing residues)
    neg = 1.0 / (1.0 + 10.0 ** (PKA_LEHNINGER["C_term"] - ph))
    neg += counts.get("D", 0) / (1.0 + 10.0 ** (PKA_LEHNINGER["D"] - ph))
    neg += counts.get("E", 0) / (1.0 + 10.0 ** (PKA_LEHNINGER["E"] - ph))
    neg += counts.get("C", 0) / (1.0 + 10.0 ** (PKA_LEHNINGER["C"] - ph))
    neg += counts.get("Y", 0) / (1.0 + 10.0 ** (PKA_LEHNINGER["Y"] - ph))

    return pos - neg


def calculate_isoelectric_point(sequence: str, precision: float = 0.0001, max_iter: int = 100) -> float:
    """
    Finds the isoelectric point (pI) where net charge Z(pH) == 0.0 using the Bisection root-finding method.
    Search range: pH 0.0 to 14.0.
    """
    if not sequence:
        return 7.0

    low = 0.0
    high = 14.0

    # Charge is monotonically decreasing with pH
    for _ in range(max_iter):
        mid = (low + high) / 2.0
        if (high - low) < precision:
            return mid

        charge = calculate_net_charge(sequence, mid)
        if charge > 0:
            low = mid
        else:
            high = mid

    return (low + high) / 2.0


def calculate_aliphatic_index(sequence: str) -> float:
    """
    Calculates the Aliphatic Index (AI) as a proxy for thermal stability (Ikai, 1980).
    AI = X_Ala + 2.9 * X_Val + 3.9 * (X_Ile + X_Leu)
    where X_AA is the molar percentage of that amino acid.
    """
    length = len(sequence)
    if length == 0:
        return 0.0

    counts = Counter(sequence)
    n_ala = counts.get("A", 0)
    n_val = counts.get("V", 0)
    n_ile = counts.get("I", 0)
    n_leu = counts.get("L", 0)

    ai = ((n_ala + 2.9 * n_val + 3.9 * (n_ile + n_leu)) / length) * 100.0
    return ai


def calculate_instability_index(sequence: str) -> float:
    """
    Calculates Guruprasad's Instability Index (II) (Guruprasad et al., 1990).
    II = (10 / L) * sum(DIWV(x_i, x_{i+1}))
    A peptide is considered stable if II < 40.0.
    """
    length = len(sequence)
    if length < 2:
        return 0.0

    total_diwv = 0.0
    for i in range(length - 1):
        aa1 = sequence[i]
        aa2 = sequence[i + 1]
        if aa1 in DIWV_MATRIX and aa2 in DIWV_MATRIX[aa1]:
            total_diwv += DIWV_MATRIX[aa1][aa2]
        else:
            total_diwv += 1.0

    return (10.0 / length) * total_diwv


def calculate_hydrophobic_ratio(sequence: str) -> float:
    """
    Calculates the percentage of hydrophobic residues {A, V, I, L, F, W, M} (METHODOLOGY.md Sec 5).
    """
    length = len(sequence)
    if length == 0:
        return 0.0

    hydro_count = sum(1 for aa in sequence if aa in HYDROPHOBIC_RESIDUES)
    return (hydro_count / length) * 100.0


def calculate_gravy(sequence: str) -> float:
    """
    Calculates the Grand Average of Hydropathicity (GRAVY) based on Kyte-Doolittle scale.
    """
    length = len(sequence)
    if length == 0:
        return 0.0

    total_hydropathy = sum(KYTE_DOOLITTLE.get(aa, 0.0) for aa in sequence)
    return total_hydropathy / length


def calculate_boman_index(sequence: str) -> float:
    """
    Calculates the Boman Index (kcal/mol) as a measure of protein-binding / membrane affinity (Boman, 2003).
    BI = sum(Solubility(aa_i)) / L
    """
    length = len(sequence)
    if length == 0:
        return 0.0

    total_solubility = sum(BOMAN_SCALE.get(aa, 0.0) for aa in sequence)
    return total_solubility / length


def calculate_as35_score(
    aliphatic_index: float,
    charge_ph6: float,
    instability_index: float,
    hydrophobic_ratio: float,
    boman_index: float
) -> float:
    """
    Calculates the AliphaScore-35 (AS-35) Composite Score (0-100) (METHODOLOGY.md Sec 7).
    Weights:
      - 30% Thermal Stability (Aliphatic Index normalized to max 140)
      - 25% Electrostatic Penetration (Charge @ pH 6 normalized to max +6)
      - 20% Shelf-Life Stability (1.0 - II/40.0)
      - 15% Hydrophobic Insertion (Distance from optimal 42.5%)
      - 10% Membrane Affinity (Distance from optimal 1.25 kcal/mol)
    """
    # 1. Thermal score (AI)
    s_thermal = min(max(aliphatic_index / 140.0, 0.0), 1.0)

    # 2. Charge score (Net charge @ pH 6.0)
    s_charge = min(max(charge_ph6 / 6.0, 0.0), 1.0)

    # 3. Stability score (Instability index < 40)
    s_stability = min(max(1.0 - (instability_index / 40.0), 0.0), 1.0)

    # 4. Hydrophobic ratio score (Optimal target 42.5%, tolerance +- 12.5%)
    s_hydro = min(max(1.0 - (abs(hydrophobic_ratio - 42.5) / 12.5), 0.0), 1.0)

    # 5. Membrane affinity / Boman score (Optimal target 1.25 kcal/mol, tolerance +- 1.25)
    s_membrane = min(max(1.0 - (abs(boman_index - 1.25) / 1.25), 0.0), 1.0)

    composite = 100.0 * (
        0.30 * s_thermal +
        0.25 * s_charge +
        0.20 * s_stability +
        0.15 * s_hydro +
        0.10 * s_membrane
    )

    return max(min(composite, 100.0), 0.0)


# ==============================================================================
# 4. PIPELINE AGGREGATOR & EVALUATION INTERFACE
# ==============================================================================

def _build_rejection_record(
    sequence_id: str,
    raw_sequence: str,
    failed_reasons: List[str]
) -> Dict[str, Any]:
    """Helper to generate a clean schema dictionary for invalid sequences."""
    return {
        "id": sequence_id,
        "sequence": raw_sequence,
        "length": len(raw_sequence),
        "isoelectric_point": 0.0,
        "charge_ph4": 0.0,
        "charge_ph6": 0.0,
        "charge_ph7": 0.0,
        "aliphatic_index": 0.0,
        "instability_index": 0.0,
        "hydrophobic_ratio": 0.0,
        "gravy": 0.0,
        "boman_index": 0.0,
        "as35_score": 0.0,
        "thermostability_tier": "Low (AI < 60)",
        "passed_all_filters": False,
        "failed_reasons": failed_reasons
    }


def evaluate_peptide(
    sequence_id: str,
    raw_sequence: str,
    config: Optional[FilterConfig] = None
) -> Dict[str, Any]:
    """
    Evaluates a candidate peptide sequence against tropical food biopreservation criteria.

    Args:
        sequence_id: Identifier for the peptide (e.g. "PLS47_CDS_0042").
        raw_sequence: Raw amino acid sequence string.
        config: FilterConfig dataclass instance (defaults to FilterConfig.tropical_preset()).

    Returns:
        Structured dictionary conforming to ARCHITECTURE.md data schema.
    """
    if config is None:
        config = FilterConfig()

    failed_reasons: List[str] = []

    # 1. Clean and validate sequence
    clean_seq, is_valid, err_msg = clean_sequence(raw_sequence)
    if not is_valid:
        failed_reasons.append(f"Invalid sequence: {err_msg}")
        return _build_rejection_record(sequence_id, raw_sequence, failed_reasons)

    length = len(clean_seq)
    if length < config.min_length or length > config.max_length:
        failed_reasons.append(
            f"Length out of bounds ({length} aa not in [{config.min_length}, {config.max_length}])"
        )
        return _build_rejection_record(sequence_id, clean_seq, failed_reasons)

    # 2. Compute pure biochemical properties
    charge_ph4 = calculate_net_charge(clean_seq, ph=4.0)
    charge_ph6 = calculate_net_charge(clean_seq, ph=6.0)
    charge_ph7 = calculate_net_charge(clean_seq, ph=7.4)
    pi = calculate_isoelectric_point(clean_seq)
    ai = calculate_aliphatic_index(clean_seq)
    ii = calculate_instability_index(clean_seq)
    hydro_ratio = calculate_hydrophobic_ratio(clean_seq)
    gravy = calculate_gravy(clean_seq)
    boman = calculate_boman_index(clean_seq)

    # 3. Evaluate 7 Food Preservation Criteria
    if charge_ph6 < config.min_charge_ph6:
        failed_reasons.append(
            f"Net Charge @ pH 6.0 too low ({charge_ph6:.2f} < {config.min_charge_ph6:.1f})"
        )
    if pi < config.min_pi:
        failed_reasons.append(
            f"Isoelectric Point (pI) too low ({pi:.2f} < {config.min_pi:.1f})"
        )
    if ai < config.min_aliphatic_index:
        failed_reasons.append(
            f"Aliphatic Index too low ({ai:.1f} < {config.min_aliphatic_index:.1f})"
        )
    if ii >= config.max_instability_index:
        failed_reasons.append(
            f"Instability Index too high ({ii:.1f} >= {config.max_instability_index:.1f})"
        )
    if not (config.min_hydrophobic_ratio <= hydro_ratio <= config.max_hydrophobic_ratio):
        failed_reasons.append(
            f"Hydrophobic Ratio out of range ({hydro_ratio:.1f}% not in [{config.min_hydrophobic_ratio}%, {config.max_hydrophobic_ratio}%])"
        )
    if not (config.min_boman_index <= boman <= config.max_boman_index):
        failed_reasons.append(
            f"Boman Index out of range ({boman:.2f} kcal/mol not in [{config.min_boman_index}, {config.max_boman_index}])"
        )

    # 4. Check status & compute score
    passed_all = len(failed_reasons) == 0
    score = calculate_as35_score(ai, charge_ph6, ii, hydro_ratio, boman) if passed_all else 0.0

    # 5. Determine thermostability tier
    if ai >= config.gold_aliphatic_index:
        tier = "Gold Standard (AI >= 80)"
    elif ai >= config.min_aliphatic_index:
        tier = "Moderate (AI >= 60)"
    else:
        tier = "Low (AI < 60)"

    return {
        "id": sequence_id,
        "sequence": clean_seq,
        "length": length,
        "isoelectric_point": round(pi, 2),
        "charge_ph4": round(charge_ph4, 2),
        "charge_ph6": round(charge_ph6, 2),
        "charge_ph7": round(charge_ph7, 2),
        "aliphatic_index": round(ai, 2),
        "instability_index": round(ii, 2),
        "hydrophobic_ratio": round(hydro_ratio, 2),
        "gravy": round(gravy, 3),
        "boman_index": round(boman, 2),
        "as35_score": round(score, 2),
        "thermostability_tier": tier,
        "passed_all_filters": passed_all,
        "failed_reasons": failed_reasons
    }


def evaluate_peptide_batch(
    peptides: List[Tuple[str, str]],
    config: Optional[FilterConfig] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates a batch list of (sequence_id, raw_sequence) tuples.
    """
    if config is None:
        config = FilterConfig()

    return [evaluate_peptide(seq_id, seq, config) for seq_id, seq in peptides]


def generate_preservation_narrative(candidate: Union[Dict[str, Any], Any], lang: str = "id") -> str:
    """
    Generates a dynamic, physicochemical-based narrative evaluating the peptide's suitability
    for tropical food biopreservation without cold-chain dependence.
    """
    if hasattr(candidate, 'to_dict'):
        c = candidate.to_dict()
    elif isinstance(candidate, dict):
        c = candidate
    else:
        c = {}

    ai = float(c.get('aliphatic_index', 0.0))
    c6 = float(c.get('charge_ph6', 0.0))
    ii = float(c.get('instability_index', 0.0))
    boman = float(c.get('boman_index', 0.0))
    hydro = float(c.get('hydrophobic_ratio', 0.0))
    score = float(c.get('as35_score', 0.0))
    length = int(c.get('length', 0))

    if lang == "id":
        # 1. Thermal stability component
        if ai >= 80.0:
            thermal_desc = f"Nilai Aliphatic Index yang sangat tinggi ({ai:.1f}) diprediksi memiliki kepadatan residu alifatik (Ala, Val, Ile, Leu) yang kokoh, berpotensi memberikan stabilitas termal luar biasa terhadap perlakuan panas (pasteurisasi) dan penyimpanan suhu ruang tropis (28-35°C)."
        elif ai >= 60.0:
            thermal_desc = f"Aliphatic Index ({ai:.1f}) diperkirakan memiliki stabilitas termal yang memadai untuk ketahanan pangan tropis tanpa ketergantungan rantai dingin pendingin."
        else:
            thermal_desc = f"Aliphatic Index ({ai:.1f}) memerlukan perhatian khusus terhadap suhu penyimpanan."

        # 2. Charge and antimicrobial penetration
        if c6 >= 3.0:
            charge_desc = f"Muatan kationik kuat pada pH 6.0 (+{c6:.2f}) secara teoretis memfasilitasi interaksi elektrostatis cepat dengan fosfolipid membran bermuatan negatif pada bakteri patogen pangan (seperti Bacillus cereus dan Listeria monocytogenes)."
        elif c6 >= 2.0:
            charge_desc = f"Muatan bersih positif (+{c6:.2f} pada pH 6.0) berpotensi memastikan daya selektivitas pengikatan membran sel mikroba pada matriks pangan asam rendah."
        else:
            charge_desc = f"Muatan pada pH 6.0 (+{c6:.2f}) memberikan afinitas membran terbatas."

        # 3. Stability and Toxicity
        stability_desc = (
            f"Instability Index ({ii:.1f}) diprediksi memiliki struktur yang stabil dalam larutan air (II < 40), yang berpotensi memperpanjang masa simpan produk pangan."
            if ii < 40.0
            else f"Instability Index ({ii:.1f}) mengindikasikan kemungkinan kerentanan degradasi enzimatik atau proteolitik."
        )

        boman_desc = (
            f"Indeks Boman sebesar {boman:.2f} kcal/mol dan rasio hidrofobik {hydro:.1f}% diperkirakan berada dalam rentang ideal untuk insersi pori membran bakteri dengan potensi sitotoksisitas membran yang rendah (berdasarkan proksi heuristik)."
            if (0.0 <= boman <= 2.5 and 25.0 <= hydro <= 60.0)
            else f"Indeks Boman ({boman:.2f} kcal/mol) menunjukkan karakteristik interaksi protein khusus."
        )

        conclusion = (
            f"Secara keseluruhan, berdasarkan evaluasi in silico, dengan AliphaScore-35 (AS-35) {score:.1f}/100 dan panjang {length} asam amino, peptida ini merupakan kandidat biopreservatif berpotensi tinggi untuk aplikasi pangan olahan tropis."
            if score >= 50.0
            else f"Peptida ini memiliki AliphaScore-35 (AS-35) {score:.1f}/100 dan direkomendasikan untuk optimasi struktural lebih lanjut."
        )

        return f"{thermal_desc} {charge_desc} {stability_desc} {boman_desc} {conclusion}"

    else:
        # English narrative
        if ai >= 80.0:
            thermal_desc = f"The exceptionally high Aliphatic Index ({ai:.1f}) indicates a densely packed aliphatic core (Ala, Val, Ile, Leu), providing superior thermal resistance against industrial pasteurization and tropical ambient storage (28-35°C)."
        elif ai >= 60.0:
            thermal_desc = f"An Aliphatic Index of {ai:.1f} confers sufficient thermal robustness for tropical shelf stability without cold-chain reliance."
        else:
            thermal_desc = f"An Aliphatic Index of {ai:.1f} warrants temperature monitoring during distribution."

        if c6 >= 3.0:
            charge_desc = f"A strong cationic net charge at pH 6.0 (+{c6:.2f}) promotes rapid electrostatic binding and membrane permeabilization of key foodborne pathogens (e.g., Bacillus cereus, Listeria monocytogenes)."
        elif c6 >= 2.0:
            charge_desc = f"A net positive charge (+{c6:.2f} at pH 6.0) ensures selective antimicrobial targeting in low-acid food systems."
        else:
            charge_desc = f"The charge at pH 6.0 (+{c6:.2f}) provides modest membrane affinity."

        stability_desc = (
            f"The Instability Index ({ii:.1f} < 40) confirms in-solution structural stability, extending active shelf life in liquid and semi-solid food matrices."
            if ii < 40.0
            else f"The Instability Index ({ii:.1f}) reflects potential vulnerability to proteolysis."
        )

        boman_desc = (
            f"A Boman Index of {boman:.2f} kcal/mol alongside {hydro:.1f}% hydrophobicity is predicted to be well-balanced for bacterial membrane disruption with predicted low membrane cytotoxicity (heuristic proxy)."
            if (0.0 <= boman <= 2.5 and 25.0 <= hydro <= 60.0)
            else f"The Boman Index ({boman:.2f} kcal/mol) indicates distinctive interaction kinetics."
        )

        conclusion = (
            f"Overall, based on in silico profiling, possessing an AliphaScore-35 (AS-35) of {score:.1f}/100 and length of {length} aa, this peptide represents a highly promising biopreservative candidate for tropical food security."
            if score >= 50.0
            else f"The candidate has an AliphaScore-35 (AS-35) of {score:.1f}/100, recommended for rational engineering."
        )

        return f"{thermal_desc} {charge_desc} {stability_desc} {boman_desc} {conclusion}"

