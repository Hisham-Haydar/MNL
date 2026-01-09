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
    
    Supports model versions:
    - "legacy": Original Stijn Van Houtven specification
    - "AC2013": Aaberge-Colombino (2013) aligned specification
    """
    # Metadata (required fields - no defaults)
    name: str
    description: str
    wage_spec: str  # fw | vw | loc_empirical

    # Utility configuration (required fields)
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

    # === Fields with defaults below this line ===
    
    # Model version (NEW: AC2013 support)
    model_version: str = "legacy"  # "legacy" or "AC2013"

    # Parameter management
    all_param_names: List[str] = field(default_factory=list)
    initial_values: Dict[str, float] = field(default_factory=dict)
    bounds: Dict[str, Tuple[float, float]] = field(default_factory=dict)

    # Optimization settings
    opt_method: str = "L-BFGS-B"
    opt_analytical_gradient: bool = True
    opt_max_iterations: int = 10000
    opt_tolerance: float = 1e-6
    opt_gradient_tolerance: float = 1e-6  # gtol - NEW FIELD
    opt_display_convergence: bool = False  # NEW FIELD for disp
    opt_iprint: int = -1  # NEW FIELD for L-BFGS-B iteration printing    # Gradient verification settings
    grad_verify_enabled: bool = False
    grad_verify_method: str = "central"
    grad_verify_epsilon: float = 1e-7
    grad_verify_tolerance: float = 1e-4
    grad_verify_at_init: bool = True
    grad_verify_random_points: int = 0
    grad_verify_seed: int = 42
    grad_verify_verbose: bool = False
    
    # A-C 2013 specific settings (NEW)
    ac2013_use_log_age: bool = False           # Use log(age) instead of linear age
    ac2013_children_age_groups: bool = False   # Use C1, C2, C3 instead of n_children
    ac2013_experience_in_wage: bool = False    # Use exp, exp² in wage equation
    ac2013_couples_cross_leisure: bool = False # Use α_ll cross-leisure term
    ac2013_couples_mu_0: bool = False          # Use μ₀ joint market availability

    def get_initial_vector(self) -> np.ndarray:
        """
        Get initial values as numpy array in parameter order.

        Returns
        -------
        np.ndarray
            Initial values vector
        """
        return np.array([self.initial_values[name] for name in self.all_param_names])

    def is_ac2013(self) -> bool:
        """
        Check if this specification uses Aaberge-Colombino (2013) style.
        
        Returns
        -------
        bool
            True if model_version is "AC2013"
        """
        return self.model_version == "AC2013"

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

    def has_couples_gender_specific_params(self) -> bool:
        """
        Check if specification includes gender-specific couples parameters.

        Returns
        -------
        bool
            True if couples gender-specific parameters are present
        """
        # Check for existence of _m or _f suffixed leisure parameters
        return any(name.endswith('_m') or name.endswith('_f')
                   for name in self.all_param_names)

    def get_couples_param_map(self) -> Dict[str, str]:
        """
        Get mapping from singles parameter names to couples-specific parameter names.

        For couples estimation with gender-specific parameters, this maps:
        - Male: base param name -> param_name_m
        - Female: base param name -> param_name_f

        Returns
        -------
        dict
            Mapping like {'beta_l0_male': 'beta_l0_m', 'beta_l0_female': 'beta_l0_f', ...}
        """
        if not self.has_couples_gender_specific_params():
            return {}

        param_map = {}

        # Map leisure intercept
        if self.utility_leisure_intercept in self.all_param_names:
            param_map[f"{self.utility_leisure_intercept}_male"] = f"{self.utility_leisure_intercept}_m"
            param_map[f"{self.utility_leisure_intercept}_female"] = f"{self.utility_leisure_intercept}_f"

        # Map leisure shifters
        for shifter in self.utility_leisure_shifters:
            coef = shifter["coefficient"]
            # Skip n_children for males
            if not (shifter.get("gender_specific") and shifter["variable"] == "n_children"):
                param_map[f"{coef}_male"] = f"{coef}_m"
            param_map[f"{coef}_female"] = f"{coef}_f"        # Map leisure theta
        if self.utility_leisure_theta:
            param_map[f"{self.utility_leisure_theta}_male"] = f"{self.utility_leisure_theta}_m"
            param_map[f"{self.utility_leisure_theta}_female"] = f"{self.utility_leisure_theta}_f"

        return param_map
    
    def is_ac2013(self) -> bool:
        """
        Check if this specification uses A-C 2013 style.
        
        Returns
        -------
        bool
            True if model_version is "AC2013"
        """
        return self.model_version == "AC2013"
    
    def get_ac2013_features(self) -> Dict[str, bool]:
        """
        Get dictionary of which A-C 2013 features are enabled.
        
        Returns
        -------
        dict
            Feature name -> enabled status
        """
        return {
            'use_log_age': self.ac2013_use_log_age,
            'children_age_groups': self.ac2013_children_age_groups,
            'experience_in_wage': self.ac2013_experience_in_wage,
            'couples_cross_leisure': self.ac2013_couples_cross_leisure,
            'couples_mu_0': self.ac2013_couples_mu_0
        }


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
        If specification is invalid    """
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info(f"Parsing specification: {yaml_path}")
    logger.info("="*80)
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"Specification file not found: {yaml_path}")
    
    # Load YAML (with explicit UTF-8 encoding for Unicode chars like θ, μ)
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Check for model version (NEW: AC2013 support)
    model_version = config.get("model_version", "legacy")
    if model_version not in ["legacy", "AC2013"]:
        logger.warning(f"Unknown model_version '{model_version}', treating as 'legacy'")
        model_version = "legacy"
    
    logger.info(f"Model version: {model_version}")

    # Extract metadata - handle both old and new YAML formats
    spec_meta = config.get("specification", {})
    name = spec_meta.get("name", config.get("name", "unknown"))
    description = spec_meta.get("description", config.get("description", ""))
    wage_spec = spec_meta.get("wage_spec", config.get("wage_spec", "fw"))

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

    # Parse initial values - support both flat and nested AC2013 formats
    initial_values = config.get("initial_values", {})
    bounds = {}
    
    if not initial_values and model_version == "AC2013":
        # AC2013 format: extract init/bounds from nested 'parameters' section
        logger.info("AC2013 format detected - extracting init/bounds from nested structure")
        initial_values, bounds = _extract_ac2013_parameters(config)
    
    if not initial_values:
        logger.warning("No initial values specified in YAML")

    # Parse bounds from optimization section (may override nested bounds)
    opt_config = config.get("optimization", {})
    bounds = opt_config.get("bounds", {})    # Parse optimization settings
    opt_method = opt_config.get("method", "L-BFGS-B")
    opt_analytical_gradient = opt_config.get("analytical_gradient", True)
    opt_max_iterations = opt_config.get("max_iterations", 10000)
    opt_tolerance = float(opt_config.get("tolerance", 1e-9))
    opt_gradient_tolerance = float(opt_config.get("gradient_tolerance", 1e-6))  # NEW
    opt_display = opt_config.get("disp", False)  # NEW
    opt_iprint = int(opt_config.get("iprint", -1))  # NEW

    # Parse gradient verification settings
    grad_verify = config.get('gradient_verification', {})

    # Build parameter list (order matters!)
    # For AC2013, use extracted parameter names; for legacy, build from spec
    if model_version == "AC2013" and initial_values:
        # AC2013: parameter names come from the extracted initial_values
        all_param_names = list(initial_values.keys())
        logger.info(f"AC2013: Using {len(all_param_names)} parameters from YAML")
    else:
        # Legacy: build parameter list from spec structure
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
        opt_tolerance=opt_tolerance,
        opt_gradient_tolerance=opt_gradient_tolerance,  # NEW
        opt_display_convergence=opt_display,  # NEW
        opt_iprint=opt_iprint,  # NEW
        grad_verify_enabled=grad_verify.get('enabled', False),
        grad_verify_method=grad_verify.get('method', 'central'),
        grad_verify_epsilon=float(grad_verify.get('epsilon', 1e-7)),
        grad_verify_tolerance=float(grad_verify.get('tolerance', 1e-4)),
        grad_verify_at_init=grad_verify.get('check_at_init', True),
        grad_verify_random_points=int(grad_verify.get('check_random_points', 0)),
        grad_verify_seed=int(grad_verify.get('random_seed', 42)),
        grad_verify_verbose=grad_verify.get('verbose', False),
        # NEW: AC2013 settings
        model_version=model_version,
        ac2013_use_log_age=(model_version == "AC2013"),
        ac2013_children_age_groups=(model_version == "AC2013"),
        ac2013_experience_in_wage=(model_version == "AC2013"),
        ac2013_couples_cross_leisure=(model_version == "AC2013" and 'alpha_ll' in all_param_names),
        ac2013_couples_mu_0=(model_version == "AC2013" and 'mu_0' in all_param_names),
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

    # ==========================================================================

    # FULLY SEPARATE 4-GROUP ARCHITECTURE
    # ==========================================================================

    # We have 4 distinct groups with their own preference parameters:
    # 1. Singles Male (_sm suffix)
    # 2. Singles Female (_sf suffix)
    # 3. Couples Male (_m suffix)
    # 4. Couples Female (_f suffix)
    #
    # SHARED parameters (all groups):
    # - Hours opportunity (beta_work, beta_pt1, beta_pt2, beta_ft, beta_gsur, beta_work_educL, beta_work_educH)
    # - Wage opportunity (beta_w0, beta_w_educL, beta_w_educH, beta_pexp, beta_pexp2, sigma)
    #
    # COUPLES ONLY parameters:
    # - Household consumption (beta_c, theta_c)
    # - Interaction term (beta_interact)
    # ==========================================================================

    # GROUP 1: Singles Male - Leisure preferences (_sm suffix)
    singles_male_params = [
        f"{utility_leisure_intercept}_sm",  # beta_l0_sm
    ]
    for shifter in utility_leisure_shifters:
        # Skip n_children for males (only for females)
        if shifter.get("gender_specific") and shifter["variable"] == "n_children":
            continue
        singles_male_params.append(f"{shifter['coefficient']}_sm")

    singles_male_params.append(f"{utility_consumption_coef}_sm")  # beta_c_sm

    if utility_form == "box_cox":
        if utility_leisure_theta:
            singles_male_params.append(f"{utility_leisure_theta}_sm")  # theta_l_sm
        if utility_consumption_theta:
            singles_male_params.append(f"{utility_consumption_theta}_sm")  # theta_c_sm

    params.extend(singles_male_params)

    # GROUP 2: Singles Female - Leisure preferences (_sf suffix)
    singles_female_params = [
        f"{utility_leisure_intercept}_sf",  # beta_l0_sf
    ]
    for shifter in utility_leisure_shifters:
        singles_female_params.append(f"{shifter['coefficient']}_sf")

    singles_female_params.append(f"{utility_consumption_coef}_sf")  # beta_c_sf

    if utility_form == "box_cox":
        if utility_leisure_theta:
            singles_female_params.append(f"{utility_leisure_theta}_sf")  # theta_l_sf
        if utility_consumption_theta:
            singles_female_params.append(f"{utility_consumption_theta}_sf")  # theta_c_sf

    params.extend(singles_female_params)

    # GROUP 3: Couples Male - Leisure preferences (_m suffix)
    couples_male_params = [
        f"{utility_leisure_intercept}_m",  # beta_l0_m
    ]
    for shifter in utility_leisure_shifters:
        # Skip n_children for males (only for females)
        if shifter.get("gender_specific") and shifter["variable"] == "n_children":
            continue
        couples_male_params.append(f"{shifter['coefficient']}_m")

    if utility_form == "box_cox" and utility_leisure_theta:
        couples_male_params.append(f"{utility_leisure_theta}_m")  # theta_l_m

    params.extend(couples_male_params)

    # GROUP 4: Couples Female - Leisure preferences (_f suffix)
    couples_female_params = [
        f"{utility_leisure_intercept}_f",  # beta_l0_f
    ]
    for shifter in utility_leisure_shifters:
        couples_female_params.append(f"{shifter['coefficient']}_f")

    if utility_form == "box_cox" and utility_leisure_theta:
        couples_female_params.append(f"{utility_leisure_theta}_f")  # theta_l_f

    params.extend(couples_female_params)

    # COUPLES HOUSEHOLD: Consumption (shared for couples, no suffix)
    params.append(utility_consumption_coef)  # beta_c
    if utility_form == "box_cox" and utility_consumption_theta:
        params.append(utility_consumption_theta)  # theta_c

    # SHARED OPPORTUNITY: Hours parameters (all groups)
    for shifter in hours_shifters:
        params.append(shifter["coefficient"])

    # SHARED OPPORTUNITY: Wage parameters (all groups)
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

    # COUPLES ONLY: Interaction term
    if couples_interaction_coef:
        params.append(couples_interaction_coef)

    # Check for duplicates
    if len(params) != len(set(params)):
        duplicates = [p for p in params if params.count(p) > 1]
        raise ValueError(f"Duplicate parameter names found: {set(duplicates)}")

    return params


