"""
Data Loader Module for the KONECT moreno_oz Friendship Network.
Handles acquisition, validation, extraction, and raw ingestion of network records.
"""

import os
import tarfile
import urllib.request
from pathlib import Path
from typing import Tuple, List
import pandas as pd

from config.experiment_config import DatasetConfig, RAW_DATA_DIR


class DataLoader:
    """Manages downloading, extracting, and loading the moreno_oz dataset."""

    def __init__(self, config: DatasetConfig = None):
        self.config = config or DatasetConfig()
        self.raw_data_path = Path(self.config.raw_data_file)
        self.raw_dir = Path(RAW_DATA_DIR)

    def ensure_dataset(self) -> Path:
        """
        Ensures the dataset exists on disk.
        If not extracted, attempts to extract from local archives or download from KONECT.
        """
        if self.raw_data_path.exists() and self.raw_data_path.stat().st_size > 0:
            return self.raw_data_path

        # Check for local tar.bz2 in raw data directory
        archive_path = self.raw_dir / self.config.raw_archive_name
        
        # Check potential user uploaded archive location if raw directory archive doesn't exist
        if not archive_path.exists():
            # Check user uploaded folder if accessible
            uploaded_dir = Path(r"C:\Users\nandi\.gemini\antigravity\brain\dcefa59c-bb6d-40e8-acbb-c26318c2f106\.user_uploaded")
            if uploaded_dir.exists():
                for candidate in uploaded_dir.glob("*.bz2"):
                    archive_path = candidate
                    break

        if archive_path.exists():
            print(f"[DataLoader] Extracting archive from: {archive_path}")
            with tarfile.open(archive_path, "r:bz2") as tar:
                tar.extractall(self.raw_dir)
        else:
            print(f"[DataLoader] Downloading dataset from KONECT: {self.config.konect_url}")
            os.makedirs(self.raw_dir, exist_ok=True)
            archive_dest = self.raw_dir / self.config.raw_archive_name
            try:
                urllib.request.urlretrieve(self.config.konect_url, archive_dest)
                with tarfile.open(archive_dest, "r:bz2") as tar:
                    tar.extractall(self.raw_dir)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to acquire moreno_oz dataset from {self.config.konect_url}. "
                    f"Error: {e}"
                )

        if not self.raw_data_path.exists():
            raise FileNotFoundError(
                f"Expected data file not found after extraction: {self.raw_data_path}"
            )
        return self.raw_data_path

    def load_raw_edges(self) -> pd.DataFrame:
        """
        Reads out.moreno_oz_oz and returns a cleaned DataFrame of directed edge interactions.
        Columns: ['source', 'target', 'weight']
        """
        file_path = self.ensure_dataset()
        edges: List[Tuple[int, int, float]] = []

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line_idx, line in enumerate(f, start=1):
                stripped = line.strip()
                if not stripped or stripped.startswith("%"):
                    continue
                parts = stripped.split()
                if len(parts) >= 3:
                    try:
                        u = int(parts[0])
                        v = int(parts[1])
                        w = float(parts[2])
                        edges.append((u, v, w))
                    except ValueError as err:
                        raise ValueError(
                            f"Malformed record at line {line_idx} in {file_path}: '{line}'"
                        ) from err
                else:
                    raise ValueError(
                        f"Insufficient columns at line {line_idx} in {file_path}: '{line}'"
                    )

        df = pd.DataFrame(edges, columns=["source", "target", "weight"])
        return df

    def get_dataset_metadata(self) -> dict:
        """Reads metadata files if present and returns summary dictionary."""
        meta_file = Path(self.config.meta_data_file)
        meta_dict = {}
        if meta_file.exists():
            with open(meta_file, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta_dict[k.strip()] = v.strip()
        return meta_dict
