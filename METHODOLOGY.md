# Scientific Methodology & Biochemical Formulas

This document is the official reference for all mathematical and biochemical calculations in the `src/filters.py` module.

---

## 1. Sequence Cleaning & Validation
* Sequences are stripped of spaces, converted to uppercase, and trailing stop codons (`*`) are removed.
* Non-standard amino acid characters (e.g., `X, B, Z, J`) invalidate the sequence, leading to its removal.
* Valid length limit for analysis: $5 \le L \le 100$ amino acids.

---

## 2. Net Charge & Isoelectric Point (pI) Calculation

### Continuous Henderson-Hasselbalch Model:
The net charge $Z$ at a specific $\text{pH}$ is calculated by summing the degree of ionization from the N-terminus, C-terminus, and all charged amino acid side chains:

$$Z(\text{pH}) = \frac{1}{1 + 10^{(\text{pH} - \text{p}K_{a,\text{Nterm}})}} - \frac{1}{1 + 10^{(\text{p}K_{a,\text{Cterm}} - \text{pH})}} + \sum_{i \in \{R,K,H\}} \frac{N_i}{1 + 10^{(\text{pH} - \text{p}K_{a,i})}} - \sum_{j \in \{D,E,C,Y\}} \frac{N_j}{1 + 10^{(\text{p}K_{a,j} - \text{pH})}}$$

* **Standard pKa Constants (Lehninger Scale):**
  * N-Terminus: $9.69$, C-Terminus: $2.34$
  * Basic: $\text{Arg }(R) = 12.48$, $\text{Lys }(K) = 10.53$, $\text{His }(H) = 6.00$
  * Acidic: $\text{Asp }(D) = 3.86$, $\text{Glu }(E) = 4.25$, $\text{Cys }(C) = 8.33$, $\text{Tyr }(Y) = 10.07$

* **Food Parameter Evaluation:**
  * $\text{Net Charge @ pH 6.0} \ge +2.0$ (critical threshold for low-acid foods).
  * $\text{Isoelectric Point (pI)} \ge 8.4$ (prevents precipitation in food matrices).

---

