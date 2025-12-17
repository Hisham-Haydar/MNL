# RURO Pipeline Audit Report

**Date:** 2025-12-13
**Scope:** Pre-MVP Pipeline Cleanup
**Files Audited:**
- `scripts/run_fr_2016_joint_only.ps1` (511 lines)
- `scripts/RURO_estimate_FR.py` (5544+ lines)
- `scripts/RURO_prep_mnl_basic.py` (578 lines)
- `scripts/RURO_post_estimation.py` (2748+ lines)

---

## A) Pipeline Map

### Step-by-Step Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ RURO France 2016 Joint Estimation Pipeline                      │
│ Total Duration: ~2-3 minutes (assumes MNL dataset exists)       │
└─────────────────────────────────────────────────────────────────┘

STAGE 0: Prerequisites (from full pipeline, not in joint-only script)
├─ Input: FR_2016.txt (raw EUROMOD data)
├─ Scripts: france_data_prep.py → RURO_prep.py → RURO_draws.py → RURO_euromod.py → prepare_FR_gsur.py
└─ Output: fr_2016_RURO_mnl.parquet (449,589 rows, long format)

STAGE 1: Estimation (RURO_estimate_FR.py)
├─ Input: fr_2016_RURO_mnl.parquet
├─ Process:
│   ├─ 1a. Load MNL dataset (pd.read_parquet)
│   ├─ 1b. Filter by group (1=singles, 10=couples)
│   ├─ 1c. Precompute data arrays (precompute_data_singles/couples)
│   │   ├─ Extract consumption/leisure (normalized)
│   │   ├─ Extract covariates (age_norm, n_children, educ)
│   │   ├─ Extract opportunity variables (working, gsur, wage)
│   │   ├─ Compute group boundaries for vectorized operations
│   │   └─ Return PrecomputedDataSingles/Couples dataclass
│   ├─ 1d. Set initial parameters (get_initial_theta_joint)
│   ├─ 1e. Optimize using scipy.optimize.minimize
│   │   ├─ Method: L-BFGS-B (with analytical gradient)
│   │   ├─ Objective: fast_neg_ll_with_grad_singles/couples
│   │   ├─ Gradient: Analytical (computed in same function)
│   │   └─ Options: maxiter=2000, ftol=1e-9, gtol=1e-5
│   └─ 1f. Save results to JSON
├─ Output: outputs/estimates/fr/2016/fr_2016_joint.json
│   ├─ theta: [60 params for vw, 48 for fw]
│   ├─ param_names: ["sm.pref.beta_l0", ...]
│   ├─ log_likelihood: scalar
│   ├─ n_function_evals: scalar
│   ├─ n_gradient_evals: scalar
│   ├─ convergence_message: string
│   └─ parameter_bounds: dict
└─ Duration: ~30 seconds (singles) to ~2 minutes (joint)

STAGE 2: Post-Estimation (RURO_post_estimation.py)
├─ Input: fr_2016_joint.json + fr_2016_RURO_mnl.parquet
├─ Process:
│   ├─ 2a. Parse parameters (ParsedParameters class)
│   │   ├─ Identify groups (sm, sf, cou)
│   │   ├─ Identify preference shifters (age_norm, n_children, educ)
│   │   ├─ Identify Box-Cox parameters (theta_l, theta_c)
│   │   └─ Create parameter lookup methods
│   ├─ 2b. Compute fit diagnostics
│   │   ├─ Observed vs predicted participation rates
│   │   ├─ Observed vs predicted mean hours
│   │   └─ By group: sm, sf, cou_m, cou_f
│   ├─ 2c. Compute marginal utility diagnostics
│   │   ├─ MUC (marginal utility of consumption) at chosen alternatives
│   │   ├─ MUL (marginal utility of leisure) at chosen alternatives
│   │   ├─ Count negative violations
│   │   └─ Analyze MUC behavior (positive, diminishing)
│   ├─ 2d. Compute structural elasticities
│   │   ├─ Extract preference parameters
│   │   ├─ Compute approximate elasticities from θ_l, θ_c
│   │   └─ Return dataframe by group
│   ├─ 2e. Generate plots
│   │   ├─ Utility contours (consumption vs leisure, 4 groups)
│   │   ├─ Marginal utility comparison (MUC/MUL by group)
│   │   ├─ Fit comparison (observed vs predicted)
│   │   └─ Parameter significance plots
│   └─ 2f. Generate HTML report
│       ├─ Assemble all sections (stats, diagnostics, plots, params)
│       ├─ Apply styling (CSS with color coding)
│       └─ Write to post_estimation_report.html
├─ Output: outputs/post_estimation/fr/2016/joint/
│   ├─ vw_pooled_post_estimation_report.html
│   ├─ vw_pooled_params.csv
│   ├─ vw_pooled_elasticities.csv
│   ├─ vw_sm_contours.png
│   ├─ vw_sf_contours.png
│   ├─ vw_cou_m_contours.png
│   ├─ vw_cou_f_contours.png
│   ├─ vw_pooled_muc_comparison.png
│   └─ vw_pooled_mul_comparison.png
└─ Duration: ~3 seconds
```

### Key Contracts Between Stages

**RURO_prep_mnl_basic.py → RURO_estimate_FR.py**
- **Output format:** Parquet file with long-format MNL dataset
- **Required columns (singles):**
  - `ruro_id` (str): Individual identifier
  - `ruro_group` (int): 1=singles, 10=couples
  - `draw` (int): 0=observed, 1-99=simulated
  - `c_norm` or `ils_dispy` (float): Consumption (normalized or raw)
  - `l_norm` or `lhw` (float): Leisure (normalized) or hours
  - `age_norm` or `dag` (float): Demeaned age or raw age
  - `n_children` (int): Total children count
  - `educL`, `educH` (float): Education dummies
  - `working`, `working_pt1`, `working_pt2`, `working_ft` (float): Hours indicators
  - `gsur` (float): Unemployment probability
  - `wage` or `yivwg` (float): Observed wage (for vw)
  - `prior` (float): Log RURO prior density
- **Required columns (couples):** Same as singles but with `_m` and `_f` suffixes

**RURO_estimate_FR.py → RURO_post_estimation.py**
- **Output format:** JSON file
- **Required fields:**
  - `theta` (list[float]): Parameter vector
  - `param_names` (list[str]): Parameter names with namespace prefixes
    - Format: `{group}.{component}.{param}` (e.g., `sm.pref.beta_l0`)
  - `log_likelihood` (float): Final LL value
  - `n_function_evals` (int): Optimizer iterations
  - `parameter_bounds` (dict): Bounds used in optimization

---

## B) Duplication & Redundancy Audit

### CRITICAL: Duplicated Functions

#### 1. Box-Cox Transformation (3 copies!)

**Location 1:** `RURO_estimate_FR.py:1191-1246`
```python
def boxcox_transform(x: np.ndarray, theta: float) -> np.ndarray:
    eps = 1e-6
    x = np.clip(x, eps, None)
    if abs(theta) < eps:
        return np.log(x)
    else:
        return (np.power(x, theta) - 1.0) / theta

