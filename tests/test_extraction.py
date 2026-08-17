import gzip
import hashlib
import tempfile
from pathlib import Path
import pytest
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO

from src.fetcher import GenomeFetcher, compute_sha256
from src.extractor import (
    extract_annotated_cds,
    extract_six_frame_sorfs,
    extract_all_candidates,
    TRI_START_CODONS,
    STOP_CODONS
)
from engine import run_pipeline, VALID_PRESETS, VALID_MODES


# ==============================================================================
# 1. EXTRACTOR UNIT TESTS
# ==============================================================================

class TestExtractorEngine:
    """Tests Phase 1 CDS parsing and Phase 2 Six-Frame sORF translation logic."""

    @pytest.fixture
    def mock_faa_file(self, tmp_path):
        """Creates a mock .faa protein FASTA with diverse length & canonical properties."""
        records = [
            SeqRecord(Seq("MKTATCHCSIHVSK"), id="PROKKA_0001", description="Hypothetical small protein"),  # 14 aa (Valid)
            SeqRecord(Seq("MKF"), id="PROKKA_0002", description="Too short"),  # 3 aa (< 5, Invalid)
            SeqRecord(Seq("M" + "A" * 150), id="PROKKA_0003", description="Too long"),  # 151 aa (> 100, Invalid)
            SeqRecord(Seq("MKTATXHCSI*"), id="PROKKA_0004", description="Non-canonical X"),  # Invalid char
            SeqRecord(Seq("ITSISLCTPGCKTGALMGCNMKTATCHCSIHVSK*"), id="PROKKA_0005", description="Nisin-like CDS*")  # 34 aa (Valid)
        ]
        faa_path = tmp_path / "test_proteins.faa"
        SeqIO.write(records, str(faa_path), "fasta")
        return faa_path

    @pytest.fixture
    def mock_fna_file(self, tmp_path):
        """
        Creates a mock genomic .fna with explicit ATG, GTG, and TTG forward and reverse ORFs.
        """
        # Forward:
        # Frame +1: ATG (0) -> AAA TTT (3,6) -> TAA (9) => aa: MKF (len 3, too short if min=5)
        # Followed by a valid 10 aa ORF starting with GTG:
        # GTG GCG GCG GCG GCG GCG GCG GCG GCG GCG TAG => aa: VAAAAAAAAA (10 aa)
        # Followed by a valid 6 aa ORF starting with TTG:
        # TTG GCT GCT GCT GCT GCT TGA => aa: LAAAAA (6 aa)
        fwd_seq = "ATGAAATTCTAAGTGGCGGCGGCGGCGGCGGCGGCGGCGGCGTAGTTGGCTGCTGCTGCTGCTTGA"
        # Reverse complement will also contain valid frames
        records = [
            SeqRecord(Seq(fwd_seq), id="Contig_01", description="Synthetic Contig")
        ]
        fna_path = tmp_path / "test_genomic.fna"
        SeqIO.write(records, str(fna_path), "fasta")
        return fna_path

    def test_extract_annotated_cds_filtering(self, mock_faa_file):
        results = list(extract_annotated_cds(mock_faa_file, organism_prefix="PLS47", min_len=5, max_len=100))

        # Only PROKKA_0001 (14 aa) and PROKKA_0005 (34 aa) should pass
        assert len(results) == 2
        ids = [r["id"] for r in results]
        assert "PLS47_CDS_PROKKA_0001_14aa" in ids[0] or "PLS47_CDS_PROKKA_0001_14aa" in ids[1]
        assert "PLS47_CDS_PROKKA_0005_34aa" in ids[0] or "PLS47_CDS_PROKKA_0005_34aa" in ids[1]

        for r in results:
            assert r["source"] == "CDS"
            assert 5 <= r["length"] <= 100
            assert "*" not in r["sequence"]
            assert "X" not in r["sequence"]

    def test_extract_six_frame_sorfs_tri_start(self, mock_fna_file):
        results = list(extract_six_frame_sorfs(mock_fna_file, organism_prefix="PLS47", min_len=5, max_len=100))
        assert len(results) >= 2
        sequences = [r["sequence"] for r in results]

        # Verify that prokaryotic Table 11 initiator decoding translates GTG/TTG to M
        assert any(s == "MAAAAAAAAA" and len(s) == 10 for s in sequences)
        assert any(s == "MAAAAA" and len(s) == 6 for s in sequences)
        assert all(s.startswith("M") for s in sequences)

        # Verify ID schema format
        for r in results:
            assert r["id"].startswith("PLS47_sORF_F")
            assert r["source"] == "sORF"
            assert 5 <= r["length"] <= 100
            assert r["strand"] in ["forward", "reverse"]

    def test_extract_all_candidates_unified(self, mock_faa_file, mock_fna_file):
        all_results = list(extract_all_candidates(faa_path=mock_faa_file, fna_path=mock_fna_file, organism_prefix="PLS47"))
        
        sources = {r["source"] for r in all_results}
        assert "CDS" in sources
        assert "sORF" in sources
        assert len(all_results) >= 4


