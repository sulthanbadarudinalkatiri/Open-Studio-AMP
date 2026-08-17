# Scientific Methodology & Biochemical Formulas

Dokumen ini merupakan acuan resmi seluruh perhitungan matematika dan biokimia pada modul `src/filters.py`.

---

## 1. Pembersihan & Validasi Sekuens
* Sekuens dibersihkan dari spasi, dikonversi menjadi huruf kapital, dan tanda stop codon (`*`) di ujung dihilangkan.
* Karakter asam amino non-standar (misal: `X, B, Z, J`) ditandai dan dibuang.
* Batas panjang valid untuk analisis: $5 \le L \le 100$ asam amino.

---

## 2. Perhitungan Muatan Bersih (Net Charge) & Titik Isoelektrik (pI)

### Model Kontinu Henderson-Hasselbalch:
Muatan bersih $Z$ pada nilai $\text{pH}$ tertentu dihitung dengan menjumlahkan derajat ionisasi dari N-terminus, C-terminus, dan seluruh rantai samping asam amino bermuatan:

$$Z(\text{pH}) = \frac{1}{1 + 10^{(\text{pH} - \text{p}K_{a,\text{Nterm}})}} - \frac{1}{1 + 10^{(\text{p}K_{a,\text{Cterm}} - \text{pH})}} + \sum_{i \in \{R,K,H\}} \frac{N_i}{1 + 10^{(\text{pH} - \text{p}K_{a,i})}} - \sum_{j \in \{D,E,C,Y\}} \frac{N_j}{1 + 10^{(\text{p}K_{a,j} - \text{pH})}}$$

* **Konstanta pKa Standar (Skala Lehninger):**
  * N-Terminus: $9.69$, C-Terminus: $2.34$
  * Basa: $\text{Arg }(R) = 12.48$, $\text{Lys }(K) = 10.53$, $\text{His }(H) = 6.00$
  * Asam: $\text{Asp }(D) = 3.86$, $\text{Glu }(E) = 4.25$, $\text{Cys }(C) = 8.33$, $\text{Tyr }(Y) = 10.07$

* **Evaluasi Parameter Pangan:**
  * $\text{Net Charge @ pH 6.0} \ge +2.0$ (kondisi kritis makanan asam rendah).
  * $\text{Titik Isoelektrik (pI)} \ge 8.4$ (mencegah presipitasi di makanan).

---

## 3. Indeks Alifatik (Aliphatic Index - AI) — Kestabilan Termal Tropis
* **Referensi:** Ikai, A. (1980). *J. Biochem.*, 88(6), 1895–1898.
* **Formula:**
  $$\text{AI} = X_{\text{Ala}} + 2.9 \cdot X_{\text{Val}} + 3.9 \cdot (X_{\text{Ile}} + X_{\text{Leu}})$$
  *Dimana $X_{\text{AA}}$ adalah persentase molar asam amino:*
  $$X_{\text{AA}} = \left(\frac{N_{\text{AA}}}{L}\right) \times 100$$
* **Ambang Batas Kelayakan:**
  * Lolos Dasar: $\text{AI} \ge 60.0$
  * Ekstremofil Gold Standard: $\text{AI} \ge 80.0$

---

## 4. Indeks Instabilitas (Instability Index - II) — Ketahanan Masa Simpan
* **Referensi:** Guruprasad, K., et al. (1990). *Protein Engineering*, 4(2), 155–161.
* **Formula:**
  $$\text{II} = \frac{10}{L} \sum_{i=1}^{L-1} \text{DIWV}(x_i, x_{i+1})$$
  *Dimana $\text{DIWV}(x_i, x_{i+1})$ adalah nilai bobot instabilitas pasangan dipeptida bersebelahan.*
* **Ambang Batas Kelayakan:**
  * $\text{II} < 40.0 \implies \text{Stabil (Layak Pangan)}$
  * $\text{II} \ge 40.0 \implies \text{Tidak Stabil (Cepat Terurai)}$

---

## 5. Rasio Asam Amino Hidrofobik & GRAVY
* **Grup Asam Amino Hidrofobik:** $\mathcal{H} = \{A, V, I, L, F, W, M\}$
* **Rasio Hidrofobik:**
  $$\%H = \left(\frac{\sum_{aa \in \mathcal{H}} N_{aa}}{L}\right) \times 100 \quad (\text{Target: } 30.0\% - 55.0\%)$$
* **GRAVY (Grand Average of Hydropathicity):**
  $$\text{GRAVY} = \frac{1}{L} \sum_{i=1}^{L} \text{Skor Hidropati Kyte-Doolittle}(aa_i) \quad (\text{Target: } -0.5 \text{ s/d } +0.8)$$

---

## 6. Indeks Boman (Boman Index - BI) — Afinitas Membran & Keamanan
* **Referensi:** Boman, H. G. (2003). *J. Intern. Med.*, 254(3), 197–215.
* **Skala Solubilitas Asam Amino (kcal/mol):**
  $$L: -4.92,\ I: -4.92,\ V: -4.04,\ F: -2.98,\ M: -2.35,\ W: -2.33,\ A: -1.81,\ C: -1.28,\ G: -0.94,\ Y: -0.14,\ T: +2.57,\ S: +3.40,\ H: +4.66,\ Q: +5.54,\ K: +5.55,\ N: +6.64,\ E: +6.81,\ D: +8.72,\ R: +14.92,\ P: 0.0$$
* **Formula:**
  $$\text{BI} = \frac{\sum_{i=1}^{L} \text{Solubilitas}(aa_i)}{L}$$
* **Ambang Batas Kelayakan:** $0.0 \le \text{BI} \le 2.5\text{ kcal/mol}$ (Interaktif terhadap membran mikroba tanpa melisiskan sel manusia).

---

## 7. Formula AliphaScore-35 (AS-35) Composite Score (0–100)
Untuk seluruh kandidat yang lolos seluruh filter eliminasi, dihitung skor komposit:

$$\text{AliphaScore-35} = 100 \times \left( 0.30 \hat{S}_{\text{thermal}} + 0.25 \hat{S}_{\text{charge}} + 0.20 \hat{S}_{\text{stability}} + 0.15 \hat{S}_{\text{hydrophobic}} + 0.10 \hat{S}_{\text{membrane}} \right)$$

* Komponen skor dinormalisasi ke rentang $[0, 1]$:
  * $\hat{S}_{\text{thermal}}$: Nilai Aliphatic Index (skala max 140).
  * $\hat{S}_{\text{charge}}$: Muatan pada pH 6.0 (skala max +6).
  * $\hat{S}_{\text{stability}}$: $1.0 - (\text{II} / 40.0)$.
  * $\hat{S}_{\text{hydrophobic}}$: $1.0 - \frac{|\%H - 42.5|}{12.5}$.
  * $\hat{S}_{\text{membrane}}$: $1.0 - \frac{|\text{BI} - 1.25|}{1.25}$.