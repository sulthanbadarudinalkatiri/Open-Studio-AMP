# Product Requirements Document (PRD)

## 1. Overview
* **Nama Produk:** `Open Studio AMP`
* **Tagline:** Tropical Food Biopreservation Engine & In Silico AMP Miner.
* **Rekam Jejak Riset (Project Genesis):** Proyek ini berakar dari karya ilmiah dan studi pendahuluan eksploratif pada tahun **2024**. Riset ini kemudian diperdalam dan dikembangkan menjadi studio komputasional bioinformatika terpadu (ekstraksi sORF 6-frame, pemodelan 3D, dan generator dossier ilmiah) dengan tetap membuka ruang untuk perbaikan dan kolaborasi pengujian laboratorium basah.
* **Tujuan Strategis:** Membangun studio bioinformatika dan pipeline komputasi yang secara khusus dirancang untuk menjawab masalah degradasi termal pengawet pangan di iklim tropis. Platform ini menambang kandidat peptida antimikroba (AMP) tahan panas dari genom bakteri termofilik tanah Indonesia (*Geobacillus thermocatenulatus* strain PLS47; NCBI: `PRJDB8096`) dan menyediakan jalur *Custom FASTA Ingestion* untuk menguji genom kustom laboratorium terhadap standar keamanan biopreservasi pangan tropis tanpa ketergantungan rantai dingin (*cold-chain free*).

---

## 2. Problem & Solution Statement

### Masalah Nyata Industri Pangan Tropis:
1. **Suhu Tropis Ekstrem:** Suhu ruang di Indonesia berkisar antara **28°C hingga 35°C** dengan kelembapan tinggi, mempercepat pembusukan pangan oleh bakteri patogen (*Bacillus cereus*, *Listeria monocytogenes*, *Salmonella enterica*).
2. **Kerapuhan Rantai Dingin (*Cold-Chain Breaks*):** Distribusi bahan pangan mudah rusak (daging, susu segar, tahu, santan, makanan siap saji) sering mengalami kenaikan suhu di luar kota besar.
3. **Keterbatasan Pengawet Konvensional:**
   * Pengawet kimia sintetis (benzoat, nitrit) semakin dihindari konsumen (*clean-label movement*).
   * Pengawet biologis komersial dunia seperti Nisin A (E234) dari *Lactococcus lactis* mesofilik rentan mengalami denaturasi konformasional dan kehilangan bioaktivitas pada suhu ruang tropis.

### Solusi Komputasional Open Studio AMP:
Alat R&D bioinformatika spesialis biopreservasi pangan tropis yang memfilter kandidat peptida berdasarkan 7 parameter biofisikokimia ketat (Aliphatic Index untuk stabilitas termal pasteurisasi, muatan kationik pada pH pangan, rasio hidrofobik, dan batas keamanan sel inang Boman Index non-toksik) serta merangking kandidat menggunakan AliphaScore-35 (AS-35) Composite Score (0–100). Jalur ekstraksi kustom disediakan agar peneliti pangan dapat menguji isolat genom mereka sendiri terhadap matriks standar pangan tropis ini.

---

## 3. Target Pengguna (User Personas & Jobs to be Done)
1. **Ilmuwan Pangan & Tim R&D Bioteknologi:**
   * *JTBD:* Menemukan kandidat biopreservatif alami yang kebal terhadap suhu pasteurisasi dan stabil pada suhu ruang untuk memperpanjang umur simpan produk pangan asam rendah tanpa beban rantai dingin.
2. **Reviewer Akademis, Dosen, & Recruiter:**
   * *JTBD:* Memverifikasi integritas metodologi sains, ketepatan rumus biokimia, pengujian unit test 100% green, dan arsitektur kode Python terdekoplasi.

---

## 4. Ruang Lingkup Sistem (Scope)

