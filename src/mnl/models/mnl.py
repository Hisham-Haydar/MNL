"""Simple MNL estimator wrapper leveraging statsmodels."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogitResults


@dataclass
class MultinomialLogit:
    """Wrapper around `statsmodels` MNLogit for consistent interface."""

    features: Iterable[str]
    choice_column: str

    def fit(self, df: pd.DataFrame) -> MNLogitResults:
        """Fit a multinomial logit model using the provided dataframe."""
        if self.choice_column not in df.columns:
            raise ValueError(f"Choice column `{self.choice_column}` missing from dataframe.")

        for feature in self.features:
            if feature not in df.columns:
                raise ValueError(f"Feature `{feature}` missing from dataframe.")

        y = df[self.choice_column]
        X = sm.add_constant(df[list(self.features)], has_constant="add")
        model = sm.MNLogit(y, X)
        return model.fit(method="newton", maxiter=100, full_output=True, disp=False)

    def predict_probabilities(self, fitted_model: MNLogitResults, df: pd.DataFrame) -> np.ndarray:
        """Compute choice probabilities for new data."""
        X = sm.add_constant(df[list(self.features)], has_constant="add")
        return fitted_model.predict(X)