def _extract_ac2013_parameters(config: Dict) -> Tuple[Dict[str, float], Dict[str, Tuple[float, float]]]:
    """
    Extract initial values and bounds from AC2013 nested YAML structure.
    
    AC2013 format uses nested sections like singles/preference/consumption with:
      param_name:
        init: value
        bounds: [lower, upper]
        description: "..."
    
    Parameters
    ----------
    config : dict
        Full YAML config
        
    Returns
    -------
    initial_values : dict
        Parameter name -> initial value
    bounds : dict
        Parameter name -> (lower, upper)
    """
    initial_values = {}
    bounds = {}
    
    def extract_from_section(section: Dict, prefix: str = ""):
        """Recursively extract parameters from nested sections."""
        if not isinstance(section, dict):
            return
        for key, value in section.items():
            if isinstance(value, dict):
                if 'init' in value:
                    # This is a parameter definition
                    param_name = key
                    initial_values[param_name] = float(value['init'])
                    if 'bounds' in value:
                        b = value['bounds']
                        bounds[param_name] = (float(b[0]), float(b[1]))
                else:
                    # Nested section - recurse
                    extract_from_section(value, key)
    
    # Look in singles and couples sections
    for section_name in ['singles', 'couples']:
        section = config.get(section_name, {})
        extract_from_section(section)
    
    # Also look in top-level parameters section if present
    if 'parameters' in config:
        extract_from_section(config['parameters'])
    
    return initial_values, bounds


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
        raise FileNotFoundError(f"Initial values file not found: {csv_path}")    # Check if it's a JSON file
    if csv_path.suffix.lower() == '.json':
        with open(csv_path, 'r') as f:
            data = json.load(f)

        # NEW FORMAT: Check for 'results' key (enhanced estimation output)
        if "results" in data:
            init_dict = {}
            # Collect all parameters from all groups (support joint, singles_male, etc.)
            for group_name, group_data in data['results'].items():
                if isinstance(group_data, dict) and 'parameters' in group_data:
                    params = group_data.get('parameters', {})
                    init_dict.update(params)
            return init_dict

        # OLD FORMAT: Check for param_names and theta arrays
        elif "param_names" in data and "theta" in data:
            # Strip hierarchical prefixes like 'sm.pref.' from old format
            clean_names = []
            for name in data["param_names"]:
                # Remove prefixes: sm.pref.beta_l0 → beta_l0
                if '.' in name:
                    clean_name = name.split('.')[-1]
                else:
                    clean_name = name
                clean_names.append(clean_name)
            return dict(zip(clean_names, data["theta"]))

        else:
            raise ValueError("JSON must have either 'results' dict or 'param_names'+'theta' arrays")
    
    # Otherwise treat as CSV
    df = pd.read_csv(csv_path)

    # Support both 'parameter_name' and 'parameter' column names
    param_col = None
    if "parameter_name" in df.columns:
        param_col = "parameter_name"
    elif "parameter" in df.columns:
        param_col = "parameter"
    else:
        raise ValueError("CSV must have column 'parameter_name' or 'parameter'")

    if "value" not in df.columns:
        raise ValueError("CSV must have column 'value'")

    return dict(zip(df[param_col], df["value"]))


