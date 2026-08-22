# Product Requirements Document (PRD)

## 1. Overview
* **Product Name:** `Open Studio AMP`
* **Tagline:** Tropical Food Biopreservation Engine & In Silico AMP Miner.
* **Project Genesis:** This project originated from an academic paper and exploratory preliminary study in 2024. The research expanded into a unified bioinformatics computational studio (6-frame sORF extraction, 3D modeling, and scientific dossier generation) while maintaining space for continuous improvement and wet-lab testing collaboration.
* **Strategic Goal:** Build a bioinformatics studio and computational pipeline specifically designed to solve the thermal degradation of food preservatives in tropical climates. This platform mines heat-resistant antimicrobial peptide (AMP) candidates from the genome of the Indonesian soil thermophilic bacterium (*Geobacillus thermocatenulatus* strain PLS47; NCBI: `PRJDB8096`). It also provides a Custom FASTA Ingestion pipeline so food scientists can test custom laboratory genomes against tropical food biopreservation safety standards without relying on cold chains.

---

## 2. Problem & Solution Statement

### Real Problems in the Tropical Food Industry:
1. **Extreme Tropical Heat:** Room temperatures in Indonesia range from 28°C to 35°C with high humidity, accelerating food spoilage by pathogenic bacteria (*Bacillus cereus*, *Listeria monocytogenes*, *Salmonella enterica*).
2. **Cold-Chain Breaks:** The distribution of perishable foods (meat, fresh milk, tofu, coconut milk, ready-to-eat meals) frequently experiences temperature spikes outside major cities.
3. **Limitations of Conventional Preservatives:**
   * Consumers increasingly avoid synthetic chemical preservatives (benzoates, nitrites) due to the clean-label movement.
   * Global commercial biological preservatives like Nisin A (E234) from the mesophilic *Lactococcus lactis* are prone to conformational denaturation and lose bioactivity at tropical room temperatures.

### Open Studio AMP Computational Solution:
A bioinformatics R&D tool specializing in tropical food biopreservation. It filters peptide candidates based on 7 strict biophysicochemical parameters (Aliphatic Index for pasteurization thermal stability, cationic charge at food pH, hydrophobic ratio, and a non-toxic Boman Index host cell safety limit) and ranks candidates using the AliphaScore-35 (AS-35) Composite Score (0–100). A custom extraction pipeline allows food scientists to test their own genome isolates against this standard tropical food matrix.

---

## 3. Target Users (User Personas & Jobs to be Done)
1. **Food Scientists & Biotechnology R&D Teams:**
   * *JTBD:* Find natural biopreservative candidates that resist pasteurization temperatures and remain stable at room temperature to extend the shelf life of low-acid foods without cold-chain dependence.
2. **Academic Reviewers, Lecturers, & Recruiters:**
   * *JTBD:* Verify the integrity of the scientific methodology, the accuracy of biochemical formulas, the 100% green unit tests, and the decoupled Python code architecture.

---

## 4. System Scope

### Core Features:
* **Ingestion & Dual Extraction Engine:** Automated genome data retrieval via the NCBI API with local cache fallback (`data/raw/`), annotated CDS extraction (`.faa`), and *de novo* sORF mining via six-frame translation (`.fna`).
* **Custom FASTA Ingestion:** Parses `.faa` / `.fna` / `.fasta` files and manual in-memory inputs with sequence type auto-detection.
* **Physicochemical Filtering:** Screens against 7 tropical food-specific physicochemical parameters.
* **AliphaScore-35 (AS-35) Composite Scoring:** Ranks top candidates (0–100 scale).
* **Interactive Web Studio:** Streamlit dashboard featuring Henderson-Hasselbalch titration curves, 3D molecular visualization (`3Dmol.js`), and CSV data exports.
* **Academic PDF Dossier Generator:** Exports formal 2-page monochrome A4 reports with dynamic biopreservation narratives and experimental follow-up matrices.
* **Validation Suite:** 64 unit tests based on positive controls, negative controls, local foods, and architectural integrity.

---

## 5. Food Parameter Feasibility Matrix

| No | Parameter | Passing Criteria | Model Reference | Biochemical Food Rationale |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Sequence Length ($L$)** | $5 \le L \le 100$ aa (Optimal: 10–50 aa) | Canonical residues | High bioavailability and efficient industrial synthesis cost. |
| **2** | **Charge @ pH 6.0** | $\ge +2.0$ | Henderson-Hasselbalch | Strong electrostatic penetration into bacterial cell walls in low-acid foods. |
| **3** | **Isoelectric Point (pI)** | $\ge 8.4$ | Neutral charge point | Prevents isoelectric precipitation (settling) in processed food matrices. |
| **4** | **Aliphatic Index (AI)** | $\ge 60.0$ (Ideal $\ge 80.0$) | Ikai (1980) | Structural stability against tropical storage temperatures ($>30^\circ\text{C}$). |
| **5** | **Instability Index (II)** | $< 40.0$ | Guruprasad (1990) | Resistance to spontaneous degradation during product shelf life. |
| **6** | **Hydrophobic Ratio** | $30.0\% \text{ to } 55.0\%$ | Residues $\{A,V,I,L,F,W,M\}$ | Penetrates microbial lipid cores without triggering aggregation/insolubility. |
| **7** | **Boman Index** | $0.0 \text{ to } 2.5 \text{ kcal/mol}$ | Boman (2003) | Optimal membrane interaction without cytotoxicity/lysing human blood cells. |

---

## 6. Validation Controls (64 Unit Tests Benchmark)

| Category | Peptide Control | Key Characteristics | Food Filter Status |
| :--- | :--- | :--- | :---: |
| **Positive Control 1** | Nisin A (Core) | Global commercial lantibiotic | **Pass (Baseline = 41.22)** |
| **Positive Control 2** | Pediocin PA-1 | Lactic acid bacteria bacteriocin | **Pass (Permissive Preset)** |
| **Positive Control 3** | Lactoferricin B | Cationic AMP from milk whey | **Pass (Permissive Preset)** |
| **Negative Control 1** | Casein CMP fragment | Anionic-neutral hydrophilic fragment | **Fail (Charge < +2.0)** |
| **Negative Control 2** | Melittin (Bee Venom) | Cytotoxic to red blood cells | **Fail (Instability & Toxic)** |
| **Negative Control 3** | Poly-Acid Fragment | Pure aspartic & glutamic acids | **Fail (Negative Charge & Low AI)** |
| **Local Food 1** | Tempeh Glycinin Fragment | Bioactive peptide from fermented soybeans | **Characterized Profile** |
| **Local Food 2** | Casocidin-I | Antimicrobial peptide from milk casein | **Characterized Profile** |