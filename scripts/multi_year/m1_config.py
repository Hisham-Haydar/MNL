"""
m1_config.py
============

Stage M1 — YAML configuration loader.

Loads a stage-config YAML file (e.g. config/multi_year/fr_p3a_stage_m1.yaml)
and provides a typed StageConfig object consumed by all reusable M1 scripts.

The --config p3a shortcut resolves to the canonical France P3a YAML at:
    config/multi_year/fr_p3a_stage_m1.yaml

Reference: docs/JMP_multi_year_stage_M1_generalization_report_v1.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

# ---------------------------------------------------------------------------
# Shortcut map: --config <name> resolves to this YAML path (relative to REPO)
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[2]

_SHORTCUT_MAP: Dict[str, str] = {
    "p2":  "config/multi_year/fr_p3a_stage_m1.yaml",   # P2 uses FR config, years subset
    "p3a": "config/multi_year/fr_p3a_stage_m1.yaml",
    "p3b": "config/multi_year/fr_p3a_stage_m1.yaml",
    "p3b_robustness": "config/multi_year/fr_p3a_stage_m1.yaml",
    "p4":  "config/multi_year/fr_p3a_stage_m1.yaml",
}


def resolve_config_path(
    config_name: Optional[str] = None,
    stage_config_path: Optional[str] = None,
) -> Path:
    """
    Return the Path to the stage-config YAML.

    Priority:
      1. --stage-config <path>  (explicit path, absolute or relative to cwd)
      2. --config <name>        (shortcut → REPO/config/multi_year/...)

    Raises ValueError if neither is provided.
    """
    if stage_config_path:
        p = Path(stage_config_path)
        if not p.is_absolute():
            p = Path.cwd() / p
        return p
    if config_name:
        key = config_name.lower()
        rel = _SHORTCUT_MAP.get(key)
        if rel is None:
            raise ValueError(
                f"No config shortcut registered for '--config {config_name}'. "
                f"Known shortcuts: {list(_SHORTCUT_MAP)}. "
                "Use --stage-config to pass an explicit YAML path."
            )
        return REPO / rel
    raise ValueError(
        "Provide either --stage-config <path> or --config <name>."
    )


# ---------------------------------------------------------------------------
# StageConfig — typed wrapper around the raw YAML dict
# ---------------------------------------------------------------------------

class StageConfig:
    """
    Typed accessor for a stage-config YAML.

    All attributes mirror the YAML fields documented in
    config/multi_year/fr_p3a_stage_m1.yaml.
    """

    def __init__(self, raw: Dict[str, Any], yaml_path: Path) -> None:
        self._raw = raw
        self.yaml_path = yaml_path

        # Identity
        self.country_code: str = raw["country_code"]
        self.country_slug: str = raw["country_slug"]
        self.project_label: str = raw["project_label"]
        self.config_name: str = raw["config_name"]

        # Years
        self.years: List[int] = [int(y) for y in raw["years"]]
        raw_year_tags: Dict[Any, Any] = raw["year_tags"]
        self.year_tags: Dict[int, int] = {
            int(k): int(v) for k, v in raw_year_tags.items()
        }
        self.tag_year: Dict[int, int] = {v: k for k, v in self.year_tags.items()}

        # UIDs
        self.uid_base: int = int(raw["uid_base"])

        # Column names
        self.household_id_col: str = raw["household_id_col"]
        self.person_id_col: str = raw["person_id_col"]
        self.raw_household_id_col: str = raw["raw_household_id_col"]
        self.raw_person_id_col: str = raw["raw_person_id_col"]
        self.cluster_id_col: str = raw["cluster_id_col"]
        self.cluster_source_col: str = raw["cluster_source_col"]
        self.raw_id_cols: List[str] = list(raw["raw_id_cols"])

        # Monetary variables
        self.monetary_variables: List[str] = list(raw["monetary_variables"])
        self.variables_excluded_from_deflation: Set[str] = frozenset(
            raw["variables_excluded_from_deflation"]
        )

        # Paths (relative to REPO; scripts resolve with self.repo_path)
        self.processed_root: Path = REPO / raw["processed_root"]
        self.pooled_output_dir: Path = REPO / raw["pooled_output_dir"]
        self.results_dir: Path = REPO / raw["results_dir"]
        self.external_data_dir: Path = REPO / raw["external_data_dir"]
        self.cpi_template_path: Path = REPO / raw["cpi_template_path"]
        self.cpi_final_path: Path = REPO / raw["cpi_final_path"]
        self.input_parquet_dir: Path = REPO / raw["input_parquet_dir"]
        self.input_parquet_patterns: List[str] = list(raw["input_parquet_patterns"])

        # Output file stems
        stems_raw = raw.get("output_file_stems", {})
        slug = self.country_slug
        cfg = self.config_name
        self.stacked_raw_stem: str = stems_raw.get(
            "stacked_raw", f"{slug}_{cfg}_stacked_raw"
        ).format(country_slug=slug, config_name=cfg)
        self.harmonised_stem: str = stems_raw.get(
            "harmonised", f"{slug}_{cfg}_harmonised"
        ).format(country_slug=slug, config_name=cfg)

        # Expected counts
        expected_rows_raw: Dict[str, Any] = raw.get("expected_row_counts", {})
        self.expected_row_counts: Dict[str, int] = {
            k: int(v) for k, v in expected_rows_raw.items()
        }
        raw_overlaps: Dict[str, Any] = raw.get("expected_overlap_counts", {})
        self.expected_overlap_counts: Dict[Tuple[int, int], int] = {}
        for key_str, count in raw_overlaps.items():
            parts = str(key_str).split("-")
            if len(parts) == 2:
                self.expected_overlap_counts[(int(parts[0]), int(parts[1]))] = int(count)

        self.p3a_overlap_tolerance: int = int(raw.get("p3a_overlap_tolerance", 200))

        ils_range = raw.get("ils_dispy_real_range", {})
        self.ils_dispy_real_min: float = float(ils_range.get("min", 25000.0))
        self.ils_dispy_real_max: float = float(ils_range.get("max", 55000.0))

        # Identity validation thresholds
        thr_raw: Dict[str, Any] = raw.get("identity_validation_thresholds", {})
        self.identity_thresholds: Dict[str, float] = {
            "sex_stability_min":    float(thr_raw.get("sex_stability_min",    0.9990)),
            "age_progression_min":  float(thr_raw.get("age_progression_min",  0.9950)),
            "suspicious_warn_max":  float(thr_raw.get("suspicious_warn_max",  0.0020)),
            "suspicious_block_max": float(thr_raw.get("suspicious_block_max", 0.0100)),
            "hh_continuity_min":    float(thr_raw.get("hh_continuity_min",    0.9700)),
        }

        # Special gates
        gates = raw.get("special_gates", {})
        self.p3b_isf_memo_path: Path = REPO / gates.get(
            "p3b_isf_memo_path", "Results/M1_ISF_tpr_comparability_check_2018.md"
        )
        self.p3b_isf_proceed_phrase: str = gates.get(
            "p3b_isf_proceed_phrase", "proceed with p3b"
        )
        blocked_raw: Dict[str, Any] = gates.get("blocked_configs", {})
        self.blocked_configs: Dict[str, str] = {
            k: str(v).strip() for k, v in blocked_raw.items()
        }

    # Convenience helpers --------------------------------------------------

    def stacked_raw_path(self) -> Path:
        return self.pooled_output_dir / f"{self.stacked_raw_stem}.parquet"

    def harmonised_path(self) -> Path:
        return self.pooled_output_dir / f"{self.harmonised_stem}.parquet"

    def expected_year_tags(self) -> Set[int]:
        return {self.year_tags[y] for y in self.years if y in self.year_tags}

    def config_tags_for(self, config_key: str) -> Optional[Set[int]]:
        """
        Return the expected year_tag set for a given config key
        (looked up from expected_row_counts keys + years mapping).
        Implemented as a simple per-config lookup; the canonical definition
        lives in the YAML years field for the config's own file.
        For the primary config this always returns expected_year_tags().
        For sub-configs (p2, p3b) it returns None (caller must handle).
        """
        if config_key == self.config_name:
            return self.expected_year_tags()
        return None

    def expected_rows_for(self, config_key: str) -> Optional[int]:
        return self.expected_row_counts.get(config_key)

    def __repr__(self) -> str:
        return (
            f"StageConfig("
            f"country={self.country_code}, config={self.config_name}, "
            f"years={self.years}, uid_base={self.uid_base})"
        )


# ---------------------------------------------------------------------------
# Public loader
# ---------------------------------------------------------------------------

def load_stage_config(
    config_name: Optional[str] = None,
    stage_config_path: Optional[str] = None,
) -> StageConfig:
    """
    Load and return a StageConfig.

    Parameters
    ----------
    config_name : str, optional
        Shortcut name (e.g. 'p3a').  Resolves to the canonical YAML.
    stage_config_path : str, optional
        Explicit path to a YAML file.  Takes priority over config_name.

    Returns
    -------
    StageConfig
    """
    yaml_path = resolve_config_path(config_name, stage_config_path)

    if not yaml_path.exists():
        raise FileNotFoundError(
            f"Stage-config YAML not found: {yaml_path}\n"
            "Check --stage-config path or ensure the shortcut YAML exists."
        )

    with open(yaml_path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if not isinstance(raw, dict):
        raise ValueError(
            f"Stage-config YAML must be a mapping at the top level: {yaml_path}"
        )

    return StageConfig(raw, yaml_path)