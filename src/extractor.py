from pathlib import Path
from typing import Dict, Iterator, Optional, Set, Tuple, Union, Any, List
from Bio import SeqIO
from Bio.Seq import Seq

# ==============================================================================
# 1. CONSTANTS
# ==============================================================================

# Thermophilic Tri-Start Codons for Gram-positive extremophiles (Geobacillus / Bacillus)
TRI_START_CODONS: Set[str] = {"ATG", "GTG", "TTG"}

# Standard Universal Stop Codons
STOP_CODONS: Set[str] = {"TAA", "TAG", "TGA"}

# 20 Standard Amino Acids
VALID_AA_SET: Set[str] = set("ACDEFGHIKLMNPQRSTVWY")


# ==============================================================================
# 2. PHASE 1: ANNOTATED CDS EXTRACTOR
# ==============================================================================

def extract_annotated_cds(
    faa_path: Union[str, Path],
    organism_prefix: str = "PLS47",
    min_len: int = 5,
    max_len: int = 100
) -> Iterator[Dict[str, Any]]:
    """
    Extracts annotated short peptides from a protein FASTA file (.faa).
    
    Filters:
      - Ignores non-canonical amino acids (X, B, Z, J, etc.)
      - Pre-filters length to range [min_len, max_len] aa.
      - Strips terminal stop codon '*' if present.
    
    Yields:
        Dictionary: {"id": str, "sequence": str, "source": "CDS", "length": int, "description": str}
    """
    faa_file = Path(faa_path)
    if not faa_file.exists():
        raise FileNotFoundError(f"Protein FASTA file not found: {faa_file}")

    for record in SeqIO.parse(str(faa_file), "fasta"):
        raw_seq = str(record.seq).strip().upper()
        if raw_seq.endswith("*"):
            raw_seq = raw_seq[:-1]

        # Check length
        seq_len = len(raw_seq)
        if not (min_len <= seq_len <= max_len):
            continue

        # Check for invalid non-canonical amino acids
        if set(raw_seq) - VALID_AA_SET:
            continue

        # Extract clean locus tag or accession ID
        locus_id = record.id.replace("|", "_").replace(".", "_")
        formatted_id = f"{organism_prefix}_CDS_{locus_id}_{seq_len}aa"

        yield {
            "id": formatted_id,
            "sequence": raw_seq,
            "source": "CDS",
            "length": seq_len,
            "description": record.description
        }


# ==============================================================================
# 3. PHASE 2: SIX-FRAME sORF EXTRACTOR
# ==============================================================================

