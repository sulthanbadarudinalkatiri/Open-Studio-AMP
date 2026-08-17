"""
Unit Tests for In-Memory Custom FASTA Ingestion Subsystem
Module: tests/test_custom_ingestion.py
"""

import pytest
import pandas as pd
from src.extractor import (
    parse_fasta_stream,
    detect_sequence_type,
    extract_from_custom_fasta
)
from src.filters import evaluate_peptide_batch, FilterConfig


class TestCustomFastaParsingAndTypeDetection:
    def test_parse_fasta_stream_multiline(self):
        sample_fasta = """
        >Peptide_1 First sample description
        MGGKV
        TIQNLK
        >Peptide_2 Second sample
        LFIHLHRLIPNELK
        """
        records = list(parse_fasta_stream(sample_fasta))
        assert len(records) == 2
        assert records[0][0] == "Peptide_1"
        assert records[0][1] == "MGGKVTIQNLK"
        assert "First sample description" in records[0][2]
        assert records[1][0] == "Peptide_2"
        assert records[1][1] == "LFIHLHRLIPNELK"

    def test_parse_raw_sequence_without_header(self):
        raw_seq = "MGGERVTIQNLKIVKVDPERNLLLIKGNVPGPRKGLVIVKSAVKAAKKAK"
        records = list(parse_fasta_stream(raw_seq))
        assert len(records) == 1
        assert records[0][1] == raw_seq

    def test_detect_sequence_type_protein(self):
        protein_seqs = [
            "MGGERVTIQNLKIVKVDPERNLLLIKGNVPGPRKGLVIVKSAVKAAKKAK",
            "LFIHLHRLIPNELKKKIVIKKSE",
            "ITSISLCTPGCKTGALMGCNMKTATCHCSIHVSK"
        ]
        assert detect_sequence_type(protein_seqs) == "protein"

    def test_detect_sequence_type_dna(self):
        dna_seqs = [
            "ATGGGCGGAGAGCGCGTGACCATCCAGAACCTGAAGATCGTGAAGGTGGACCCCGAGCGC",
            "TTGTTTATCACCATCTGCACCCCGGGCTGCAAGACCGGCGCGCTGATGGGCTGCAACATG"
        ]
        assert detect_sequence_type(dna_seqs) == "nucleotide"


class TestCustomFastaExtractionAndEvaluation:
    def test_extract_from_custom_protein_fasta(self):
        sample_protein_fasta = """
        >Custom_AMP_01
        MGGERVTIQNLKIVKVDPERNLLLIKGNVPGPRKGLVIVKSAVKAAKKAK
        >Custom_Short_Invalid
        ACD
        >Custom_AMP_02
        LFIHLHRLIPNELKKKIVIKKSE*
        """
        candidates = list(extract_from_custom_fasta(sample_protein_fasta, organism_prefix="UserIso"))
        assert len(candidates) == 2  # Short_Invalid (3aa < 5aa) is filtered
        assert candidates[0]["id"].startswith("UserIso_Custom_AMP_01")
        assert candidates[0]["source"] == "Custom_CDS"
        assert candidates[1]["sequence"] == "LFIHLHRLIPNELKKKIVIKKSE"

    def test_extract_from_custom_dna_fasta_6frame(self):
        # A synthetic DNA fragment containing an ATG start and in-frame stop codon TAA
        sample_dna_fasta = """
        >Synthetic_Contig_1
        CCATGGGCGGAGAGCGCGTGACCATCCAGAACCTGAAGATCGTGAAGGTGGACCCCGAGCGCCTCTAAAG
        """
        candidates = list(extract_from_custom_fasta(sample_dna_fasta, organism_prefix="UserGenome"))
        assert len(candidates) >= 1
        assert any(c["source"] == "Custom_sORF" for c in candidates)

    def test_end_to_end_custom_dataframe_generation(self):
        custom_fasta = """
        >Candidate_A High Score
        MGGERVTIQNLKIVKVDPERNLLLIKGNVPGPRKGLVIVKSAVKAAKKAK
        >Candidate_B Nisin Control
        ITSISLCTPGCKTGALMGCNMKTATCHCSIHVSK
        """
        extracted = list(extract_from_custom_fasta(custom_fasta, organism_prefix="Lab"))
        peptides = [(c["id"], c["sequence"]) for c in extracted]
        evaluated = evaluate_peptide_batch(peptides, FilterConfig.tropical_preset())
        
        df_custom = pd.DataFrame(evaluated)
        df_custom["source"] = [c["source"] for c in extracted]

        assert len(df_custom) == 2
        assert "as35_score" in df_custom.columns
        assert "passed_all_filters" in df_custom.columns
        assert df_custom["passed_all_filters"].all()