def d_boxcox_dtheta(x: np.ndarray, theta: float) -> np.ndarray:
    # ... derivative logic

def d_boxcox_dx(x: np.ndarray, theta: float) -> np.ndarray:
    # ... derivative logic
```

**Location 2:** `RURO_estimate_FR.py:2574-2588` (fast versions)
```python
def _fast_boxcox(x: np.ndarray, theta: float) -> np.ndarray:
    if abs(theta) < 1e-6:
        return np.log(x)
    return (np.power(x, theta) - 1.0) / theta

def _fast_d_boxcox_dtheta(x: np.ndarray, theta: float) -> np.ndarray:
    # ... derivative logic (slightly different implementation)
```

**Location 3:** `RURO_post_estimation.py:223-235`
```python
def boxcox_transform(x: Union[float, np.ndarray], theta: float) -> Union[float, np.ndarray]:
    # ... same logic, different signature
```

**Issue:** 3 implementations with subtle differences:
- `boxcox_transform` vs `_fast_boxcox` (different epsilon: 1e-6 vs 1e-6)
- Post-estimation version handles both scalar and array inputs
- Derivative functions duplicated in estimation but not in post-estimation

#### 2. Normalization Constants (2 locations)

**Location 1:** `RURO_estimate_FR.py:90-93`
```python
MEAN_DISPY_NORM = 2500.0
MEAN_LHW_NORM = 35.0
TOTAL_LEISURE_HOURS = 80.0
```

**Location 2:** `RURO_prep_mnl_basic.py:33-36`
```python
MEAN_DISPY_NORM = 2500.0
MEAN_LHW_NORM = 35.0
TOTAL_LEISURE_HOURS = 80.0
```

**Issue:** Magic numbers duplicated. If these need to change (e.g., for different years or countries), they must be updated in both places.

#### 3. Consumption Computation Logic (duplicated for singles/couples)

**Location 1:** `RURO_estimate_FR.py:321-421` (precompute_data_singles)
```python
# CRITICAL FIX: Check if consumption varies within choice sets.
c = None
if "c_norm" in df.columns and not df["c_norm"].isna().all():
    c = df["c_norm"].to_numpy(dtype=np.float64)

# ... 50+ lines checking if consumption varies ...

if c is None:
    # Compute synthetic consumption that varies with earnings
    NET_OF_TAX = 0.60
    base_non_labor = base_ils - NET_OF_TAX * base_yem
    c = base_non_labor[inverse] + NET_OF_TAX * yem
```

**Location 2:** `RURO_estimate_FR.py:580-658` (precompute_data_couples)
```python
# CRITICAL FIX: Check if consumption varies within choice sets.
c = None
if "c_norm" in df.columns and not df["c_norm"].isna().all():
    c = df["c_norm"].to_numpy(dtype=np.float64)

# ... nearly identical logic ...

if c is None:
    NET_OF_TAX = 0.60
    # ... same computation pattern for couples
```

**Issue:** ~100 lines of near-identical logic. The only difference is couples need to handle household-level consumption vs individual-level.

#### 4. RURO Prior Computation (isolated in prep script)

**Location:** `RURO_prep_mnl_basic.py:240-419` (`_compute_prior`)

**Issue:** This is 179 lines of complex logic that computes log-densities for:
- Hours opportunity (normal distribution)
- Wage opportunity (log-normal distribution)

This logic is **NOT duplicated** (good!), but it's tightly coupled to the prep script. If estimation needs to recompute priors (e.g., for diagnostics), it would require duplicating this logic or importing from prep script.

### MODERATE: Redundant Patterns

#### 5. Helper Functions (_get_col pattern)

**RURO_estimate_FR.py:1113-1122**
```python
def _get_col(df: pd.DataFrame, col: str, default: float = 0.0) -> np.ndarray:
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").fillna(default).to_numpy()
    else:
        return np.full(len(df), default)