def extract_six_frame_sorfs(
    fna_path: Union[str, Path],
    organism_prefix: str = "PLS47",
    min_len: int = 5,
    max_len: int = 100,
    start_codons: Optional[Set[str]] = None
) -> Iterator[Dict[str, Any]]:
    """
    Performs de novo 6-frame translation on a genomic DNA FASTA file (.fna) to mine
    cryptic small Open Reading Frames (sORFs).

    Scans 3 forward frames (+1, +2, +3) and 3 reverse-complement frames (-1, -2, -3)
    using thermophilic tri-start initiation codons (ATG, GTG, TTG) to in-frame stop codons.

    Yields:
        Dictionary: {
            "id": str,
            "sequence": str,
            "source": "sORF",
            "length": int,
            "frame": str,
            "strand": str,
            "start": int,
            "end": int
        }
    """
    if start_codons is None:
        start_codons = TRI_START_CODONS

    fna_file = Path(fna_path)
    if not fna_file.exists():
        raise FileNotFoundError(f"Genomic DNA FASTA file not found: {fna_file}")

    for record in SeqIO.parse(str(fna_file), "fasta"):
        fwd_dna_str = str(record.seq).strip().upper()
        rev_dna_str = str(Seq(fwd_dna_str).reverse_complement())
        seq_len_nt = len(fwd_dna_str)

        # ----------------------------------------------------------------------
        # 1. Forward Strand (+1, +2, +3)
        # ----------------------------------------------------------------------
        for frame_offset in range(3):
            frame_label = f"+{frame_offset + 1}"
            sub_seq = fwd_dna_str[frame_offset:]
            n_codons = len(sub_seq) // 3

            start_codon_positions = []
            for codon_idx in range(n_codons):
                nt_pos = frame_offset + (codon_idx * 3)
                codon = sub_seq[codon_idx * 3 : (codon_idx + 1) * 3]

                if codon in start_codons:
                    start_codon_positions.append((codon_idx, nt_pos))
                elif codon in STOP_CODONS:
                    # Resolve all pending sORFs ending at this stop codon
                    for s_idx, s_nt_pos in start_codon_positions:
                        orf_aa_len = codon_idx - s_idx
                        if min_len <= orf_aa_len <= max_len:
                            # Include in-frame stop codon to invoke NCBI Table 11 initiator decoding (GTG/TTG -> M)
                            orf_nt = fwd_dna_str[s_nt_pos : nt_pos + 3]
                            try:
                                translated_peptide = str(Seq(orf_nt).translate(table=11, cds=True))
                            except Exception:
                                continue
                            
                            # Validate canonical amino acids
                            if not (set(translated_peptide) - VALID_AA_SET):
                                end_nt_pos = nt_pos + 3
                                orf_id = (
                                    f"{organism_prefix}_sORF_F{frame_label}_"
                                    f"{s_nt_pos + 1}_{end_nt_pos}_fwd_{orf_aa_len}aa"
                                )
                                yield {
                                    "id": orf_id,
                                    "sequence": translated_peptide,
                                    "source": "sORF",
                                    "length": orf_aa_len,
                                    "frame": frame_label,
                                    "strand": "forward",
                                    "start": s_nt_pos + 1,
                                    "end": end_nt_pos
                                }
                    start_codon_positions = []

        # ----------------------------------------------------------------------
        # 2. Reverse Complement Strand (-1, -2, -3)
        # ----------------------------------------------------------------------
        for frame_offset in range(3):
            frame_label = f"-{frame_offset + 1}"
            sub_seq = rev_dna_str[frame_offset:]
            n_codons = len(sub_seq) // 3

            start_codon_positions = []
            for codon_idx in range(n_codons):
                nt_pos_rev = frame_offset + (codon_idx * 3)
                codon = sub_seq[codon_idx * 3 : (codon_idx + 1) * 3]

                if codon in start_codons:
                    start_codon_positions.append((codon_idx, nt_pos_rev))
                elif codon in STOP_CODONS:
                    for s_idx, s_nt_pos in start_codon_positions:
                        orf_aa_len = codon_idx - s_idx
                        if min_len <= orf_aa_len <= max_len:
                            # Include in-frame stop codon to invoke NCBI Table 11 initiator decoding (GTG/TTG -> M)
                            orf_nt = rev_dna_str[s_nt_pos : nt_pos_rev + 3]
                            try:
                                translated_peptide = str(Seq(orf_nt).translate(table=11, cds=True))
                            except Exception:
                                continue

                            if not (set(translated_peptide) - VALID_AA_SET):
                                # Map coordinates relative to original forward strand
                                orig_start = seq_len_nt - (nt_pos_rev + 3) + 1
                                orig_end = seq_len_nt - s_nt_pos
                                orf_id = (
                                    f"{organism_prefix}_sORF_F{frame_label}_"
                                    f"{orig_start}_{orig_end}_rev_{orf_aa_len}aa"
                                )
                                yield {
                                    "id": orf_id,
                                    "sequence": translated_peptide,
                                    "source": "sORF",
                                    "length": orf_aa_len,
                                    "frame": frame_label,
                                    "strand": "reverse",
                                    "start": orig_start,
                                    "end": orig_end
                                }
                    start_codon_positions = []


# ==============================================================================
# 4. UNIFIED DUAL-PHASE PIPELINE EXTRACTOR
# ==============================================================================

