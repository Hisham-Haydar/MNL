from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Iterable

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ANALYZER_SCRIPT = PROJECT_ROOT / "scripts" / "analyze_dcm_results.py"


def run_analyzer(source: str, genders: Iterable[str], variant: str) -> None:
    """Invoke analyze_dcm_results.py for the provided genders/variant."""
    genders = list(genders)
    if not ANALYZER_SCRIPT.exists():
        LOGGER.warning("Analyzer script not found at %s; skipping auto-report.", ANALYZER_SCRIPT)
        return
    base_cmd = [
        sys.executable,
        str(ANALYZER_SCRIPT),
        "--source",
        source,
        "--variant",
        variant,
    ]
    for gender in genders:
        cmd = base_cmd + ["--genders", gender]
        try:
            LOGGER.info("Running analyzer (%s, %s, %s)", source, gender, variant)
            subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)
        except subprocess.CalledProcessError as exc:
            LOGGER.warning("Analyzer failed for %s/%s: %s", source, gender, exc)
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.warning("Unexpected analyzer error for %s/%s: %s", source, gender, exc)