```

**Similar pattern in RURO_prep_mnl_basic.py** for safe column access, but not abstracted into reusable function.

**Issue:** This pattern is repeated ~50 times in RURO_estimate_FR.py. Not a duplication per se, but shows a common pattern that could be centralized.

#### 6. Parameter Packing/Unpacking (multiple functions)

**RURO_estimate_FR.py:**
- `unpack_theta_singles` (line ~1004)
- `unpack_theta_couples` (line 4368)
- `_extract_group_params_from_joint` (line 4279)

**Issue:** Each function manually indexes into the theta vector. While necessary for type safety (dataclasses), there's no validation that indexes are consistent with `get_param_names_*` functions.

**Risk:** If parameter layout changes (e.g., adding a new shifter), multiple functions need updating in lockstep.

### MINOR: Redundant Imports

Multiple files import the same standard libraries (`numpy`, `pandas`, `logging`, `Path`). This is acceptable Python practice, **NOT flagged for cleanup**.

---

## C) Concrete Fixes as Diffs

### Fix 1: Consolidate Box-Cox Functions into Shared Utilities

**Create:** `scripts/utils/transformations.py`

```python
"""
Box-Cox transformations and derivatives.

SINGLE SOURCE OF TRUTH for all utility transformations used in RURO estimation.
"""
from __future__ import annotations
import numpy as np
from typing import Union

__all__ = ['boxcox_transform', 'd_boxcox_dtheta', 'd_boxcox_dx']

# Numerical stability threshold
BOXCOX_EPSILON = 1e-6

def boxcox_transform(x: Union[float, np.ndarray], theta: float) -> Union[float, np.ndarray]:
    """
    Box-Cox transformation: (x^θ - 1) / θ.

    For θ → 0, this approaches log(x) (L'Hôpital's rule).

    Parameters
    ----------
    x : float or np.ndarray
        Input value(s), must be positive.
    theta : float
        Transformation parameter. θ=1 is linear, θ=0 is log.

    Returns
    -------
    Union[float, np.ndarray]
        Transformed value(s).

    Notes
    -----
    - Handles both scalar and array inputs
    - Clips x to avoid log(0)
    - Used in: RURO estimation, post-estimation

    Examples
    --------
    >>> boxcox_transform(1.0, 0.5)
    0.0
    >>> boxcox_transform(2.0, 0.0)  # log(2)
    0.693147...
    """
    x = np.clip(x, BOXCOX_EPSILON, None)

    if abs(theta) < BOXCOX_EPSILON:
        return np.log(x)
    else:
        return (np.power(x, theta) - 1.0) / theta


def d_boxcox_dtheta(x: Union[float, np.ndarray], theta: float) -> Union[float, np.ndarray]:
    """
    Derivative of Box-Cox transform w.r.t. theta: ∂BC(x,θ)/∂θ.

    Used for analytical gradient computation in estimation.

    Parameters
    ----------
    x : float or np.ndarray
        Input value(s), must be positive.
    theta : float
        Transformation parameter.

    Returns
    -------
    Union[float, np.ndarray]
        Derivative value(s).
    """
    ln_x = np.log(np.clip(x, BOXCOX_EPSILON, None))

    if abs(theta) < BOXCOX_EPSILON:
        # Limit as θ → 0: 0.5 * (log x)²
        return 0.5 * ln_x * ln_x
    else:
        x_theta = np.power(x, theta)
        numerator = theta * x_theta * ln_x - (x_theta - 1.0)
        denominator = theta * theta
        return numerator / denominator


def d_boxcox_dx(x: Union[float, np.ndarray], theta: float) -> Union[float, np.ndarray]:
    """
    Derivative of Box-Cox transform w.r.t. x: ∂BC(x,θ)/∂x.

    Parameters
    ----------
    x : float or np.ndarray
        Input value(s), must be positive.
    theta : float
        Transformation parameter.

    Returns
    -------
    Union[float, np.ndarray]
        Derivative value(s).
    """
    x = np.clip(x, BOXCOX_EPSILON, None)

    if abs(theta) < BOXCOX_EPSILON:
        # Limit as θ → 0: 1/x
        return 1.0 / x
    else:
        return np.power(x, theta - 1.0)
```

**Modify:** `RURO_estimate_FR.py`

```diff
--- a/scripts/RURO_estimate_FR.py
+++ b/scripts/RURO_estimate_FR.py
@@ -1,6 +1,7 @@
 """RURO Estimation for France 2016."""
 from __future__ import annotations
 import numpy as np
+from utils.transformations import boxcox_transform, d_boxcox_dtheta, d_boxcox_dx

-# DELETE lines 1191-1246 (old boxcox functions)
-# DELETE lines 2574-2588 (old _fast_boxcox functions)
+# Use imported functions instead
```

**Modify:** `RURO_post_estimation.py`

```diff
--- a/scripts/RURO_post_estimation.py
+++ b/scripts/RURO_post_estimation.py
@@ -1,6 +1,7 @@
 """RURO Post-Estimation Analysis."""
 from __future__ import annotations
 import numpy as np
+from utils.transformations import boxcox_transform

-# DELETE lines 223-235 (old boxcox_transform)
+# Use imported function instead
```

**Impact:** Reduces codebase by ~80 lines, eliminates 3 implementations down to 1 canonical version.

---

### Fix 2: Centralize Normalization Constants

**Create:** `scripts/utils/constants.py`

```python
"""
Normalization constants for RURO estimation.

SINGLE SOURCE OF TRUTH for all scaling factors.
These values should match the data preparation stage (RURO_prep.py).
"""

# Disposable income normalization (in euros/year)
# Used to scale consumption variables to ~O(1) for numerical stability
MEAN_DISPY_NORM = 2500.0

# Mean hours worked normalization (in hours/week)
# Used to center leisure around median worker
MEAN_LHW_NORM = 35.0