### Fitur Utama:
* **Ingestion & Dual Extraction Engine:** Pengambilan data genom otomatis via NCBI API dengan cache fallback lokal (`data/raw/`), ekstraksi CDS teranotasi (`.faa`), dan penambangan *de novo* sORF via *six-frame translation* (`.fna`).
* **Custom FASTA Ingestion:** Parsing berkas `.faa` / `.fna` / `.fasta` dan input manual in-memory dengan auto-detection tipe sekuens.
* **Physicochemical Filtering:** Penyaringan 7 parameter fisikokimia spesifik pangan tropis.
* **AliphaScore-35 (AS-35) Composite Scoring:** Perangkingan kandidat terbaik (skala 0–100).
* **Interactive Web Studio:** Dashboard Streamlit dengan kurva titrasi Henderson-Hasselbalch, visualisasi 3D molekul (`3Dmol.js`), dan ekspor data CSV.
* **Academic PDF Dossier Generator:** Ekspor laporan formal 2-halaman monochrome A4 dengan narasi biopreservasi dinamis dan matriks rencana tindak lanjut eksperimen.
* **Validation Suite:** Pengujian 59 unit tests berbasis kontrol positif, negatif, pangan lokal, dan integritas arsitektur.

---

## 5. Matriks Kelayakan Parameter Pangan

| No | Parameter | Kriteria Kelayakan | Referensi Model | Alasan Biokimia Pangan |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Panjang Sekuens ($L$)** | $5 \le L \le 100$ aa (Optimal: 10–50 aa) | Residu kanonikal | Bioavailabilitas tinggi dan biaya sintesis industri efisien. |
| **2** | **Muatan @ pH 6.0** | $\ge +2.0$ | Henderson-Hasselbalch | Penetrasi elektrostatik kuat ke dinding sel bakteri pada pangan asam rendah. |
| **3** | **Titik Isoelektrik (pI)** | $\ge 8.4$ | Titik muatan netral | Mencegah presipitasi isoelektrik (pengendapan) di matriks pangan olahan. |
| **4** | **Aliphatic Index (AI)** | $\ge 60.0$ (Ideal $\ge 80.0$) | Ikai (1980) | Kestabilan struktur terhadap suhu penyimpanan tropis ($>30^\circ\text{C}$). |
| **5** | **Instability Index (II)** | $< 40.0$ | Guruprasad (1990) | Ketahanan terhadap degradasi spontan selama masa simpan produk. |
| **6** | **Hydrophobic Ratio** | $30.0\% \text{ s/d } 55.0\%$ | Residu $\{A,V,I,L,F,W,M\}$ | Penusukan inti lipid membran mikroba tanpa memicu agregasi/ketaklarutan. |
| **7** | **Boman Index** | $0.0 \text{ s/d } 2.5 \text{ kcal/mol}$ | Boman (2003) | Interaksi membran optimal tanpa sitotoksisitas/lisis sel darah manusia. |

---

## 6. Kontrol Validasi (59 Unit Tests Benchmark)

| Kategori | Kontrol Peptida | Karakteristik Kunci | Status Filter Pangan |
| :--- | :--- | :--- | :---: |
| **Kontrol Positif 1** | Nisin A (Core) | Lantibiotik komersial dunia | **Lolos (Baseline = 41.22)** |
| **Kontrol Positif 2** | Pediocin PA-1 | Bakteriosin bakteri asam laktat | **Lolos (Preset Permisif)** |
| **Kontrol Positif 3** | Lactoferricin B | AMP kationik asal whey susu | **Lolos (Preset Permisif)** |
| **Kontrol Negatif 1** | Casein CMP fragment | Fragmen hidrofilik anik-netral | **Gagal (Muatan < +2.0)** |
| **Kontrol Negatif 2** | Melittin (Bisa Lebah) | Sitotoksik sel darah merah | **Gagal (Instabilitas & Toksik)** |
| **Kontrol Negatif 3** | Fragmen Poli-Asam | Asam aspartat & glutamat murni | **Gagal (Muatan Negatif & AI Rendah)** |
| **Pangan Lokal 1** | Tempe Glycinin Fragment | Peptida bioaktif fermentasi kedelai | **Profil Terkarakterisasi** |
| **Pangan Lokal 2** | Casocidin-I | Peptida antimikroba kasein susu | **Profil Terkarakterisasi** |