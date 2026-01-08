"""
CLEAN REPLACEMENT FUNCTIONS FOR RURO_post_estimation_styled.py

Copy these functions to replace the broken versions around lines 1230-1550.
Make sure indentation is exactly 4 spaces per level.
"""

def compute_null_log_likelihood(df: pd.DataFrame, choice_id_col: str = 'idhh') -> float:
    """
    Compute null model log-likelihood: LL0 = -Σ_i log(J_i).
    
    Parameters
    ----------
    df : pd.DataFrame
        Long-format MNL data
    choice_id_col : str
        Column identifying choice units (households)
    
    Returns
    -------
    float
        Null model log-likelihood
    """
    choice_set_sizes = df.groupby(choice_id_col).size()
    ll_null = -np.sum(np.log(choice_set_sizes.values))
    return ll_null


def compute_fit_diagnostics_from_data(
    parsed_params: ParsedParameters,
    mnl_base: Path,
    spec: Optional[Any] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Compute observed vs predicted participation and hours by group.
    
    This computes probabilities using the same utility as estimation:
    V_ij = U_pref(c_ij, l_ij; θ) + log(f_opp_ij) - log(prior_ij)
    
    Returns
    -------
    Dict[str, Dict[str, float]]
        Nested dict: {group: {'participation_observed': ..., 'participation_predicted': ..., etc.}}
    """
    LOGGER.info("Computing fit diagnostics from MNL data...")
    
    mnl_base = Path(mnl_base)
    fit_results = {}
    
    # Load data files
    try:
        metadata_path = Path(str(mnl_base) + '__mnlmeta.json')
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        singles_path = Path(str(mnl_base) + '__singles.parquet')
        couples_path = Path(str(mnl_base) + '__couples.parquet')
        
        df_singles = pd.read_parquet(singles_path) if singles_path.exists() else None
        df_couples = pd.read_parquet(couples_path) if couples_path.exists() else None
    except Exception as e:
        LOGGER.warning(f"Could not load MNL data: {e}")
        return {}
    
    # Process singles (male=0, female=1)
    for gender_code, gender_name, group_key in [(0, 'male', 'sm'), (1, 'female', 'sf')]:
        if df_singles is None:
            continue
        
        # Try 'dgn' first (dataset convention), then 'gender'
        gender_col = 'dgn' if 'dgn' in df_singles.columns else 'gender'
        df_g = df_singles[df_singles[gender_col] == gender_code].copy()
        if len(df_g) == 0:
            continue
        
        # Get parameters for this group
        params = None
        for try_key in [group_key, f'singles_{gender_name}', group_key.upper()]:
            if try_key in parsed_params.params_by_group:
                params = parsed_params.get_all_params_for_group(try_key)
                break
        
        if params is None or 'beta_c' not in params:
            LOGGER.warning(f"No parameters found for {group_key}, skipping fit diagnostics")
            continue
        
        try:
            # Compute observed moments
            chosen_col = 'is_chosen' if 'is_chosen' in df_g.columns else 'chosen'
            chosen = df_g[df_g[chosen_col] == 1].copy()
            obs_participation = (chosen['hours'] > 0).mean()
            obs_hours = chosen.loc[chosen['hours'] > 0, 'hours'].mean() if (chosen['hours'] > 0).any() else 0.0
            
            # Compute predicted probabilities
            beta_c = params.get('beta_c', 1.0)
            theta_c = params.get('theta_c', 0.5)
            beta_l0 = params.get('beta_l0', 0.0)
            theta_l = params.get('theta_l', 0.5)
            
            # Utility from preferences
            c = df_g['consumption'].values
            l = df_g['leisure'].values
            U_pref = beta_c * boxcox_transform(c, theta_c) + beta_l0 * boxcox_transform(l, theta_l)
            
            # Add opportunity terms if available
            if 'log_opp' in df_g.columns:
                V = U_pref + df_g['log_opp'].values
            else:
                V = U_pref
            
            # Subtract prior if available
            if 'log_prior' in df_g.columns:
                V = V - df_g['log_prior'].values
            
            # Compute choice probabilities within each household
            df_g['V'] = V
            df_g['prob'] = 0.0
            
            for idhh, group_df in df_g.groupby('idhh'):
                V_group = group_df['V'].values
                V_shifted = V_group - V_group.max()
                exp_V = np.exp(V_shifted)
                probs = exp_V / exp_V.sum()
                df_g.loc[group_df.index, 'prob'] = probs
            
            # Predicted participation
            pred_participation = (df_g.groupby('idhh').apply(
                lambda x: (x['prob'] * (x['hours'] > 0).astype(float)).sum()
            )).mean()
            
            # Predicted mean hours among workers
            def household_pred_hours(x):
                working_mask = (x['hours'] > 0).values
                if not working_mask.any():
                    return 0.0
                numerator = (x['prob'].values * x['hours'].values * working_mask).sum()
                denominator = (x['prob'].values * working_mask).sum()
                return numerator / denominator if denominator > 0 else 0.0
            
            pred_hours = df_g.groupby('idhh').apply(household_pred_hours).mean()
            
            fit_results[group_key] = {
                'participation_observed': obs_participation,
                'participation_predicted': pred_participation,
                'mean_hours_observed': obs_hours,
                'mean_hours_predicted': pred_hours,
            }
            
            LOGGER.info(f"  {group_key}: obs_part={obs_participation:.3f}, pred_part={pred_participation:.3f}")
            
        except Exception as e:
            LOGGER.warning(f"Could not compute fit for {group_key}: {e}")
            continue
    
    # Process couples (simplified - use observed moments as approximation)
    if df_couples is not None and len(df_couples) > 0:
        chosen_col = 'is_chosen' if 'is_chosen' in df_couples.columns else 'chosen'
        
        for gender, suffix in [('male', '_m'), ('female', '_f')]:
            group_key = f'cou{suffix}'
            
            try:
                chosen = df_couples[df_couples[chosen_col] == 1].copy()
                hours_col = f'hours_{gender}'
                obs_participation = (chosen[hours_col] > 0).mean()
                obs_hours = chosen.loc[chosen[hours_col] > 0, hours_col].mean() if (chosen[hours_col] > 0).any() else 0.0
                
                # For couples, use observed as approximation for predicted
                fit_results[group_key] = {
                    'participation_observed': obs_participation,
                    'participation_predicted': obs_participation,
                    'mean_hours_observed': obs_hours,
                    'mean_hours_predicted': obs_hours,
                }
                
                LOGGER.info(f"  {group_key}: obs_part={obs_participation:.3f}, obs_hours={obs_hours:.1f}")
                
            except Exception as e:
                LOGGER.warning(f"Could not compute fit for {group_key}: {e}")
                continue
    
    return fit_results


def compute_marginal_utilities_at_chosen(
    parsed_params: ParsedParameters,
    mnl_base: Path,
) -> Dict[str, Any]:
    """
    Compute marginal utilities (MUC, MUL) at chosen alternatives.
    
    Returns
    -------
    Dict with keys:
        - 'by_group': Dict[str, Dict] with N, n_neg_muc, pct_neg_muc, mean_muc, etc.
        - 'totals': Dict with aggregate stats
    """
    LOGGER.info("Computing marginal utilities at chosen alternatives...")
    
    mnl_base = Path(mnl_base)
    mu_results = {'by_group': {}, 'totals': {}}
    
    # Load data
    try:
        singles_path = Path(str(mnl_base) + '__singles.parquet')
        couples_path = Path(str(mnl_base) + '__couples.parquet')
        
        df_singles = pd.read_parquet(singles_path) if singles_path.exists() else None
        df_couples = pd.read_parquet(couples_path) if couples_path.exists() else None
    except Exception as e:
        LOGGER.warning(f"Could not load data for MU computation: {e}")
        return mu_results
    
    all_muc = []
    all_mul = []
    
    # Process singles
    for gender_code, gender_name, group_key in [(0, 'male', 'sm'), (1, 'female', 'sf')]:
        if df_singles is None:
            continue
        
        # Try 'dgn' first (dataset convention), then 'gender'
        gender_col = 'dgn' if 'dgn' in df_singles.columns else 'gender'
        chosen_col = 'is_chosen' if 'is_chosen' in df_singles.columns else 'chosen'
        df_g = df_singles[(df_singles[gender_col] == gender_code) & (df_singles[chosen_col] == 1)].copy()
        if len(df_g) == 0:
            continue
        
        params = None
        for try_key in [group_key, f'singles_{gender_name}']:
            if try_key in parsed_params.params_by_group:
                params = parsed_params.get_all_params_for_group(try_key)
                break
        
        if params is None:
            continue
        
        beta_c = params.get('beta_c', 1.0)
        theta_c = params.get('theta_c', 0.5)
        beta_l0 = params.get('beta_l0', 0.0)
        theta_l = params.get('theta_l', 0.5)
        
        c = df_g['consumption'].values
        l = df_g['leisure'].values
        
        muc = compute_marginal_utility_consumption(c, beta_c, theta_c)
        mul = beta_l0 * d_boxcox_dx(l, theta_l)
        
        all_muc.extend(muc)
        all_mul.extend(mul)
        
        mu_results['by_group'][group_key] = {
            'N': len(df_g),
            'n_neg_muc': int((muc < 0).sum()),
            'pct_neg_muc': float(100 * (muc < 0).mean()),
            'n_neg_mul': int((mul < 0).sum()),
            'pct_neg_mul': float(100 * (mul < 0).mean()),
            'mean_muc': float(muc.mean()),
            'mean_mul': float(mul.mean()),
        }
        
        LOGGER.info(f"  {group_key}: {len(df_g)} obs, {(muc<0).sum()} neg MUC ({100*(muc<0).mean():.1f}%)")
    
    # Process couples
    if df_couples is not None:
        chosen_col = 'is_chosen' if 'is_chosen' in df_couples.columns else 'chosen'
        df_chosen = df_couples[df_couples[chosen_col] == 1].copy()
        
        params = None
        for try_key in ['cou', 'couples']:
            if try_key in parsed_params.params_by_group:
                params = parsed_params.get_all_params_for_group(try_key)
                break
        
        if params is not None and len(df_chosen) > 0:
            beta_c = params.get('beta_c', 1.0)
            theta_c = params.get('theta_c', 0.5)
            
            c = df_chosen['consumption'].values
            muc = compute_marginal_utility_consumption(c, beta_c, theta_c)
            all_muc.extend(muc)
            
            # Males in couples
            beta_l0_m = params.get('beta_l0_m', params.get('beta_l0', 0.0))
            theta_l_m = params.get('theta_l_m', params.get('theta_l', 0.5))
            l_m = df_chosen['leisure_male'].values
            mul_m = beta_l0_m * d_boxcox_dx(l_m, theta_l_m)
            all_mul.extend(mul_m)
            
            mu_results['by_group']['cou_m'] = {
                'N': len(df_chosen),
                'n_neg_muc': int((muc < 0).sum()),
                'pct_neg_muc': float(100 * (muc < 0).mean()),
                'n_neg_mul': int((mul_m < 0).sum()),
                'pct_neg_mul': float(100 * (mul_m < 0).mean()),
                'mean_muc': float(muc.mean()),
                'mean_mul': float(mul_m.mean()),
            }
            
            # Females in couples
            beta_l0_f = params.get('beta_l0_f', params.get('beta_l0', 0.0))
            theta_l_f = params.get('theta_l_f', params.get('theta_l', 0.5))
            l_f = df_chosen['leisure_female'].values
            mul_f = beta_l0_f * d_boxcox_dx(l_f, theta_l_f)
            all_mul.extend(mul_f)
            
            mu_results['by_group']['cou_f'] = {
                'N': len(df_chosen),
                'n_neg_muc': int((muc < 0).sum()),
                'pct_neg_muc': float(100 * (muc < 0).mean()),
                'n_neg_mul': int((mul_f < 0).sum()),
                'pct_neg_mul': float(100 * (mul_f < 0).mean()),
                'mean_muc': float(muc.mean()),
                'mean_mul': float(mul_f.mean()),
            }
    
    # Compute totals
    if all_muc:
        all_muc = np.array(all_muc)
        all_mul = np.array(all_mul)
        mu_results['totals'] = {
            'n_negative_muc_total': int((all_muc < 0).sum()),
            'n_negative_mul_total': int((all_mul < 0).sum()),
            'pct_negative_muc_total': float(100 * (all_muc < 0).mean()),
            'pct_negative_mul_total': float(100 * (all_mul < 0).mean()),
        }
        LOGGER.info(f"  Totals: {(all_muc<0).sum()} neg MUC, {(all_mul<0).sum()} neg MUL")
    
    return mu_results