# Total time endowment (in hours/week)
# Assumes: 24h/day * 7 days/week - 88h sleep/week = 80h
TOTAL_LEISURE_HOURS = 80.0

# Net-of-tax rate for synthetic consumption computation
# Used when EUROMOD consumption not available (fallback)
NET_OF_TAX_RATE = 0.60
```

**Modify:** `RURO_estimate_FR.py`

```diff
--- a/scripts/RURO_estimate_FR.py
+++ b/scripts/RURO_estimate_FR.py
@@ -1,6 +1,7 @@
 """RURO Estimation for France 2016."""
 from __future__ import annotations
 import numpy as np
+from utils.constants import MEAN_DISPY_NORM, MEAN_LHW_NORM, TOTAL_LEISURE_HOURS, NET_OF_TAX_RATE

-# DELETE lines 90-93 (old constants)
```

**Modify:** `RURO_prep_mnl_basic.py`

```diff
--- a/scripts/RURO_prep_mnl_basic.py
+++ b/scripts/RURO_prep_mnl_basic.py
@@ -1,6 +1,7 @@
 """Build MNL estimation dataset from RURO draws + EUROMOD outputs."""
 from __future__ import annotations
 import pandas as pd
+from utils.constants import MEAN_DISPY_NORM, MEAN_LHW_NORM, TOTAL_LEISURE_HOURS

-# DELETE lines 33-36 (old constants)
```

**Impact:**
- Reduces duplication by 2 occurrences
- Makes it trivial to update constants for different years/countries
- Documents the source of truth for these magic numbers

---

### Fix 3: Extract Consumption Computation Logic

**Create:** `scripts/utils/consumption.py`

```python
"""
Consumption computation utilities.

SINGLE SOURCE OF TRUTH for extracting and normalizing consumption data.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Tuple
from .constants import MEAN_DISPY_NORM, NET_OF_TAX_RATE

__all__ = ['extract_consumption_singles', 'extract_consumption_couples']


def _check_consumption_varies(c: np.ndarray, ids: np.ndarray) -> bool:
    """Check if consumption varies within choice sets (by individual)."""
    df_check = pd.DataFrame({'id': ids, 'c': c})
    c_std_per_id = df_check.groupby('id')['c'].std()
    return (c_std_per_id > 1e-6).any()


def extract_consumption_singles(
    df: pd.DataFrame,
    id_col: str = 'idhh_true',
) -> np.ndarray:
    """
    Extract consumption for singles estimation.

    CRITICAL FIX: Check if consumption varies within choice sets.
    If ils_dispy is constant (EUROMOD not run for each draw), we compute
    a synthetic consumption that varies with earnings.

    Parameters
    ----------
    df : pd.DataFrame
        MNL dataset (long format) for singles.
    id_col : str
        Column name for individual IDs.

    Returns
    -------
    c : np.ndarray
        Normalized consumption (mean = 1), shape (n_rows,).

    Notes
    -----
    Priority order:
    1. c_norm (if varies)
    2. ils_dispy / MEAN_DISPY_NORM (if varies)
    3. Synthetic: base_non_labor + NET_OF_TAX * earnings (fallback)
    """
    n = len(df)
    ids = df[id_col].to_numpy()

    # Try c_norm first
    c = None
    if "c_norm" in df.columns and not df["c_norm"].isna().all():
        c = df["c_norm"].to_numpy(dtype=np.float64)
        if _check_consumption_varies(c, ids):
            return c

    # Try ils_dispy / MEAN_DISPY_NORM
    if "ils_dispy" in df.columns and not df["ils_dispy"].isna().all():
        c = df["ils_dispy"].to_numpy(dtype=np.float64) / MEAN_DISPY_NORM
        if _check_consumption_varies(c, ids):
            return c

    # Fallback: Compute synthetic consumption from earnings
    # This requires base income (draw=0) and variable earnings (yem)
    base_mask = (df['draw'] == 0)

    if 'ils_dispy' in df.columns and 'yem' in df.columns:
        base_ils = df.loc[base_mask, 'ils_dispy'].to_numpy()
        base_yem = df.loc[base_mask, 'yem'].to_numpy()

        # Map base values back to all rows using ID
        unique_ids, inverse = np.unique(ids, return_inverse=True)
        base_non_labor = base_ils - NET_OF_TAX_RATE * base_yem

        # For each row: C = base_non_labor + NET_OF_TAX * current_yem
        yem = df['yem'].to_numpy()
        c = base_non_labor[inverse] + NET_OF_TAX_RATE * yem
        c = c / MEAN_DISPY_NORM  # Normalize
        return c

    # Final fallback: constant consumption (not ideal, but prevents crash)
    return np.ones(n, dtype=np.float64)


def extract_consumption_couples(
    df: pd.DataFrame,
    id_col: str = 'idhh',
) -> np.ndarray:
    """
    Extract consumption for couples estimation.

    Same logic as singles, but consumption is at household level.

    Parameters
    ----------
    df : pd.DataFrame
        MNL dataset (long format) for couples.
    id_col : str
        Column name for household IDs.

    Returns
    -------
    c : np.ndarray
        Normalized consumption (mean = 1), shape (n_rows,).
    """
    n = len(df)
    ids = df[id_col].to_numpy()

    # Try c_norm first
    c = None
    if "c_norm" in df.columns and not df["c_norm"].isna().all():
        c = df["c_norm"].to_numpy(dtype=np.float64)
        if _check_consumption_varies(c, ids):
            return c

    # Try ils_dispy / MEAN_DISPY_NORM
    if "ils_dispy" in df.columns and not df["ils_dispy"].isna().all():
        c = df["ils_dispy"].to_numpy(dtype=np.float64) / MEAN_DISPY_NORM
        if _check_consumption_varies(c, ids):
            return c

    # Fallback: Compute synthetic consumption from earnings (household)
    base_mask = (df['draw'] == 0)

    if 'ils_dispy' in df.columns and 'yem_m' in df.columns and 'yem_f' in df.columns:
        base_ils = df.loc[base_mask, 'ils_dispy'].to_numpy()
        base_yem_m = df.loc[base_mask, 'yem_m'].to_numpy()
        base_yem_f = df.loc[base_mask, 'yem_f'].to_numpy()
        base_yem_total = base_yem_m + base_yem_f

        unique_ids, inverse = np.unique(ids, return_inverse=True)
        base_non_labor = base_ils - NET_OF_TAX_RATE * base_yem_total

        # For each row: C = base_non_labor + NET_OF_TAX * (yem_m + yem_f)
        yem_m = df['yem_m'].to_numpy()
        yem_f = df['yem_f'].to_numpy()
        yem_total = yem_m + yem_f
        c = base_non_labor[inverse] + NET_OF_TAX_RATE * yem_total
        c = c / MEAN_DISPY_NORM
        return c

    # Final fallback
    return np.ones(n, dtype=np.float64)
```

**Modify:** `RURO_estimate_FR.py`

```diff
--- a/scripts/RURO_estimate_FR.py
+++ b/scripts/RURO_estimate_FR.py
@@ -5,6 +5,7 @@
 import pandas as pd
 import numpy as np
 from utils.transformations import boxcox_transform, d_boxcox_dtheta, d_boxcox_dx
+from utils.consumption import extract_consumption_singles, extract_consumption_couples

 def precompute_data_singles(...):
-    # DELETE lines 321-421 (old consumption logic)
+    c = extract_consumption_singles(df, id_col='idhh_true')

 def precompute_data_couples(...):
-    # DELETE lines 580-658 (old consumption logic)
+    c = extract_consumption_couples(df, id_col='idhh')
```

**Impact:**
- Reduces RURO_estimate_FR.py by ~180 lines
- Eliminates near-identical logic duplication
- Makes consumption extraction testable in isolation
- Documents the complex fallback logic in one place

---

### Fix 4: Add Validation for Parameter Layout Consistency

**Create:** `scripts/utils/param_validation.py`

```python
"""
Parameter layout validation.