def extract_all_candidates(
    faa_path: Optional[Union[str, Path]] = None,
    fna_path: Optional[Union[str, Path]] = None,
    organism_prefix: str = "PLS47",
    min_len: int = 5,
    max_len: int = 100
) -> Iterator[Dict[str, Any]]:
    """
    Chains annotated CDS extraction and 6-frame sORF translation into a single
    streamlined generator.
    """
    # 1. Phase 1: Annotated CDS
    if faa_path and Path(faa_path).exists():
        yield from extract_annotated_cds(
            faa_path=faa_path,
            organism_prefix=organism_prefix,
            min_len=min_len,
            max_len=max_len
        )

    # 2. Phase 2: Cryptic sORF 6-Frame
    if fna_path and Path(fna_path).exists():
        yield from extract_six_frame_sorfs(
            fna_path=fna_path,
            organism_prefix=organism_prefix,
            min_len=min_len,
            max_len=max_len
        )


# ==============================================================================
# 5. IN-MEMORY CUSTOM FASTA STREAMING & AUTO-DETECTION
# ==============================================================================

def parse_fasta_stream(fasta_text: str) -> Iterator[Tuple[str, str, str]]:
    """
    Parses multi-line or single-record FASTA formatted text completely in-memory.

    Yields:
        (header_id, clean_sequence, full_header_description)
    """
    current_id: Optional[str] = None
    current_desc: Optional[str] = None
    current_seq_chunks: list = []

    for raw_line in fasta_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith(">"):
            if current_id is not None:
                full_seq = "".join(current_seq_chunks).upper()
                if full_seq:
                    yield current_id, full_seq, (current_desc or current_id)
            header_content = line[1:].strip()
            parts = header_content.split(maxsplit=1)
            current_id = parts[0] if parts else "unnamed_seq"
            current_desc = header_content
            current_seq_chunks = []
        else:
            if current_id is None:
                # Sequence without header -> assign default ID
                current_id = "Custom_Seq_1"
                current_desc = "Custom input sequence"
            current_seq_chunks.append(line)

    if current_id is not None:
        full_seq = "".join(current_seq_chunks).upper()
        if full_seq:
            yield current_id, full_seq, (current_desc or current_id)


def detect_sequence_type(sample_seqs: List[str]) -> str:
    """
    Auto-detects whether a batch of sequences is nucleotide (DNA) or amino acid (Protein).
    Returns 'nucleotide' or 'protein'.
    """
    if not sample_seqs:
        return "protein"

    nt_chars = set("ACGTNURYKMSWBDHV")
    total_len = 0
    nt_count = 0

    for seq in sample_seqs[:20]:  # Test first 20 sequences
        clean = seq.upper().replace(" ", "").replace("\n", "")
        total_len += len(clean)
        nt_count += sum(1 for ch in clean if ch in nt_chars)

    if total_len > 0 and (nt_count / total_len) >= 0.88:
        return "nucleotide"
    return "protein"