def find_latest_results(
    search_dirs: List[Path],
    results_filename: str = "estimation_results.json"
) -> Optional[Path]:
    """
    Find the most recent estimation results file across multiple directories.
    
    Searches in the specified directories and their subdirectories for
    results files, returning the path to the most recently modified one.
    
    Parameters
    ----------
    search_dirs : List[Path]
        Directories to search for results files
    results_filename : str
        Name of the results file to look for (default: estimation_results.json)
        
    Returns
    -------
    Optional[Path]
        Path to the most recent results file, or None if not found
    """
    import os
    
    logger = logging.getLogger(__name__)
    candidates = []
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        # Search recursively for results files
        for root, dirs, files in os.walk(search_dir):
            if results_filename in files:
                results_path = Path(root) / results_filename
                mtime = results_path.stat().st_mtime
                candidates.append((results_path, mtime))
                
    if not candidates:
        logger.info("No previous estimation results found")
        return None
        
    # Sort by modification time (newest first)
    candidates.sort(key=lambda x: x[1], reverse=True)
    latest_path = candidates[0][0]
    
    logger.info(f"Found {len(candidates)} previous results file(s)")
    logger.info(f"Latest: {latest_path}")
    
    return latest_path


def load_warm_start_values(
    spec: 'EstimationSpec',
    results_path: Optional[Path] = None,
    search_dirs: Optional[List[Path]] = None,
    default_value: float = 0.0
) -> Tuple[np.ndarray, Dict[str, str]]:
    """
    Load initial values from previous results with fallback to defaults.
    
    For parameters that exist in both the current specification and the
    previous results, uses the estimated values. For new parameters,
    uses the default value from the spec or the provided default_value.
    
    Parameters
    ----------
    spec : EstimationSpec
        Current specification with parameter names
    results_path : Optional[Path]
        Explicit path to results JSON file. If None, auto-finds latest.
    search_dirs : Optional[List[Path]]
        Directories to search if results_path is None
    default_value : float
        Default value for new parameters not in previous results (default: 0.0)
        
    Returns
    -------
    Tuple[np.ndarray, Dict[str, str]]
        - Initial values vector
        - Dictionary mapping parameter names to their source ('previous', 'spec_default', 'fallback_default')
    """
    import json
    
    logger = logging.getLogger(__name__)
    
    # Find results file if not explicitly provided
    if results_path is None and search_dirs is not None:
        results_path = find_latest_results(search_dirs)
    
    # Load previous parameters if available
    prev_params = {}
    if results_path is not None and results_path.exists():
        try:
            prev_params = load_custom_initial_values(results_path)
            logger.info(f"Loaded {len(prev_params)} parameters from: {results_path}")
        except Exception as e:
            logger.warning(f"Failed to load previous results: {e}")
            prev_params = {}
    
    # Build initial values vector
    theta_init = np.zeros(len(spec.all_param_names))
    sources = {}
    
    n_from_prev = 0
    n_from_spec = 0
    n_from_default = 0
    
    for i, param_name in enumerate(spec.all_param_names):
        if param_name in prev_params:
            # Use value from previous estimation
            theta_init[i] = prev_params[param_name]
            sources[param_name] = 'previous'
            n_from_prev += 1
        elif param_name in spec.initial_values and spec.initial_values[param_name] != 0.0:
            # Use spec default (if non-zero, meaning it was explicitly set)
            theta_init[i] = spec.initial_values[param_name]
            sources[param_name] = 'spec_default'
            n_from_spec += 1
        else:
            # Use fallback default
            theta_init[i] = default_value
            sources[param_name] = 'fallback_default'
            n_from_default += 1
    
    logger.info(f"Initial values: {n_from_prev} from previous, "
                f"{n_from_spec} from spec, {n_from_default} from fallback default ({default_value})")
    
    # Log which parameters are new
    if n_from_default > 0 or n_from_spec > 0:
        new_params = [p for p, s in sources.items() if s != 'previous']
        if new_params and len(new_params) <= 20:
            logger.info(f"New/default parameters: {new_params}")
        elif new_params:
            logger.info(f"New/default parameters: {new_params[:10]} ... and {len(new_params)-10} more")
    
    return theta_init, sources


# ==============================================================================
# End of estimation_spec_parser.py
# ==============================================================================