# ==============================================================================
# 2. FETCHER CACHE, SHA256 & DECOMPRESSION SAFETY TESTS
# ==============================================================================

class TestGenomeFetcherSecurityAndIntegrity:
    """Tests local cache detection, SHA256 checksums, and decompression size caps."""

    def test_local_cache_hit(self, tmp_path):
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        
        fna_file = raw_dir / "testorg_genomic.fna"
        faa_file = raw_dir / "testorg_protein.faa"

        # Create mock files > 1000 bytes
        fna_file.write_text(">contig1\n" + "ACGT" * 500)
        faa_file.write_text(">prot1\n" + "MKVAL" * 300)

        fetcher = GenomeFetcher(raw_data_dir=str(raw_dir))
        cached = fetcher.check_local_cache(prefix="testorg")

        assert cached is not None
        cached_fna, cached_faa = cached
        assert cached_fna == fna_file
        assert cached_faa == faa_file

    def test_compute_sha256_accuracy(self, tmp_path):
        test_file = tmp_path / "sample.txt"
        test_file.write_bytes(b"OpenStudioAMPSecurityVerification2026")
        
        expected_hash = hashlib.sha256(b"OpenStudioAMPSecurityVerification2026").hexdigest()
        observed_hash = compute_sha256(test_file)
        
        assert observed_hash == expected_hash

    def test_decompression_size_cap_defense(self, tmp_path):
        """
        Verifies that exceeding the max_decompressed_bytes threshold aborts decompression
        and cleans up output files to protect against decompression bombs.
        """
        target_fna = tmp_path / "bomb_genomic.fna"
        gz_path = tmp_path / "bomb_genomic.fna.gz"
        
        large_uncompressed_data = b"A" * 20000
        with gzip.open(gz_path, "wb") as f_gz:
            f_gz.write(large_uncompressed_data)

        # Set safety cap to only 5,000 bytes (< 20,000 bytes)
        fetcher = GenomeFetcher(raw_data_dir=str(tmp_path), max_decompressed_bytes=5000)

        with pytest.raises(ValueError, match="Decompressed size exceeded safety limit"):
            fetcher._decompress_gzip_with_cap(gz_path=gz_path, target_path=target_fna)

        # Confirm target file was cleanly deleted on error
        assert not target_fna.exists()


# ==============================================================================
# 3. CLI ARGUMENT WHITELIST VALIDATION TESTS
# ==============================================================================

class TestEngineWhitelistValidation:
    """Tests strict whitelist validation for preset and mode CLI arguments."""

    def test_valid_presets_and_modes(self):
        assert "tropical" in VALID_PRESETS
        assert "permissive" in VALID_PRESETS
        assert "cds" in VALID_MODES
        assert "sorfs" in VALID_MODES
        assert "all" in VALID_MODES

    def test_invalid_preset_rejected(self):
        with pytest.raises(ValueError, match="Invalid preset 'malicious_preset'"):
            run_pipeline(preset="malicious_preset")

    def test_invalid_mode_rejected(self):
        with pytest.raises(ValueError, match="Invalid mode 'dangerous_mode'"):
            run_pipeline(mode="dangerous_mode")
