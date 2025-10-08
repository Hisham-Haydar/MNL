"""End-to-end pipeline for estimating a discrete-choice model."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from mnl.config import EstimationConfig
from mnl.data import load_raw_choice_data, prepare_panel_data
from mnl.models import MultinomialLogit
from mnl.evaluation import log_likelihood, prediction_accuracy


def run_estimation_pipeline(
    *,
    config: EstimationConfig,
    raw_data_path: Path | None = None,
    save_probabilities_to: Path | None = None,
) -> dict[str, float]:
    """Execute the default estimation pipeline end-to-end."""
    data_path = raw_data_path or config.data_path
    df = load_raw_choice_data(data_path)
    df = prepare_panel_data(
        df,
        individual_id=config.individual_id_column,
        choice_column=config.choice_column,
        alternative_id=config.alternative_id_column,
    )

    model = MultinomialLogit(features=config.features, choice_column=config.choice_column)
    result = model.fit(df)

    probs = model.predict_probabilities(result, df)
    metrics = {
        "log_likelihood": log_likelihood(result),
        "accuracy": prediction_accuracy(df[config.choice_column], probs),
    }

    if save_probabilities_to:
        probabilities_df = pd.DataFrame(probs, columns=result.model.endog_names)
        probabilities_df.to_csv(save_probabilities_to, index=False)

    return metrics