## 3. Aliphatic Index (AI) - Tropical Thermal Stability
* **Reference:** Ikai, A. (1980). *J. Biochem.*, 88(6), 1895-1898. [DOI: 10.1093/oxfordjournals.jbchem.a133168](https://doi.org/10.1093/oxfordjournals.jbchem.a133168)
* **Formula:**
  $$\text{AI} = X_{\text{Ala}} + 2.9 \cdot X_{\text{Val}} + 3.9 \cdot (X_{\text{Ile}} + X_{\text{Leu}})$$
  *Where $X_{\text{AA}}$ is the molar percentage of the amino acid:*
  $$X_{\text{AA}} = \left(\frac{N_{\text{AA}}}{L}\right) \times 100$$
* **Passing Thresholds:**
  * Baseline Pass: $\text{AI} \ge 60.0$
  * Extremophile Gold Standard: $\text{AI} \ge 80.0$

---

## 4. Instability Index (II) - Shelf-life Durability
* **Reference:** Guruprasad, K., et al. (1990). *Protein Engineering*, 4(2), 155-161. [DOI: 10.1093/protein/4.2.155](https://doi.org/10.1093/protein/4.2.155)
* **Formula:**
  $$\text{II} = \frac{10}{L} \sum_{i=1}^{L-1} \text{DIWV}(x_i, x_{i+1})$$
  *Where $\text{DIWV}(x_i, x_{i+1})$ is the instability weight value of the adjacent dipeptide pair.*
* **Passing Thresholds:**
  * $\text{II} < 40.0 \implies \text{Stable (Food-grade)}$
  * $\text{II} \ge 40.0 \implies \text{Unstable (Rapidly degrades)}$

---

## 5. Hydrophobic Amino Acid Ratio & GRAVY
* **Hydrophobic Amino Acid Group:** $\mathcal{H} = \{A, V, I, L, F, W, M\}$
* **Hydrophobic Ratio:**
  $$\%H = \left(\frac{\sum_{aa \in \mathcal{H}} N_{aa}}{L}\right) \times 100 \quad (\text{Target: } 30.0\% - 55.0\%)$$
* **GRAVY (Grand Average of Hydropathicity):**
  $$\text{GRAVY} = \frac{1}{L} \sum_{i=1}^{L} \text{Kyte-Doolittle Hydropathy Score}(aa_i) \quad (\text{Target: } -0.5 \text{ to } +0.8)$$

---

## 6. Boman Index (BI) - Membrane Affinity & Safety
* **Reference:** Boman, H. G. (2003). *J. Intern. Med.*, 254(3), 197-215. [DOI: 10.1046/j.1365-2796.2003.01228.x](https://doi.org/10.1046/j.1365-2796.2003.01228.x)
* **Amino Acid Solubility Scale (kcal/mol):**
  $$L: -4.92,\ I: -4.92,\ V: -4.04,\ F: -2.98,\ M: -2.35,\ W: -2.33,\ A: -1.81,\ C: -1.28,\ G: -0.94,\ Y: -0.14,\ T: +2.57,\ S: +3.40,\ H: +4.66,\ Q: +5.54,\ K: +5.55,\ N: +6.64,\ E: +6.81,\ D: +8.72,\ R: +14.92,\ P: 0.0$$
* **Formula:**
  $$\text{BI} = \frac{\sum_{i=1}^{L} \text{Solubility}(aa_i)}{L}$$
* **Passing Thresholds:** $0.0 \le \text{BI} \le 2.5\text{ kcal/mol}$ (Predicted low membrane cytotoxicity / heuristic proxy).

---

## 7. AliphaScore-35 (AS-35) Composite Score (0-100)
For all candidates passing the elimination filters, we calculate a composite score:

$$\text{AliphaScore-35} = 100 \times \left( 0.30 \hat{S}_{\text{thermal}} + 0.25 \hat{S}_{\text{charge}} + 0.20 \hat{S}_{\text{stability}} + 0.15 \hat{S}_{\text{hydrophobic}} + 0.10 \hat{S}_{\text{membrane}} \right)$$

* Score components are normalized to a $[0, 1]$ range:
  * $\hat{S}_{\text{thermal}}$: Aliphatic Index value (max scale 140).
  * $\hat{S}_{\text{charge}}$: Charge at pH 6.0 (max scale +6).
  * $\hat{S}_{\text{stability}}$: $1.0 - (\text{II} / 40.0)$.
  * $\hat{S}_{\text{hydrophobic}}$: $1.0 - \frac{|\%H - 42.5|}{12.5}$.
  * $\hat{S}_{\text{membrane}}$: $1.0 - \frac{|\text{BI} - 1.25|}{1.25}$.
---

## 8. Scientific Limitations & False-Positive Risks

The biochemical screening pipeline relies on foundational thermodynamic and physicochemical heuristics. When applied to short antimicrobial peptides (AMPs), users must acknowledge the following computational and biological limitations:

* **Lack of Homology Validation:** The pipeline relies purely on rule-based physicochemical filters without performing homology searches (BLAST/DIAMOND) or HMM profile alignments (Pfam/InterPro) against known AMP databases (e.g., DRAMP, APD3).
* **False-Positive Risk from 6-Frame Translation:** Because the pipeline performs *de novo* 6-frame translation on raw genomic DNA, there is a high risk of extracting random sequences (spurious ORFs). A translation artifact that coincidentally happens to be rich in cationic (Arg/Lys) and aliphatic (Ala/Val) residues might achieve a high AliphaScore-35, even though it is biologically meaningless translation noise.
* **Missing AntiFam / Domain Checks:** Without evolutionary domain validation (such as AntiFam to discard non-coding regions), all discovered sequences must be treated strictly as **putative candidates**.
* **Structural Discrepancies:** Models such as the Aliphatic Index (Ikai 1980) and Instability Index (Guruprasad 1990) are based on the statistical distribution of residues in folded globular proteins. Short peptides (< 50 aa) are often *intrinsically disordered* in aqueous solutions.
* **Absence of Post-Translational Modifications (PTMs):** This *in silico* pipeline analyzes primary amino acid sequences translated directly from DNA. It does not predict structural fortifications like disulfide bridges, cyclization, or lanthionine rings (crucial for bacteriocins like Nisin A).
* **Heuristic Calibration:** The thresholds applied are not universal biological truths, but **food-grade screening heuristics calibrated against Nisin A**.

> **Crucial Requirement:** Due to these inherent limitations, computational screening serves only as a preliminary sieve. The Top putative candidates generated by this pipeline **must** undergo Solid-Phase Peptide Synthesis (SPPS) and *in vitro* Minimum Inhibitory Concentration (MIC) tests in a physical wet-lab to validate their actual antimicrobial efficacy and structural viability.

**Further Reading on Computational AMP Discovery & Food Safety (Open Access / Free Full Text):**
1. Bisht, V., Das, B., Hussain, A., Kumar, V., & Navani, N. K. (2024). *Understanding of probiotic origin antimicrobial peptides: a sustainable approach ensuring food safety.* **npj Science of Food** (Nature Portfolio), 8, 64. [DOI: 10.1038/s41538-024-00304-8](https://doi.org/10.1038/s41538-024-00304-8) (Open Access, Free PDF)
2. Capecchi, A., et al. (2022). *Rational Discovery of Antimicrobial Peptides by Means of Artificial Intelligence.* **Membranes** (MDPI), 12(7), 708. [DOI: 10.3390/membranes12070708](https://doi.org/10.3390/membranes12070708) (Open Access, Free PDF)