Ensures that parameter unpacking functions are consistent with parameter name lists.
"""
from __future__ import annotations
from typing import List, Callable
import numpy as np

def validate_param_layout(
    get_names_fn: Callable[[], List[str]],
    unpack_fn: Callable[[np.ndarray], tuple],
    wage_spec: str = "fw",
    group: str = "singles",
) -> None:
    """
    Validate that parameter names align with unpacking function.

    This is a sanity check that should be run in tests or as a startup check.

    Parameters
    ----------
    get_names_fn : callable
        Function returning list of parameter names (e.g., get_param_names_singles)
    unpack_fn : callable
        Function unpacking theta vector (e.g., unpack_theta_singles)
    wage_spec : str
        "fw" or "vw"
    group : str
        Group name for error messages

    Raises
    ------
    ValueError
        If unpacking produces wrong number of parameters

    Examples
    --------
    >>> from RURO_estimate_FR import get_param_names_singles, unpack_theta_singles
    >>> validate_param_layout(
    ...     lambda: get_param_names_singles("fw"),
    ...     lambda theta: unpack_theta_singles(theta, "fw"),
    ...     wage_spec="fw",
    ...     group="singles_fw"
    ... )
    """
    names = get_names_fn()
    n_expected = len(names)

    # Create dummy theta
    theta_dummy = np.zeros(n_expected)

    # Unpack
    unpacked = unpack_fn(theta_dummy)

    # Count parameters in unpacked dataclasses
    n_unpacked = sum(len(vars(obj)) for obj in unpacked if hasattr(obj, '__dict__'))

    if n_unpacked != n_expected:
        raise ValueError(
            f"Parameter layout mismatch for {group}!\n"
            f"  Expected (from names): {n_expected}\n"
            f"  Unpacked (from unpack_fn): {n_unpacked}\n"
            f"  This indicates parameter indices are out of sync."
        )
```

**Add to:** `tests/test_param_layout.py`

```python
"""Test parameter layout consistency."""
import pytest
from scripts.RURO_estimate_FR import (
    get_param_names_singles, unpack_theta_singles,
    get_param_names_couples, unpack_theta_couples,
    get_param_names_joint, get_initial_theta_joint,
)
from scripts.utils.param_validation import validate_param_layout

def test_singles_fw_layout():
    validate_param_layout(
        lambda: get_param_names_singles("fw"),
        lambda theta: unpack_theta_singles(theta, "fw"),
        wage_spec="fw",
        group="singles_fw"
    )

def test_singles_vw_layout():
    validate_param_layout(
        lambda: get_param_names_singles("vw"),
        lambda theta: unpack_theta_singles(theta, "vw"),
        wage_spec="vw",
        group="singles_vw"
    )

def test_couples_fw_layout():
    validate_param_layout(
        lambda: get_param_names_couples("fw"),
        lambda theta: unpack_theta_couples(theta, "fw"),
        wage_spec="fw",
        group="couples_fw"
    )

def test_couples_vw_layout():
    validate_param_layout(
        lambda: get_param_names_couples("vw"),
        lambda theta: unpack_theta_couples(theta, "vw"),
        wage_spec="vw",
        group="couples_vw"
    )

def test_joint_vw_layout():
    """Ensure joint theta can be correctly extracted for all groups."""
    theta_joint = get_initial_theta_joint(wage_spec="vw")
    param_names = get_param_names_joint(wage_spec="vw")

    assert len(theta_joint) == len(param_names), \
        f"Joint theta length {len(theta_joint)} != param_names length {len(param_names)}"

    # Check expected lengths
    assert len(param_names) == 60, f"Expected 60 params for vw joint, got {len(param_names)}"
```

**Impact:**
- Prevents silent parameter indexing bugs
- Documents expected parameter counts
- Catches regressions when adding/removing parameters

---

## D) "Single Source of Truth" Rules

### 1. Normalization Constants
**Location:** `scripts/utils/constants.py`
**Rule:** All scaling factors (MEAN_DISPY_NORM, MEAN_LHW_NORM, TOTAL_LEISURE_HOURS) must be imported from this file. **DO NOT** hardcode these values elsewhere.

**Enforcement:** Add pre-commit hook to grep for hardcoded `2500.0`, `35.0`, `80.0` outside of constants.py.

### 2. Box-Cox Transformations
**Location:** `scripts/utils/transformations.py`
**Rule:** All Box-Cox transforms and derivatives must use functions from this module. **DO NOT** reimplement Box-Cox logic.

**Enforcement:** Code review + unit tests ensuring RURO_estimate_FR and RURO_post_estimation import these functions.

### 3. Consumption Extraction
**Location:** `scripts/utils/consumption.py`
**Rule:** Consumption variables must be extracted using `extract_consumption_singles()` or `extract_consumption_couples()`. **DO NOT** manually compute consumption from ils_dispy/yem.

**Enforcement:** Code review. If adding new group types, extend the extraction functions rather than duplicating logic.

### 4. RURO Prior Computation
**Location:** `scripts/RURO_prep_mnl_basic.py:240-419` (_compute_prior function)
**Rule:** RURO prior (log-density) is computed **ONCE** during MNL dataset preparation. Estimation and post-estimation scripts read the `prior` column from the dataset.

**Exception:** If diagnostic tools need to recompute priors (e.g., for sensitivity analysis), extract `_compute_prior` into `scripts/utils/prior.py` and import it.

**Enforcement:** Ensure no direct calls to GSUR/wage density functions outside of RURO_prep_mnl_basic.py.

### 5. Choice Sets (Hours Alternatives)
**Location:** `scripts/RURO_prep_mnl_basic.py` (implicit in long-format dataset)
**Rule:** Choice sets are defined by `(ruro_id, draw)` grouping in the MNL dataset. Each individual has one observed alternative (draw=0) and N simulated alternatives (draw=1..99).

**Rule:** Hours categories are defined by `working`, `working_pt1`, `working_pt2`, `working_ft` indicator columns. **DO NOT** create new hour bins without updating RURO_prep_mnl_basic.py.

### 6. Opportunity Terms (hopp, wopp)
**Location:** `scripts/RURO_estimate_FR.py` (ff_calc_hopp, ff_calc_wopp functions)
**Rule:** Hours opportunity density (hopp) and wage opportunity density (wopp) are computed during estimation from precomputed data arrays. These use **SIMPLIFIED** specifications:
- **No region effects** (removed for identification)
- **No year dummies** (single year estimation)

**Rule:** If adding region/year effects back, update:
1. `PrecomputedDataSingles` / `PrecomputedDataCouples` (add columns)
2. `HoursOppParams` / `WageOppParams` (add parameters)
3. `ff_calc_hopp` / `ff_calc_wopp` (add terms to linear predictor)
4. `get_param_names_*` (add parameter names)

### 7. Random Seeding
**Location:** Currently **NOT ENFORCED** (⚠️ **ISSUE**)
**Rule:** For reproducibility, all random draws (Monte Carlo wage draws in RURO_draws.py, any bootstrapping in post-estimation) should use explicit seeds.

**Action Required:** Add `--seed` argument to scripts and set `np.random.seed(seed)` at the top of each script.

### 8. Output Paths
**Location:** `scripts/run_fr_2016_joint_only.ps1` (PowerShell script)
**Rule:** All output paths follow the pattern:
- Estimates: `outputs/estimates/{country}/{year}/{country}_{year}_{model_type}.json`
- Post-estimation: `outputs/post_estimation/{country}/{year}/{model_type}/`

**Enforcement:** Use `pathlib.Path` and centralize path construction in `scripts/utils/paths.py`.

---

## E) Verification Runbook

### Prerequisites

```powershell
# 1. Ensure .venv is activated
U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\activate

# 2. Verify Python version
python --version
# Expected: Python 3.12.2

# 3. Verify dependencies
python -c "import numpy, scipy, pandas, pyarrow, numba; print('✓ All dependencies OK')"
# Expected: ✓ All dependencies OK

# 4. Verify MNL dataset exists
ls U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl.parquet
# Expected: File exists (449,589 rows)
```

### Test 1: Parameter Layout Validation

```bash
# Run parameter layout tests
pytest tests/test_param_layout.py -v

# Expected output:
# test_singles_fw_layout PASSED
# test_singles_vw_layout PASSED
# test_couples_fw_layout PASSED
# test_couples_vw_layout PASSED
# test_joint_vw_layout PASSED
```

### Test 2: Box-Cox Transformation Consistency

```python
# Create test script: tests/test_boxcox_consistency.py
import numpy as np
from scripts.utils.transformations import boxcox_transform, d_boxcox_dtheta

def test_boxcox_identity():
    """Test Box-Cox(1, 1) = 0 (x^1 - 1)/1 = 0."""
    assert np.isclose(boxcox_transform(1.0, 1.0), 0.0)

def test_boxcox_log_limit():
    """Test Box-Cox(x, θ→0) → log(x)."""
    x = 2.0
    theta_near_zero = 1e-9
    bc_result = boxcox_transform(x, theta_near_zero)
    log_result = np.log(x)
    assert np.isclose(bc_result, log_result, atol=1e-6)

def test_derivative_finite_difference():
    """Validate analytical derivative matches finite difference."""
    x = 1.5
    theta = 0.5
    eps = 1e-6

    # Analytical
    grad_analytical = d_boxcox_dtheta(x, theta)

    # Finite difference
    bc_plus = boxcox_transform(x, theta + eps)
    bc_minus = boxcox_transform(x, theta - eps)
    grad_fd = (bc_plus - bc_minus) / (2 * eps)

    assert np.isclose(grad_analytical, grad_fd, rtol=1e-4)
```

```bash
pytest tests/test_boxcox_consistency.py -v
# Expected: All PASSED
```

### Test 3: Consumption Extraction Smoke Test

```python
# Create test: tests/test_consumption_extraction.py
import pandas as pd
import numpy as np
from scripts.utils.consumption import extract_consumption_singles

def test_extract_consumption_from_c_norm():
    """Test that c_norm is used when available and varies."""
    df = pd.DataFrame({
        'idhh_true': [1, 1, 1, 2, 2, 2],
        'draw': [0, 1, 2, 0, 1, 2],
        'c_norm': [1.0, 1.1, 1.2, 0.9, 1.0, 1.1],
    })

    c = extract_consumption_singles(df, id_col='idhh_true')

    # Should return c_norm directly (it varies)
    np.testing.assert_array_equal(c, df['c_norm'].to_numpy())

def test_extract_consumption_synthetic_fallback():
    """Test synthetic consumption when ils_dispy is constant."""
    df = pd.DataFrame({
        'idhh_true': [1, 1, 1],
        'draw': [0, 1, 2],
        'ils_dispy': [2500.0, 2500.0, 2500.0],  # Constant (bad!)
        'yem': [1000.0, 1200.0, 1400.0],        # Earnings vary
    })

    c = extract_consumption_singles(df, id_col='idhh_true')

    # Should use synthetic formula
    # C = base_non_labor + 0.6 * yem
    # base_non_labor = 2500 - 0.6*1000 = 1900
    # C[0] = 1900 + 0.6*1000 = 2500
    # C[1] = 1900 + 0.6*1200 = 2620
    # C[2] = 1900 + 0.6*1400 = 2740
    expected = np.array([2500.0, 2620.0, 2740.0]) / 2500.0  # Normalized

    np.testing.assert_allclose(c, expected, rtol=1e-6)
```

```bash
pytest tests/test_consumption_extraction.py -v
# Expected: All PASSED
```

### Test 4: Full Pipeline Dry Run

```powershell
# Navigate to repo root
cd U:\Desktop\Nizam_Hisham\MNL

# Run joint estimation (quick test with maxiter=10)
python scripts/RURO_estimate_FR.py `
  --mnl-file "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl.parquet" `
  --joint `
  --wage-spec vw `
  --optimizer L-BFGS-B `
  --maxiter 10 `
  --use-numba `
  --n-jobs 8 `
  --out-file "outputs/estimates/fr/2016/test_joint_dry_run.json"

# Expected output:
# [INFO] Loading MNL dataset...
# [INFO] Filtered to 449,589 rows (all groups)
# [INFO] Precomputing data arrays...
# [INFO] Starting joint estimation (60 parameters)...
# [INFO] Iteration 1/10: LL = -123456.78
# ...
# [INFO] Iteration 10/10: LL = -123000.00
# [INFO] Optimization terminated (maxiter reached)
# [INFO] Saved results to outputs/estimates/fr/2016/test_joint_dry_run.json
```

```bash
# Verify output file
cat outputs/estimates/fr/2016/test_joint_dry_run.json | python -m json.tool | head -n 20

# Expected: Valid JSON with theta, param_names, log_likelihood
```

### Test 5: Post-Estimation Dry Run

```bash
python scripts/RURO_post_estimation.py \
  --results outputs/estimates/fr/2016/test_joint_dry_run.json \
  --mnl-file "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl.parquet" \
  --out-dir outputs/post_estimation/fr/2016/test_dry_run \
  --wage-spec vw \
  --sex pooled

# Expected output:
# [INFO] Parsing parameters... Found 3 groups: ['sm', 'sf', 'cou']
# [INFO] Computing fit diagnostics...
# [INFO] Computing marginal utility diagnostics...
# [INFO] Generating plots...
# [INFO] Generating HTML report...
# [INFO] POST-ESTIMATION COMPLETE
```

```powershell
# Verify outputs exist
ls outputs/post_estimation/fr/2016/test_dry_run

# Expected files:
# vw_pooled_post_estimation_report.html
# vw_pooled_params.csv
# vw_pooled_elasticities.csv
# vw_sm_contours.png
# vw_sf_contours.png
# vw_cou_m_contours.png
# vw_cou_f_contours.png
```

### Test 6: Full Production Run

```powershell
# Run the full pipeline (with production maxiter=2000)
powershell -ExecutionPolicy Bypass -File ./scripts/run_fr_2016_joint_only.ps1

# Expected duration: ~2-3 minutes
# Expected output:
# ========================================
# RURO France 2016 - Joint Estimation Only
# ========================================
# [Step 7a] Single Males (vw)...
#   Converged: True, LL=-12345.67, Iters=156
# [Step 7b] Single Females (vw)...
#   Converged: True, LL=-23456.78, Iters=189
# [Step 7c] Couples (vw)...
#   Converged: True, LL=-56789.01, Iters=234
# [Step 7d] Joint Estimation (vw)...
#   Converged: True, LL=-92591.46, Iters=278
# [Step 8] Post-Estimation...
#   ✓ HTML report generated
#   ✓ Plots saved
# ========================================
# Pipeline completed successfully!
# ========================================
```

### Test 7: Verify Reproducibility (Determinism Check)

```powershell
# Run estimation twice with same seed
python scripts/RURO_estimate_FR.py ... --seed 42 --out-file run1.json
python scripts/RURO_estimate_FR.py ... --seed 42 --out-file run2.json

# Compare results
python -c "
import json
with open('run1.json') as f1, open('run2.json') as f2:
    r1, r2 = json.load(f1), json.load(f2)
    theta1, theta2 = r1['theta'], r2['theta']
    max_diff = max(abs(a-b) for a,b in zip(theta1, theta2))
    print(f'Max parameter difference: {max_diff}')
    assert max_diff < 1e-10, 'NOT DETERMINISTIC!'
    print('✓ Results are identical (deterministic)')
"
```

**Expected output:** `✓ Results are identical (deterministic)`

**⚠️ KNOWN ISSUE:** Current scripts do NOT enforce seeding! This test will **FAIL** until Fix #9 (add --seed argument) is implemented.

---

## F) Summary of Recommended Actions

### Immediate (Pre-MVP, High Priority)

1. **Create `scripts/utils/` directory** with:
   - `transformations.py` (Box-Cox functions)
   - `constants.py` (normalization constants)
   - `consumption.py` (consumption extraction logic)
   - `param_validation.py` (parameter layout checks)

2. **Modify core scripts** to import from utils:
   - Update `RURO_estimate_FR.py` (remove duplicated Box-Cox, constants, consumption)
   - Update `RURO_prep_mnl_basic.py` (import constants)
   - Update `RURO_post_estimation.py` (import Box-Cox)

3. **Add unit tests** (`tests/`):
   - `test_param_layout.py` (parameter consistency)
   - `test_boxcox_consistency.py` (transformation correctness)
   - `test_consumption_extraction.py` (consumption logic)

4. **Run verification runbook** (Tests 1-6) to confirm no regressions

### Short-term (MVP Packaging)

5. **Add random seeding**:
   - Add `--seed` argument to all scripts
   - Set `np.random.seed(seed)` at script entry points
   - Update `run_fr_2016_joint_only.ps1` to pass `--seed 42`

6. **Centralize path construction**:
   - Create `scripts/utils/paths.py` with output path builders
   - Update all scripts to use centralized paths

7. **Add logging configuration**:
   - Create `scripts/utils/logging_config.py`
   - Ensure all scripts use consistent log format

### Long-term (Post-MVP)

8. **Extract RURO prior computation** (optional):
   - If diagnostic tools need priors, move `_compute_prior` to `utils/prior.py`
   - Import in both RURO_prep_mnl_basic.py and diagnostic scripts

9. **Performance profiling**:
   - Profile estimation time (L-BFGS-B iterations)
   - Identify bottlenecks (gradient computation, log-likelihood)
   - Consider Numba JIT for more functions (currently only used in 4 places)

10. **Documentation**:
    - Convert this audit report into permanent documentation
    - Add docstrings to all refactored utilities
    - Update CLAUDE.md with new utils/ structure

---

## G) Impact Summary

### Lines of Code Reduction
- **Before:** 8,841 total lines (RURO_estimate_FR: 5544, RURO_prep_mnl_basic: 578, RURO_post_estimation: 2748)
- **After refactoring:** ~8,550 lines (estimated)
- **Reduction:** ~291 lines (~3.3%)

### Duplication Elimination
- Box-Cox functions: 3 copies → 1 copy (saved ~80 lines)
- Normalization constants: 2 locations → 1 location (saved ~6 lines)
- Consumption extraction: 2 near-identical functions → 2 wrappers of shared logic (saved ~180 lines)
- New utilities added: ~200 lines (transformations.py, consumption.py, constants.py, param_validation.py)
- Net reduction: ~66 lines + improved maintainability

### Risk Mitigation
- **Parameter indexing bugs:** Automated tests catch mismatches
- **Magic number drift:** Single source of truth for constants
- **Consumption logic divergence:** Shared implementation prevents bugs
- **Transformation inconsistencies:** Centralized Box-Cox eliminates numerical differences

### Maintainability Improvements
- **Adding new parameters:** Update 1 file (get_param_names) + 1 test
- **Changing normalization:** Update 1 constant, propagates everywhere
- **Debugging consumption:** Read 1 function instead of 2 duplicates
- **Testing transformations:** Unit tests cover all use cases

---

## H) Next Steps

1. **Review this document** with team/supervisor
2. **Approve refactoring plan** (C: Concrete Fixes)
3. **Implement fixes** in order:
   - Fix 1: Box-Cox consolidation
   - Fix 2: Constants centralization
   - Fix 3: Consumption extraction
   - Fix 4: Parameter validation tests
4. **Run verification runbook** (E: Verification)
5. **Commit changes** with message: `refactor: consolidate duplicated utilities (pre-MVP cleanup)`
6. **Proceed to MVP packaging** (docs/mvp_facts_report.md already complete)

---

**End of Pipeline Audit Report**
For questions, contact: Research Software Engineer
Last updated: 2025-12-13
