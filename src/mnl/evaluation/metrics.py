"""Common evaluation metrics for discrete-choice models."""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.discrete.discrete_model import MNLogitResults


def log_likelihood(result: MNLogitResults) -> float:
    """Return the maximized log-likelihood from a fitted MNLogit result."""
    return float(result.llf)


def prediction_accuracy(choices: pd.Series, probabilities: np.ndarray) -> float:
    """Compute hit rate by selecting the highest-probability alternative."""
    if len(choices) != len(probabilities):
        raise ValueError("Choices and probabilities must have the same length.")

    predicted = probabilities.argmax(axis=1)
    return float(np.mean(predicted == choices.to_numpy()))

