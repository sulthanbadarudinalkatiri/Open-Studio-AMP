"""
Unit Tests for UI Sorting, Motif Search, and Smart Label Generation
Module: tests/test_ui_sorting_search.py
"""

import pytest
import pandas as pd
from src.theme import build_smart_label


@pytest.fixture
def sample_candidates_df() -> pd.DataFrame:
    data = [
        {
            "id": "PLS47_sORF_F+1_100_200_fwd_33aa",
            "sequence": "MGGERVTIQNLKIVKVDPERNLLLIKGNVPGPR",
            "length": 33,
            "as35_score": 85.4,
            "aliphatic_index": 120.5,
            "charge_ph6": 3.2,
            "instability_index": 28.4,
            "passed_all_filters": True,
            "source": "sORF"
        },
        {
            "id": "PLS47_CDS_locus_1234_25aa",
            "sequence": "LFIHLHRLIPNELKKKIVIKKSEKK",
            "length": 25,
            "as35_score": 72.1,
            "aliphatic_index": 145.0,
            "charge_ph6": 5.1,
            "instability_index": 35.2,
            "passed_all_filters": True,
            "source": "CDS"
        },
        {
            "id": "PLS47_sORF_F-2_500_650_rev_50aa",
            "sequence": "ITSISLCTPGCKTGALMGCNMKTATCHCSIHVSKAAAKKKRKKRRR",
            "length": 50,
            "as35_score": 91.0,
            "aliphatic_index": 75.2,
            "charge_ph6": 6.8,
            "instability_index": 18.0,
            "passed_all_filters": True,
            "source": "sORF"
        }
    ]
    return pd.DataFrame(data)


class TestCandidateSortingLogic:
    def test_sort_by_score_descending(self, sample_candidates_df):
        sorted_df = sample_candidates_df.sort_values(by="as35_score", ascending=False).reset_index(drop=True)
        assert sorted_df.iloc[0]["id"] == "PLS47_sORF_F-2_500_650_rev_50aa"
        assert sorted_df.iloc[0]["as35_score"] == 91.0
        assert sorted_df.iloc[-1]["as35_score"] == 72.1

    def test_sort_by_aliphatic_index_descending(self, sample_candidates_df):
        sorted_df = sample_candidates_df.sort_values(by="aliphatic_index", ascending=False).reset_index(drop=True)
        assert sorted_df.iloc[0]["id"] == "PLS47_CDS_locus_1234_25aa"
        assert sorted_df.iloc[0]["aliphatic_index"] == 145.0

    def test_sort_by_net_charge_descending(self, sample_candidates_df):
        sorted_df = sample_candidates_df.sort_values(by="charge_ph6", ascending=False).reset_index(drop=True)
        assert sorted_df.iloc[0]["charge_ph6"] == 6.8

    def test_sort_by_length_ascending(self, sample_candidates_df):
        sorted_df = sample_candidates_df.sort_values(by="length", ascending=True).reset_index(drop=True)
        assert sorted_df.iloc[0]["length"] == 25
        assert sorted_df.iloc[-1]["length"] == 50


class TestMotifAndIdSearchLogic:
    def test_search_by_id_substring(self, sample_candidates_df):
        query = "locus_1234"
        id_match = sample_candidates_df["id"].astype(str).str.contains(query, case=False, na=False)
        seq_match = sample_candidates_df["sequence"].astype(str).str.contains(query.upper(), case=False, na=False)
        matched = sample_candidates_df[id_match | seq_match]
        assert len(matched) == 1
        assert matched.iloc[0]["id"] == "PLS47_CDS_locus_1234_25aa"

    def test_search_by_amino_acid_motif(self, sample_candidates_df):
        query = "RKK"
        id_match = sample_candidates_df["id"].astype(str).str.contains(query, case=False, na=False)
        seq_match = sample_candidates_df["sequence"].astype(str).str.contains(query.upper(), case=False, na=False)
        matched = sample_candidates_df[id_match | seq_match]
        assert len(matched) == 1
        assert "RKK" in matched.iloc[0]["sequence"]

    def test_search_by_rank(self, sample_candidates_df):
        sorted_df = sample_candidates_df.sort_values(by="as35_score", ascending=False).reset_index(drop=True)
        import re
        
        # Test '#1'
        query_upper = "#1".upper()
        rank_search = re.search(r'^(?:#|RANK\s*|TOP\s*)?(\d+)$', query_upper)
        assert rank_search is not None
        rank_num = int(rank_search.group(1))
        assert rank_num == 1
        assert sorted_df.iloc[rank_num - 1]["id"] == "PLS47_sORF_F-2_500_650_rev_50aa"

        # Test 'Rank 2'
        query_upper2 = "RANK 2".upper()
        rank_search2 = re.search(r'^(?:#|RANK\s*|TOP\s*)?(\d+)$', query_upper2)
        assert rank_search2 is not None
        assert int(rank_search2.group(1)) == 2
        assert sorted_df.iloc[1]["id"] == "PLS47_sORF_F+1_100_200_fwd_33aa"

    def test_search_no_match(self, sample_candidates_df):
        query = "ZZZZZZ"
        id_match = sample_candidates_df["id"].astype(str).str.contains(query, case=False, na=False)
        seq_match = sample_candidates_df["sequence"].astype(str).str.contains(query.upper(), case=False, na=False)
        matched = sample_candidates_df[id_match | seq_match]
        assert len(matched) == 0


class TestSmartLabelFormatting:
    def test_build_smart_label_format(self, sample_candidates_df):
        label = build_smart_label(sample_candidates_df.iloc[0])
        assert "[85.4 | AI:120 | Q:+3.2]" in label
        assert "PLS47_sORF_F+1_100_200_fwd_33aa" in label
