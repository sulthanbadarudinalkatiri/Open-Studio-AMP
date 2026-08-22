import random
import pytest
from src.filters import (
    evaluate_peptide,
    evaluate_peptide_batch,
    _evaluate_peptide_fast,
    FilterConfig,
)

AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

POSITIVE_CONTROLS = [
    ("Pos_Nisin_A", "ITSISLCTPGCKTGALMGCNMKTATCHCSIHVSK"),
    ("Pos_Pediocin_PA1", "KYYGNGVTCGKHSCSVDWGKATTCIINNGAMAWATGGHQGNHKC"),
    ("Pos_Lactoferricin_B", "FKCRRWQWRMKKLGAPSITCVRRAF"),
]

NEGATIVE_CONTROLS = [
    ("Neg_Casein_CMP", "MAIPPKKNQDKTEIPTINTI"),
    ("Neg_Melittin", "GIGAVLKVLTTGLPALISWIKRKRQQ"),
    ("Neg_Unstable_Acidic", "PSDDPEEDDSEEP"),
]

LOCAL_CONTROLS = [
    ("Local_Tempeh_Glycinin", "VLIVPN"),
    ("Local_Casocidin", "KTKLTEEEKNRLRE"),
    (
        "Local_Lysozyme",
        "RHGLDNYRGYSLGNWVCAAKFESNFNTQATNRNTDGSTDYGILQINSRWWCNDGRTPGSRNLCNIPCSALLSSDITASVNCAKKIVSDGNGMNAWVAWRNRCKGTDVQAWIRGCRL"
    ),
]


class TestParityFastPath:
    """
    Validates 100% full dictionary equality between the reference evaluate_peptide
    implementation and the optimized fast-path engine.
    """

    def test_positive_controls_parity(self):
        config_tropical = FilterConfig.tropical_preset()
        config_permissive = FilterConfig.permissive_amp_preset()

        for seq_id, seq in POSITIVE_CONTROLS:
            for cfg in (config_tropical, config_permissive):
                ref = evaluate_peptide(seq_id, seq, config=cfg)
                fast = _evaluate_peptide_fast(seq_id, seq, config=cfg)
                assert ref == fast, f"Mismatch on {seq_id} with preset"

    def test_negative_controls_parity(self):
        config = FilterConfig.tropical_preset()
        for seq_id, seq in NEGATIVE_CONTROLS:
            ref = evaluate_peptide(seq_id, seq, config=config)
            fast = _evaluate_peptide_fast(seq_id, seq, config=config)
            assert ref == fast, f"Mismatch on negative control {seq_id}"

    def test_local_controls_parity(self):
        config = FilterConfig.tropical_preset()
        for seq_id, seq in LOCAL_CONTROLS:
            ref = evaluate_peptide(seq_id, seq, config=config)
            fast = _evaluate_peptide_fast(seq_id, seq, config=config)
            assert ref == fast, f"Mismatch on local control {seq_id}"

    def test_two_thousand_seeded_random_sequences_parity(self):
        """Tests 2,000 seeded pseudo-random sequences (length 5-100) for exact byte/dict equality."""
        config = FilterConfig.tropical_preset()
        rng = random.Random(42)

        peptides = []
        for i in range(2000):
            length = rng.randint(5, 100)
            seq = "".join(rng.choices(AMINO_ACIDS, k=length))
            # Occasionally add stop codons or whitespace to test edge-case parity
            if i % 100 == 0:
                seq = f" {seq}* "
            elif i % 250 == 0:
                seq = seq[:3]  # triggers length bounds failure
            peptides.append((f"SEEDED_{i:04d}", seq))

        # Check individual evaluation parity
        for seq_id, seq in peptides:
            ref = evaluate_peptide(seq_id, seq, config=config)
            fast = _evaluate_peptide_fast(seq_id, seq, config=config)
            assert ref == fast, f"Mismatch on random sequence {seq_id}"

        # Check batch evaluation parity
        batch_results = evaluate_peptide_batch(peptides, config=config, parallel=False)
        assert len(batch_results) == len(peptides)
        for i, (seq_id, seq) in enumerate(peptides):
            ref = evaluate_peptide(seq_id, seq, config=config)
            assert batch_results[i] == ref, f"Batch mismatch on {seq_id}"
