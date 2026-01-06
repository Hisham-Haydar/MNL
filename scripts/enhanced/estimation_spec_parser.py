"""
==============================================================================
RURO MNL Specification Parser
==============================================================================
Parses and validates YAML specification files for MNL estimation.

Provides:
- YAML loading and validation
- EstimationSpec dataclass with all configuration
- Parameter name extraction and ordering
- Initial value and bounds extraction
- Specification validation

Author: Enhanced RURO Pipeline
Created: 2026-01-03
==============================================================================
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import yaml


@dataclass
class EstimationSpec:
    """
    Parsed estimation specification.

    Contains all information needed for estimation:
    - Specification metadata (name, wage_spec)
    - Parameter names and structure
    - Initial values and bounds
    - Shifter configurations
    """
    # Metadata
    name: str
    description: str
    wage_spec: str  # fw | vw | loc_empirical

    # Utility configuration
    utility_form: str  # box_cox | log | linear
    utility_consumption_coef: str
    utility_consumption_theta: Optional[str]
    utility_leisure_intercept: str
    utility_leisure_theta: Optional[str]
    utility_leisure_shifters: List[Dict[str, Any]]

    # Hours opportunity configuration
    hours_shifters: List[Dict[str, Any]]

    # Wage opportunity configuration
    wage_form: str  # log_normal | occupation_groups
    wage_mean_shifters: List[Dict[str, Any]]
    wage_variance_param: Optional[str]
    wage_loc_groups: Optional[List[Dict[str, Any]]]  # For loc_empirical

    # Couples configuration
    couples_interaction_coef: Optional[str]

    # Parameter management
    all_param_names: List[str] = field(default_factory=list)
    initial_values: Dict[str, float] = field(default_factory=dict)
    bounds: Dict[str, Tuple[float, float]] = field(default_factory=dict)

    # Optimization settings
    opt_method: str = "L-BFGS-B"
    opt_analytical_gradient: bool = True
    opt_max_iterations: int = 10000
    opt_tolerance: float = 1e-6

    def get_initial_vector(self) -> np.ndarray:
        """
        Get initial values as numpy array in parameter order.

        Returns
        -------
        np.ndarray
            Initial values vector
        """
        return np.array([self.initial_values[name] for name in self.all_param_names])

    def get_bounds_tuple(self) -> List[Tuple[Optional[float], Optional[float]]]:
        """
        Get bounds in scipy.optimize format.

        Returns list of (lower, upper) tuples, with None for unbounded parameters.

        Returns
        -------
        list of tuple
            Bounds for each parameter in order
        """
        bounds_list = []
        for name in self.all_param_names:
            if name in self.bounds:
                bounds_list.append(self.bounds[name])
            else:
                bounds_list.append((None, None))  # Unbounded
        return bounds_list

    def get_param_index(self, param_name: str) -> int:
        """
        Get index of parameter in parameter vector.

        Parameters
        ----------
        param_name : str
            Parameter name

        Returns
        -------
        int
            Index in all_param_names list

        Raises
        ------
        ValueError
            If parameter name not found
        """
        try:
            return self.all_param_names.index(param_name)
        except ValueError:
            raise ValueError(f"Parameter '{param_name}' not found in specification")

    def unpack_parameters(self, theta: np.ndarray) -> Dict[str, float]:
        """
        Unpack parameter vector into dictionary.

        Parameters
        ----------
        theta : np.ndarray
            Parameter vector

        Returns
        -------
        dict
            Dictionary mapping parameter names to values
        """
        if len(theta) != len(self.all_param_names):
            raise ValueError(
                f"Parameter vector length ({len(theta)}) does not match "
                f"number of parameters ({len(self.all_param_names)})"
            )

        return {name: theta[i] for i, name in enumerate(self.all_param_names)}


def parse_specification(yaml_path: Path) -> EstimationSpec:
    """
    Load and validate YAML specification file.

    Parameters
    ----------
    yaml_path : Path
        Path to YAML specification file

    Returns
    -------
    EstimationSpec
        Parsed specification object

    Raises
    ------
    FileNotFoundError
        If YAML file doesn't exist
    ValueError
        If specification is invalid
    """
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info(f"Parsing specification: {yaml_path}")
    logger.info("="*80)

    if not yaml_path.exists():
        raise FileNotFoundError(f"Specification file not found: {yaml_path}")

    # Load YAML
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    # Extract metadata
    spec_meta = config.get("specification", {})
    name = spec_meta.get("name", "unknown")
    description = spec_meta.get("description", "")
    wage_spec = spec_meta.get("wage_spec", "fw")

    logger.info(f"Specification: {name}")
    logger.info(f"Description: {description}")
    logger.info(f"Wage specification: {wage_spec}")

    # Validate wage_spec
    if wage_spec not in ["fw", "vw", "loc_empirical"]:
        raise ValueError(f"Invalid wage_spec: {wage_spec}. Must be fw, vw, or loc_empirical")

    # Parse utility function
    utility_config = config.get("utility", {})
    utility_form = utility_config.get("functional_form", "box_cox")

    consumption_config = utility_config.get("consumption", {})
    utility_consumption_coef = consumption_config.get("coefficient", "beta_c")
    utility_consumption_theta = consumption_config.get("box_cox_exponent", None)

    leisure_config = utility_config.get("leisure", {})
    utility_leisure_intercept = leisure_config.get("intercept", "beta_l0")
    utility_leisure_theta = leisure_config.get("box_cox_exponent", None)
    utility_leisure_shifters = leisure_config.get("shifters", [])

    # Parse hours opportunity
    hours_config = config.get("hours_opportunity", {})
    hours_shifters = hours_config.get("shifters", [])

    # Parse wage opportunity
    wage_config = config.get("wage_opportunity", {})
    wage_form = wage_config.get("specification", "log_normal")
    wage_mean_shifters = wage_config.get("mean_shifters", [])
    wage_variance_param = None
    wage_loc_groups = None

    if wage_spec in ["vw"]:
        variance_config = wage_config.get("variance", {})
        wage_variance_param = variance_config.get("parameter", "sigma")

    if wage_spec == "loc_empirical":
        wage_loc_groups = wage_config.get("groups", [])
        if not wage_loc_groups:
            raise ValueError("loc_empirical specification requires 'groups' in wage_opportunity")

    # Parse couples configuration
    couples_config = config.get("couples", {})
    couples_interaction_coef = None
    if couples_config:
        interaction_config = couples_config.get("leisure_interaction", {})
        couples_interaction_coef = interaction_config.get("coefficient", "beta_interact")

    # Parse initial values
    initial_values = config.get("initial_values", {})
    if not initial_values:
        logger.warning("No initial values specified in YAML")

    # Parse bounds
    opt_config = config.get("optimization", {})
    bounds = opt_config.get("bounds", {})    # Parse optimization settings
    opt_method = opt_config.get("method", "L-BFGS-B")
    opt_analytical_gradient = opt_config.get("analytical_gradient", True)
    opt_max_iterations = opt_config.get("max_iterations", 10000)
    opt_tolerance = float(opt_config.get("tolerance", 1e-6))

    # Build parameter list (order matters!)
    all_param_names = _build_parameter_list(
        utility_form=utility_form,
        utility_consumption_coef=utility_consumption_coef,
        utility_consumption_theta=utility_consumption_theta,
        utility_leisure_intercept=utility_leisure_intercept,
        utility_leisure_theta=utility_leisure_theta,
        utility_leisure_shifters=utility_leisure_shifters,
        hours_shifters=hours_shifters,
        wage_spec=wage_spec,
        wage_form=wage_form,
        wage_mean_shifters=wage_mean_shifters,
        wage_variance_param=wage_variance_param,
        wage_loc_groups=wage_loc_groups,
        couples_interaction_coef=couples_interaction_coef
    )

    logger.info(f"Total parameters: {len(all_param_names)}")

    # Validate initial values
    missing_initial = [p for p in all_param_names if p not in initial_values]
    if missing_initial:
        raise ValueError(f"Missing initial values for parameters: {missing_initial}")

    # Validate bounds
    for param_name, bound in bounds.items():
        if param_name not in all_param_names:
            logger.warning(f"Bound specified for unknown parameter: {param_name}")
        if not isinstance(bound, list) or len(bound) != 2:
            raise ValueError(f"Bound for {param_name} must be [lower, upper], got {bound}")
        if bound[0] >= bound[1]:
            raise ValueError(f"Invalid bound for {param_name}: lower ({bound[0]}) >= upper ({bound[1]})")

    # Convert bounds to tuples
    bounds_dict = {name: tuple(bound) for name, bound in bounds.items()}

    logger.info("="*80)
    logger.info("Specification parsing complete")
    logger.info("="*80)

    return EstimationSpec(
        name=name,
        description=description,
        wage_spec=wage_spec,
        utility_form=utility_form,
        utility_consumption_coef=utility_consumption_coef,
        utility_consumption_theta=utility_consumption_theta,
        utility_leisure_intercept=utility_leisure_intercept,
        utility_leisure_theta=utility_leisure_theta,
        utility_leisure_shifters=utility_leisure_shifters,
        hours_shifters=hours_shifters,
        wage_form=wage_form,
        wage_mean_shifters=wage_mean_shifters,
        wage_variance_param=wage_variance_param,
        wage_loc_groups=wage_loc_groups,
        couples_interaction_coef=couples_interaction_coef,
        all_param_names=all_param_names,
        initial_values=initial_values,
        bounds=bounds_dict,
        opt_method=opt_method,
        opt_analytical_gradient=opt_analytical_gradient,
        opt_max_iterations=opt_max_iterations,
        opt_tolerance=opt_tolerance
    )


def _build_parameter_list(
    utility_form: str,
    utility_consumption_coef: str,
    utility_consumption_theta: Optional[str],
    utility_leisure_intercept: str,
    utility_leisure_theta: Optional[str],
    utility_leisure_shifters: List[Dict[str, Any]],
    hours_shifters: List[Dict[str, Any]],
    wage_spec: str,
    wage_form: str,
    wage_mean_shifters: List[Dict[str, Any]],
    wage_variance_param: Optional[str],
    wage_loc_groups: Optional[List[Dict[str, Any]]],
    couples_interaction_coef: Optional[str]
) -> List[str]:
    """
    Build ordered list of all parameter names.

    Parameter order convention:
    1. Preference parameters (leisure shifters, consumption coef, Box-Cox exponents)
    2. Hours opportunity parameters
    3. Wage opportunity parameters
    4. Couples interaction (if applicable)

    This matches the order in the old script for backward compatibility.

    Returns
    -------
    list of str
        Ordered parameter names
    """
    params = []

    # 1. Leisure shifters
    params.append(utility_leisure_intercept)  # beta_l0

    for shifter in utility_leisure_shifters:
        params.append(shifter["coefficient"])

    # 2. Consumption coefficient
    params.append(utility_consumption_coef)  # beta_c

    # 3. Box-Cox exponents (if applicable)
    if utility_form == "box_cox":
        if utility_leisure_theta:
            params.append(utility_leisure_theta)  # theta_l
        if utility_consumption_theta:
            params.append(utility_consumption_theta)  # theta_c

    # 4. Hours opportunity parameters
    for shifter in hours_shifters:
        params.append(shifter["coefficient"])

    # 5. Wage opportunity parameters
    if wage_spec == "vw":
        # Mincer equation parameters
        for shifter in wage_mean_shifters:
            params.append(shifter["coefficient"])

        if wage_variance_param:
            params.append(wage_variance_param)  # sigma

    elif wage_spec == "loc_empirical":
        # LOC-specific intercepts
        for group in wage_loc_groups:
            params.append(group["intercept"])

        # LOC-specific sigmas
        for group in wage_loc_groups:
            params.append(group["sigma"])

        # Common shifters
        for shifter in wage_mean_shifters:
            params.append(shifter["coefficient"])

    # 6. Couples interaction (if applicable)
    if couples_interaction_coef:
        params.append(couples_interaction_coef)

    # Check for duplicates
    if len(params) != len(set(params)):
        duplicates = [p for p in params if params.count(p) > 1]
        raise ValueError(f"Duplicate parameter names found: {set(duplicates)}")

    return params


def load_custom_initial_values(csv_path: Path) -> Dict[str, float]:
    """
    Load custom initial values from CSV or JSON file.

    CSV format:
        parameter_name,value
        beta_l0,1.0
        beta_c,0.5
        ...

    JSON format:
        {
            "param_names": ["beta_l0", "beta_c", ...],
            "theta": [1.0, 0.5, ...]
        }

    Parameters
    ----------
    csv_path : Path
        Path to CSV or JSON file

    Returns
    -------
    dict
        Dictionary mapping parameter names to initial values
    """
    import pandas as pd
    import json

    if not csv_path.exists():
        raise FileNotFoundError(f"Initial values file not found: {csv_path}")

    # Check if it's a JSON file
    if csv_path.suffix.lower() == '.json':
        with open(csv_path, 'r') as f:
            data = json.load(f)
        
        if "param_names" not in data or "theta" not in data:
            raise ValueError("JSON must have fields: param_names, theta")
        
        return dict(zip(data["param_names"], data["theta"]))
    
    # Otherwise treat as CSV
    df = pd.read_csv(csv_path)

    if "parameter_name" not in df.columns or "value" not in df.columns:
        raise ValueError("CSV must have columns: parameter_name, value")

    return dict(zip(df["parameter_name"], df["value"]))


# ==============================================================================
# End of estimation_spec_parser.py
# ==============================================================================