def extract_from_custom_fasta(
    content: str,
    organism_prefix: str = "Custom",
    min_len: int = 5,
    max_len: int = 100
) -> Iterator[Dict[str, Any]]:
    """
    Extracts peptide candidates from an in-memory custom FASTA text (protein .faa or DNA .fna).
    Automatically handles sequence type detection and six-frame sORF translation if DNA.
    """
    records = list(parse_fasta_stream(content))
    if not records:
        return

    seq_type = detect_sequence_type([r[1] for r in records])

    if seq_type == "protein":
        for seq_id, raw_seq, desc in records:
            clean_seq = raw_seq.strip().upper()
            if clean_seq.endswith("*"):
                clean_seq = clean_seq[:-1]

            seq_len = len(clean_seq)
            if not (min_len <= seq_len <= max_len):
                continue

            if set(clean_seq) - VALID_AA_SET:
                continue

            clean_id = seq_id.replace("|", "_").replace(".", "_")
            formatted_id = f"{organism_prefix}_{clean_id}_{seq_len}aa"
            yield {
                "id": formatted_id,
                "sequence": clean_seq,
                "source": "Custom_CDS",
                "length": seq_len,
                "description": desc
            }
    else:
        # Nucleotide -> 6-Frame sORF translation in-memory
        for seq_id, dna_seq, desc in records:
            fwd_dna_str = dna_seq.strip().upper()
            rev_dna_str = str(Seq(fwd_dna_str).reverse_complement())
            seq_len_nt = len(fwd_dna_str)

            # Forward Frames (+1, +2, +3)
            for frame_offset in range(3):
                frame_label = f"+{frame_offset + 1}"
                sub_seq = fwd_dna_str[frame_offset:]
                n_codons = len(sub_seq) // 3
                start_codon_positions = []

                for codon_idx in range(n_codons):
                    nt_pos = frame_offset + (codon_idx * 3)
                    codon = sub_seq[codon_idx * 3 : (codon_idx + 1) * 3]

                    if codon in TRI_START_CODONS:
                        start_codon_positions.append((codon_idx, nt_pos))
                    elif codon in STOP_CODONS:
                        for s_idx, s_nt_pos in start_codon_positions:
                            orf_aa_len = codon_idx - s_idx
                            if min_len <= orf_aa_len <= max_len:
                                orf_nt = fwd_dna_str[s_nt_pos : nt_pos + 3]
                                try:
                                    translated_peptide = str(Seq(orf_nt).translate(table=11, cds=True))
                                except Exception:
                                    continue
                                if not (set(translated_peptide) - VALID_AA_SET):
                                    end_nt_pos = nt_pos + 3
                                    clean_id = seq_id.replace("|", "_").replace(".", "_")
                                    orf_id = (
                                        f"{organism_prefix}_{clean_id}_sORF_F{frame_label}_"
                                        f"{s_nt_pos + 1}_{end_nt_pos}_{orf_aa_len}aa"
                                    )
                                    yield {
                                        "id": orf_id,
                                        "sequence": translated_peptide,
                                        "source": "Custom_sORF",
                                        "length": orf_aa_len,
                                        "frame": frame_label,
                                        "strand": "forward",
                                        "start": s_nt_pos + 1,
                                        "end": end_nt_pos
                                    }
                        start_codon_positions = []

            # Reverse Frames (-1, -2, -3)
            for frame_offset in range(3):
                frame_label = f"-{frame_offset + 1}"
                sub_seq = rev_dna_str[frame_offset:]
                n_codons = len(sub_seq) // 3
                start_codon_positions = []

                for codon_idx in range(n_codons):
                    nt_pos_rev = frame_offset + (codon_idx * 3)
                    codon = sub_seq[codon_idx * 3 : (codon_idx + 1) * 3]

                    if codon in TRI_START_CODONS:
                        start_codon_positions.append((codon_idx, nt_pos_rev))
                    elif codon in STOP_CODONS:
                        for s_idx, s_nt_pos in start_codon_positions:
                            orf_aa_len = codon_idx - s_idx
                            if min_len <= orf_aa_len <= max_len:
                                orf_nt = rev_dna_str[s_nt_pos : nt_pos_rev + 3]
                                try:
                                    translated_peptide = str(Seq(orf_nt).translate(table=11, cds=True))
                                except Exception:
                                    continue
                                if not (set(translated_peptide) - VALID_AA_SET):
                                    orig_start = seq_len_nt - (nt_pos_rev + 3) + 1
                                    orig_end = seq_len_nt - s_nt_pos
                                    clean_id = seq_id.replace("|", "_").replace(".", "_")
                                    orf_id = (
                                        f"{organism_prefix}_{clean_id}_sORF_F{frame_label}_"
                                        f"{orig_start}_{orig_end}_{orf_aa_len}aa"
                                    )
                                    yield {
                                        "id": orf_id,
                                        "sequence": translated_peptide,
                                        "source": "Custom_sORF",
                                        "length": orf_aa_len,
                                        "frame": frame_label,
                                        "strand": "reverse",
                                        "start": orig_start,
                                        "end": orig_end
                                    }
                        start_codon_positions = []

