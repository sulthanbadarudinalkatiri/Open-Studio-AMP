import logging
import gzip
import hashlib

logger = logging.getLogger(__name__)
import os
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import requests
from Bio import Entrez

# ==============================================================================
# 1. CONFIGURATION & CREDENTIALS
# ==============================================================================

DEFAULT_EMAIL: str = os.getenv("NCBI_EMAIL", "bioresearch@openstudio.org")
DEFAULT_API_KEY: Optional[str] = os.getenv("NCBI_API_KEY", None)
DEFAULT_ORGANISM_QUERY: str = "Geobacillus thermocatenulatus[Organism] AND latest[filter]"
DEFAULT_ORGANISM_PREFIX: str = "pls47"

# Default maximum decompressed file size cap: 100 MB (safety limit against zip bombs)
DEFAULT_MAX_DECOMPRESSED_BYTES: int = 100 * 1024 * 1024  # 100 MB


# ==============================================================================
# 2. CRYPTOGRAPHIC CHECKSUM HELPER
# ==============================================================================

def compute_sha256(file_path: Union[str, Path], chunk_size: int = 65536) -> str:
    """
    Computes the SHA256 cryptographic hash of a local file in streaming blocks.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Cannot compute SHA256 for non-existent file: {path}")

    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


# ==============================================================================
# 3. FETCHER CORE CLASS
# ==============================================================================

class GenomeFetcher:
    """
    Manages downloading, caching, SHA256 checksum verification, and bounded
    decompression of extremophile genome datasets.
    """

    def __init__(
        self,
        raw_data_dir: str = "data/raw",
        email: str = DEFAULT_EMAIL,
        api_key: str = DEFAULT_API_KEY,
        max_decompressed_bytes: int = DEFAULT_MAX_DECOMPRESSED_BYTES
    ):
        self.raw_data_dir = Path(raw_data_dir)
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.email = email
        self.api_key = api_key
        self.max_decompressed_bytes = max_decompressed_bytes
        
        Entrez.email = self.email
        if self.api_key:
            Entrez.api_key = self.api_key

    def check_local_cache(self, prefix: str = DEFAULT_ORGANISM_PREFIX) -> Optional[Tuple[Path, Path]]:
        """
        Tier 1: Checks if .fna (genomic) and .faa (protein) already exist locally and are non-empty.
        Also calculates and logs their SHA256 checksums.
        """
        fna_path = self.raw_data_dir / f"{prefix}_genomic.fna"
        faa_path = self.raw_data_dir / f"{prefix}_protein.faa"

        if fna_path.exists() and faa_path.exists():
            if fna_path.stat().st_size > 1000 and faa_path.stat().st_size > 1000:
                fna_sha = compute_sha256(fna_path)
                faa_sha = compute_sha256(faa_path)
                logger.info(f"[CACHE HIT] Found existing raw genome files for '{prefix}':")
                logger.info(f"  - Genomic DNA : {fna_path} ({fna_path.stat().st_size / 1024:.1f} KB) | SHA256: {fna_sha[:16]}...")
                logger.info(f"  - Annotated CDS: {faa_path} ({faa_path.stat().st_size / 1024:.1f} KB) | SHA256: {faa_sha[:16]}...")
                return fna_path, faa_path

        return None

    def _decompress_gzip_with_cap(self, gz_path: Path, target_path: Path) -> int:
        """
        Decompresses a gzip archive while strictly enforcing maximum size cap to
        protect against decompression bomb attacks. Returns total decompressed bytes.
        """
        decompressed_bytes = 0
        try:
            with gzip.open(gz_path, "rb") as f_in:
                with open(target_path, "wb") as f_out:
                    while True:
                        chunk = f_in.read(65536)
                        if not chunk:
                            break
                        decompressed_bytes += len(chunk)
                        if decompressed_bytes > self.max_decompressed_bytes:
                            raise ValueError(
                                f"Decompressed size exceeded safety limit of "
                                f"{self.max_decompressed_bytes / (1024*1024):.1f} MB (possible decompression bomb)."
                            )
                        f_out.write(chunk)
        except Exception:
            if target_path.exists():
                target_path.unlink()
            raise
        return decompressed_bytes

    def _download_and_decompress(
        self,
        url: str,
        target_path: Path,
        timeout: int = 30,
        expected_sha256: Optional[str] = None
    ):
        """
        Downloads a .gz stream, computes archive hash, decompresses with a hard size cap,
        and verifies the decompressed file's SHA256 integrity.
        """
        temp_gz = target_path.with_suffix(".gz")
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        # 1. Stream download and compute archive hash
        gz_hasher = hashlib.sha256()
        with open(temp_gz, "wb") as f_out:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f_out.write(chunk)
                    gz_hasher.update(chunk)

        gz_sha256 = gz_hasher.hexdigest()
        logger.info(f"  [INTEGRITY] Archive Downloaded: {temp_gz.name} | SHA256: {gz_sha256[:16]}...")

        # 2. Decompress gzip with bounded size cap
        try:
            decompressed_bytes = self._decompress_gzip_with_cap(temp_gz, target_path)
        finally:
            if temp_gz.exists():
                temp_gz.unlink()

        # 3. Compute and verify SHA256 of final decompressed file
        final_sha256 = compute_sha256(target_path)
        logger.info(f"  [INTEGRITY] Decompressed File : {target_path.name} ({decompressed_bytes / 1024:.1f} KB) | SHA256: {final_sha256[:16]}...")

        if expected_sha256:
            if final_sha256.lower() != expected_sha256.lower():
                target_path.unlink()
                raise ValueError(
                    f"SHA256 checksum mismatch for {target_path.name}!\n"
                    f"Expected: {expected_sha256}\n"
                    f"Observed: {final_sha256}"
                )
            logger.info(f"  [VERIFIED] Checksum matched expected SHA256 digest.")

    def fetch_from_ncbi(
        self,
        organism_query: str = DEFAULT_ORGANISM_QUERY,
        prefix: str = DEFAULT_ORGANISM_PREFIX,
        timeout: int = 30,
        expected_fna_sha256: Optional[str] = None,
        expected_faa_sha256: Optional[str] = None
    ) -> Tuple[Path, Path]:
        """
        Tier 2: Queries NCBI Entrez Assembly database and downloads genomic .fna and protein .faa.
        Performs SHA256 checksum verification and decompression size bounding.
        """
        logger.info(f"[NCBI QUERY] Searching NCBI Assembly for '{organism_query}'...")
        handle = Entrez.esearch(db="assembly", term=organism_query, retmax=5)
        search_results = Entrez.read(handle)
        handle.close()

        id_list = search_results.get("IdList", [])
        if not id_list:
            handle = Entrez.esearch(db="assembly", term="Geobacillus thermocatenulatus", retmax=5)
            search_results = Entrez.read(handle)
            handle.close()
            id_list = search_results.get("IdList", [])

        if not id_list:
            raise RuntimeError(f"No assembly found on NCBI for query: {organism_query}")

        assembly_id = id_list[0]
        summary_handle = Entrez.esummary(db="assembly", id=assembly_id)
        summary_rec = Entrez.read(summary_handle)
        summary_handle.close()

        doc = summary_rec["DocumentSummarySet"]["DocumentSummary"][0]
        ftp_path = doc.get("FtpPath_RefSeq") or doc.get("FtpPath_GenBank")
        if not ftp_path:
            raise RuntimeError(f"No FTP path found in assembly record {assembly_id}")

        # Convert ftp:// to https://
        https_base_url = ftp_path.replace("ftp://", "https://")
        if not https_base_url.endswith("/"):
            https_base_url += "/"

        assembly_name = Path(ftp_path).name
        fna_filename = f"{assembly_name}_genomic.fna.gz"
        faa_filename = f"{assembly_name}_protein.faa.gz"

        fna_url = https_base_url + fna_filename
        faa_url = https_base_url + faa_filename

        target_fna = self.raw_data_dir / f"{prefix}_genomic.fna"
        target_faa = self.raw_data_dir / f"{prefix}_protein.faa"

        # Download, decompress with size cap, and verify FNA
        logger.info(f"[DOWNLOADING] Fetching genomic DNA: {fna_url}")
        self._download_and_decompress(fna_url, target_fna, timeout=timeout, expected_sha256=expected_fna_sha256)

        # Download, decompress with size cap, and verify FAA
        logger.info(f"[DOWNLOADING] Fetching annotated CDS: {faa_url}")
        self._download_and_decompress(faa_url, target_faa, timeout=timeout, expected_sha256=expected_faa_sha256)

        logger.info(f"[SUCCESS] Downloaded, verified, and cached genome files for '{prefix}' successfully.")
        return target_fna, target_faa

    def get_genome_files(
        self,
        prefix: str = DEFAULT_ORGANISM_PREFIX,
        organism_query: str = DEFAULT_ORGANISM_QUERY
    ) -> Tuple[Path, Path]:
        """
        Main entrypoint: checks local cache first, downloads from NCBI if absent.
        """
        cached = self.check_local_cache(prefix)
        if cached:
            return cached

        try:
            return self.fetch_from_ncbi(organism_query=organism_query, prefix=prefix)
        except Exception as e:
            logger.info(f"[WARNING] NCBI download encountered error: {e}")
            cached_retry = self.check_local_cache(prefix)
            if cached_retry:
                return cached_retry
            raise RuntimeError(
                f"Failed to fetch genome files from NCBI and no local cache found in {self.raw_data_dir}. "
                f"Original error: {e}"
            )


# ==============================================================================
# 4. CONVENIENCE FUNCTION
# ==============================================================================

def fetch_extremophile_genome(
    prefix: str = DEFAULT_ORGANISM_PREFIX,
    raw_data_dir: str = "data/raw",
    max_decompressed_bytes: int = DEFAULT_MAX_DECOMPRESSED_BYTES
) -> Tuple[Path, Path]:
    """
    Helper function to get or download the PLS47 genome files with integrity checks.
    """
    fetcher = GenomeFetcher(raw_data_dir=raw_data_dir, max_decompressed_bytes=max_decompressed_bytes)
    return fetcher.get_genome_files(prefix=prefix)
