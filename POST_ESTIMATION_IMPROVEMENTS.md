# Post-Estimation Report Improvements

**Date:** 2026-01-28
**File:** `scripts/enhanced/RURO_post_estimation_styled.py`

---

## Summary of Requested Changes

1. ✅ Add number of iterations to elapsed time section (4th component)
2. ✅ Flip indifference curve axes (consumption on y-axis, leisure on x-axis)
3. ✅ Make Model Specification sections specification-agnostic
4. ✅ Add histogram plots for observed vs predicted hours distribution
5. ✅ Add curve/histogram plots for observed vs predicted wage distribution

---

## Implementation Details

### 1. Add Number of Iterations to Elapsed Time Section

**Current location:** Lines 1737-1757

**Changes needed:**

#### A. Add `n_iterations` parameter to function signature (line 1564):
```python
def generate_html_report_styled(
    parsed_params: ParsedParameters,
    fit_results: Dict[str, Dict[str, Any]],
    output_path: Path,
    fit_stats: Dict[str, float] = None,
    plot_paths: Dict[str, Path] = None,
    mu_results: Dict[str, Dict[str, Any]] = None,
    elasticities_df: pd.DataFrame = None,
    muc_analysis: List[Dict[str, Any]] = None,
    estimation_time_seconds: float = None,
    post_estimation_time_seconds: float = None,
    total_elapsed_seconds: float = None,
    n_iterations: int = None,  # NEW PARAMETER
    prob_diagnostics: Dict[str, Any] = None,
    bound_diagnostics: List[Dict[str, Any]] = None,
    hessian_diagnostics: Dict[str, Any] = None,
) -> Path:
```

#### B. Update elapsed time section HTML (lines 1737-1757):
```python
# Elapsed time section
time_section = ""
if estimation_time_seconds is not None or post_estimation_time_seconds is not None or total_elapsed_seconds is not None or n_iterations is not None:
    time_section = f"""
<div class="time-box">
  <h4>⏱️ Elapsed Time & Iterations</h4>
  <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1em; text-align: center;">
    <div>
      <div style="font-size: 0.9em; opacity: 0.8;">Estimation</div>
      <div class="time-value">{format_time(estimation_time_seconds)}</div>
    </div>
    <div>
      <div style="font-size: 0.9em; opacity: 0.8;">Post-Estimation</div>
      <div class="time-value">{format_time(post_estimation_time_seconds)}</div>
    </div>
    <div>
      <div style="font-size: 0.9em; opacity: 0.8;">Total</div>
      <div class="time-value">{format_time(total_elapsed_seconds)}</div>
    </div>
    <div>
      <div style="font-size: 0.9em; opacity: 0.8;">Iterations</div>
      <div class="time-value">{n_iterations if n_iterations is not None else "N/A"}</div>
    </div>
  </div>
</div>
"""
```

#### C. Extract n_iterations from JSON (around line 3670):
```python
# Extract timing info from results
estimation_time = None
n_iterations = None  # NEW
if 'summary' in data:
    estimation_time = data['summary'].get('total_walltime_seconds')
    n_iterations = data['summary'].get('n_iterations')  # NEW
elif 'estimation_time_seconds' in data:
    estimation_time = data['estimation_time_seconds']
    n_iterations = data.get('n_iterations')  # NEW

# Also check in results for n_iterations if not found in summary
if n_iterations is None:
    results = data.get('results', {})
    for group_name, group_data in results.items():
        if 'n_iterations' in group_data:
            n_iterations = group_data.get('n_iterations')
            break
```

#### D. Pass n_iterations to function call (around line 3818):
```python
html_path = generate_html_report_styled(
    parsed_params=parsed,
    fit_results=fit_results,
    output_path=html_path,
    fit_stats=fit_stats,
    plot_paths=plot_paths,
    mu_results=mu_results,
    elasticities_df=elasticities_df,
    muc_analysis=muc_analysis,
    estimation_time_seconds=estimation_time,
    post_estimation_time_seconds=post_estimation_time,
    total_elapsed_seconds=total_time if estimation_time else None,
    n_iterations=n_iterations,  # NEW
    prob_diagnostics=prob_diagnostics,
    bound_diagnostics=bound_diagnostics,
    hessian_diagnostics=hessian_diagnostics,
)
```

---

### 2. Flip Indifference Curve Axes

**Current location:** Lines 845-870 (function `plot_utility_contours`)

**Change:** Swap `C` and `L` in plotting commands:

```python
# BEFORE (line 850-856):
fig, ax = plt.subplots(figsize=(8, 6))
cf = ax.contourf(C, L, U, levels=20, cmap='RdYlGn', alpha=0.7)
plt.colorbar(cf, ax=ax, label='Utility')
cs = ax.contour(C, L, U, levels=levels, colors='black', linewidths=1.0)
ax.clabel(cs, inline=True, fontsize=9)

ax.set_xlabel('Normalized Consumption (c/c̄)')
ax.set_ylabel('Normalized Leisure (l/l̄)')

# AFTER (swap axes):
fig, ax = plt.subplots(figsize=(8, 6))
cf = ax.contourf(L, C, U.T, levels=20, cmap='RdYlGn', alpha=0.7)  # Swapped C,L → L,C and transpose U
plt.colorbar(cf, ax=ax, label='Utility')
cs = ax.contour(L, C, U.T, levels=levels, colors='black', linewidths=1.0)  # Swapped and transposed
ax.clabel(cs, inline=True, fontsize=9)

ax.set_xlabel('Normalized Leisure (l/l̄)')  # Swapped
ax.set_ylabel('Normalized Consumption (c/c̄)')  # Swapped
```

**Important:** Need to transpose U matrix when swapping axes: `U.T`

---

### 3. Make Model Specification Sections Specification-Agnostic

**Current locations:**
- Hours Opportunity: Lines 1813-1831
- Wage Equation: Lines 1781-1810

**Approach:** Instead of hardcoded equations, dynamically build from actual parameters in `parsed_params`.

#### A. Replace hardcoded hours opportunity section with dynamic builder:

```python
def build_hours_opportunity_html_dynamic(parsed_params: ParsedParameters) -> str:
    """
    Build hours opportunity HTML dynamically from actual estimated parameters.
    """
    hours_params = {}

    # Collect all hours-related parameters from all groups
    for group in parsed_params.groups:
        params = parsed_params.get_all_params_for_group(group)
        for pname, pvalue in params.items():
            if any(keyword in pname.lower() for keyword in ['beta_work', 'beta_pt1', 'beta_pt2', 'beta_ft', 'beta_gsur', 'pi_']):
                hours_params[pname] = pvalue

    if not hours_params:
        return ""  # No hours opportunity parameters found

    # Build symbolic equation
    symbolic_terms = []
    numerical_terms = []

    # Group parameters by type
    for pname in sorted(hours_params.keys()):
        pvalue = hours_params[pname]

        # Create symbolic and numerical representations
        if 'beta_work' in pname and 'educL' not in pname and 'educH' not in pname and 'female' not in pname:
            symbolic_terms.append("β<sub>work</sub> · I(h>0)")
            numerical_terms.append(f"{pvalue:.4f} · I(h>0)")
        elif 'beta_pt1' in pname or 'pi_pt1' in pname:
            symbolic_terms.append("β<sub>pt1</sub> · I(h∈[18.5,20.5])")
            numerical_terms.append(f"{pvalue:+.4f} · I(h∈[18.5,20.5])")
        elif 'beta_pt2' in pname or 'pi_pt2' in pname:
            symbolic_terms.append("β<sub>pt2</sub> · I(h∈[29.5,30.5])")
            numerical_terms.append(f"{pvalue:+.4f} · I(h∈[29.5,30.5])")
        elif 'beta_ft' in pname or 'pi_ft' in pname:
            symbolic_terms.append("β<sub>ft</sub> · I(h∈[37.5,40.5])")
            numerical_terms.append(f"{pvalue:+.4f} · I(h∈[37.5,40.5])")
        elif 'beta_gsur' in pname:
            symbolic_terms.append("β<sub>gsur</sub> · gsur")
            numerical_terms.append(f"{pvalue:+.4f} · gsur")
        elif 'educL' in pname:
            symbolic_terms.append("β<sub>work,educL</sub> · educL")
            numerical_terms.append(f"{pvalue:+.4f} · educL")
        elif 'educH' in pname:
            symbolic_terms.append("β<sub>work,educH</sub> · educH")
            numerical_terms.append(f"{pvalue:+.4f} · educH")
        elif 'female' in pname:
            symbolic_terms.append("β<sub>work,female</sub> · female")
            numerical_terms.append(f"{pvalue:+.4f} · female")
        elif 'couple' in pname:
            symbolic_terms.append("β<sub>work,couple</sub> · couple")
            numerical_terms.append(f"{pvalue:+.4f} · couple")

    if not symbolic_terms:
        return ""

    symbolic_eq = " + ".join(symbolic_terms)
    numerical_eq = " + ".join(numerical_terms)

    return f"""
    <div class="stats-box" style="margin-top: 1em;">
        <h4>Hours Opportunity Function</h4>
        <div class="math-block symbolic">
            log h(h|X) = {symbolic_eq}
        </div>
        <div class="math-block numerical" style="margin-top: 1em;">
            log h(h|X) = {numerical_eq}
        </div>
    </div>
    """
```

#### B. Replace hardcoded wage equation section with dynamic builder:

```python
def build_wage_equation_html_dynamic(parsed_params: ParsedParameters) -> str:
    """
    Build wage equation HTML dynamically from actual estimated parameters.
    """
    wage_params = {}

    # Collect all wage-related parameters
    for group in parsed_params.groups:
        params = parsed_params.get_all_params_for_group(group)
        for pname, pvalue in params.items():
            if any(keyword in pname.lower() for keyword in ['beta_w0', 'beta_w_', 'beta_pexp', 'sigma']):
                wage_params[pname] = pvalue

    if not wage_params:
        return ""  # No wage parameters found

    # Build Mincer equation
    symbolic_terms = []
    numerical_terms = []

    for pname in sorted(wage_params.keys()):
        pvalue = wage_params[pname]

        if pname == 'beta_w0' or 'beta_w0_' in pname:
            symbolic_terms.append("β<sub>w0</sub>")
            numerical_terms.append(f"{pvalue:.4f}")
        elif 'beta_w_educL' in pname:
            symbolic_terms.append("β<sub>educL</sub> · educL")
            numerical_terms.append(f"{pvalue:+.4f} · educL")
        elif 'beta_w_educH' in pname:
            symbolic_terms.append("β<sub>educH</sub> · educH")
            numerical_terms.append(f"{pvalue:+.4f} · educH")
        elif 'beta_pexp2' in pname:
            symbolic_terms.append("β<sub>exp²</sub> · (exp/10)²")
            numerical_terms.append(f"{pvalue:+.4f} · (exp/10)²")
        elif 'beta_pexp' in pname:
            symbolic_terms.append("β<sub>exp</sub> · (exp/10)")
            numerical_terms.append(f"{pvalue:+.4f} · (exp/10)")

    # Find sigma
    sigma_val = wage_params.get('sigma', wage_params.get('sigma_w', 0.0))

    if not symbolic_terms:
        return ""

    symbolic_eq = " + ".join(symbolic_terms)
    numerical_eq = " + ".join(numerical_terms)

    return f"""
    <div class="stats-box" style="margin-top: 1em;">
        <h4>Log-Wage Equation (Mincer Style)</h4>
        <div class="math-block symbolic">
            log(w) = {symbolic_eq}
            <br>
            ε ~ N(0, σ²) with σ = {sigma_val:.4f}
        </div>
        <div class="math-block numerical" style="margin-top: 1em;">
            log(w) = {numerical_eq}
        </div>
    </div>
    """
```

#### C. Call these functions instead of hardcoded HTML (lines 1764-1831):

```python
# Replace lines 1764-1831 with:
wage_equation_html = build_wage_equation_html_dynamic(parsed_params)
hours_opportunity_html = build_hours_opportunity_html_dynamic(parsed_params)
```

---

### 4. Add Histogram Plots for Observed vs Predicted Hours Distribution

**New function to add after line 1150:**

```python
def plot_hours_distribution_comparison(
    parsed_params: ParsedParameters,
    mnl_base: Path,
    output_dir: Path,
    prefix: str = ''
) -> Dict[str, Path]:
    """
    Create histogram plots comparing observed vs predicted hours distributions.

    Returns paths to generated plots by group.
    """
    if not MATPLOTLIB_AVAILABLE:
        return {}

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_paths = {}

    # Hours bins matching the specification
    bins = [0, 10, 18.5, 20.5, 25, 29.5, 30.5, 35, 37.5, 40.5, 45, 50, 60, 70]
    bin_labels = ['0', '10', '18.5-20.5\n(PT1)', '20.5', '25', '29.5-30.5\n(PT2)',
                  '30.5', '35', '37.5-40.5\n(FT)', '40.5', '45', '50', '60+']

    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'singles_male': 'Single Males', 'singles_female': 'Single Females',
        'couples': 'Couples', 'cou': 'Couples'
    }

    # Load data
    singles_path = Path(str(mnl_base) + '__singles.parquet')
    couples_path = Path(str(mnl_base) + '__couples.parquet')

    groups_data = {}
    if singles_path.exists():
        df_singles = pd.read_parquet(singles_path)
        # Split by gender
        if 'female' in df_singles.columns:
            groups_data['sm'] = df_singles[df_singles['female'] == 0]
            groups_data['sf'] = df_singles[df_singles['female'] == 1]
        else:
            groups_data['singles'] = df_singles

    if couples_path.exists():
        df_couples = pd.read_parquet(couples_path)
        groups_data['couples'] = df_couples

    # Create plots for each group
    for group_key, df_group in groups_data.items():
        try:
            # Get observed hours (from chosen alternatives)
            obs_hours = df_group[df_group['actual_choice'] == 1]['lhw'].values

            # Get predicted hours (probability-weighted)
            # For each individual, compute expected hours = sum(P_j * h_j)
            individuals = df_group.groupby('idhh')
            pred_hours_list = []

            for idhh, group_df in individuals:
                probs = group_df['choice_prob'].values if 'choice_prob' in group_df.columns else np.ones(len(group_df)) / len(group_df)
                hours = group_df['lhw'].values
                expected_hours = np.sum(probs * hours)
                pred_hours_list.append(expected_hours)

            pred_hours = np.array(pred_hours_list)

            # Create histogram comparison
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

            # Observed distribution
            ax1.hist(obs_hours, bins=bins, alpha=0.7, color='blue', edgecolor='black', density=True)
            ax1.set_xlabel('Weekly Hours')
            ax1.set_ylabel('Density')
            ax1.set_title(f'Observed Hours Distribution\n{group_labels.get(group_key, group_key)}')
            ax1.grid(True, alpha=0.3)
            ax1.set_xlim(0, 70)

            # Predicted distribution
            ax2.hist(pred_hours, bins=bins, alpha=0.7, color='green', edgecolor='black', density=True)
            ax2.set_xlabel('Weekly Hours')
            ax2.set_ylabel('Density')
            ax2.set_title(f'Predicted Hours Distribution\n{group_labels.get(group_key, group_key)}')
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(0, 70)

            # Add participation rates as text
            obs_part_rate = (obs_hours > 0).mean() * 100
            pred_part_rate = (pred_hours > 0).mean() * 100
            ax1.text(0.05, 0.95, f'Participation: {obs_part_rate:.1f}%',
                    transform=ax1.transAxes, verticalalignment='top')
            ax2.text(0.05, 0.95, f'Participation: {pred_part_rate:.1f}%',
                    transform=ax2.transAxes, verticalalignment='top')

            fig.tight_layout()
            output_path = output_dir / f'{prefix}{group_key}_hours_distribution.png'
            fig.savefig(output_path, dpi=150)
            plt.close(fig)
            plot_paths[f'{group_key}_hours_dist'] = output_path

        except Exception as e:
            LOGGER.error(f"Error creating hours distribution plot for {group_key}: {e}")

    return plot_paths
```

**Call this function around line 3780 (after other plotting functions):**

```python
# After plot_utility_contours and other plots:
if mnl_base:
    hours_dist_plots = plot_hours_distribution_comparison(parsed, mnl_base, plot_output_dir, prefix)
    plot_paths.update(hours_dist_plots)
```

---

### 5. Add Wage Distribution Plots (Observed vs Predicted)

**New function to add after the hours distribution function:**

```python
def plot_wage_distribution_comparison(
    parsed_params: ParsedParameters,
    mnl_base: Path,
    output_dir: Path,
    prefix: str = ''
) -> Dict[str, Path]:
    """
    Create smooth density plots comparing observed vs predicted wage distributions.

    Uses kernel density estimation for smooth curves.
    Returns paths to generated plots by group.
    """
    if not MATPLOTLIB_AVAILABLE:
        return {}

    try:
        from scipy.stats import gaussian_kde
    except ImportError:
        LOGGER.warning("scipy not available for KDE, skipping wage distribution plots")
        return {}

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_paths = {}

    group_labels = {
        'sm': 'Single Males', 'sf': 'Single Females',
        'singles_male': 'Single Males', 'singles_female': 'Single Females',
        'couples_m': 'Males in Couples', 'couples_f': 'Females in Couples'
    }

    # Load data
    singles_path = Path(str(mnl_base) + '__singles.parquet')
    couples_path = Path(str(mnl_base) + '__couples.parquet')

    groups_data = {}
    if singles_path.exists():
        df_singles = pd.read_parquet(singles_path)
        # Filter only working alternatives
        df_singles_working = df_singles[df_singles['working'] == 1]

        if 'female' in df_singles_working.columns and 'log_wage' in df_singles_working.columns:
            groups_data['sm'] = df_singles_working[df_singles_working['female'] == 0]
            groups_data['sf'] = df_singles_working[df_singles_working['female'] == 1]

    if couples_path.exists():
        df_couples = pd.read_parquet(couples_path)
        df_couples_working = df_couples[df_couples['working_male'] == 1]
        if 'log_wage_male' in df_couples_working.columns:
            groups_data['couples_m'] = df_couples_working

        df_couples_working_f = df_couples[df_couples['working_female'] == 1]
        if 'log_wage_female' in df_couples_working_f.columns:
            groups_data['couples_f'] = df_couples_working_f

    # Create plots for each group
    for group_key, df_group in groups_data.items():
        try:
            # Determine wage column name
            if group_key == 'couples_m':
                wage_col = 'log_wage_male'
            elif group_key == 'couples_f':
                wage_col = 'log_wage_female'
            else:
                wage_col = 'log_wage'

            if wage_col not in df_group.columns:
                continue

            # Get observed wages (from chosen alternatives)
            obs_wages = df_group[df_group['actual_choice'] == 1][wage_col].values
            obs_wages = obs_wages[np.isfinite(obs_wages)]  # Remove NaN/Inf

            if len(obs_wages) < 10:
                continue  # Need sufficient data for KDE

            # Get predicted wages (probability-weighted sample)
            # Sample from the distribution using choice probabilities
            individuals = df_group.groupby('idhh')
            pred_wages_list = []

            for idhh, group_df in individuals:
                if wage_col not in group_df.columns:
                    continue

                probs = group_df['choice_prob'].values if 'choice_prob' in group_df.columns else np.ones(len(group_df)) / len(group_df)
                wages = group_df[wage_col].values

                # Remove NaN/Inf
                valid_mask = np.isfinite(wages) & np.isfinite(probs) & (probs > 0)
                if not valid_mask.any():
                    continue

                wages = wages[valid_mask]
                probs = probs[valid_mask]
                probs = probs / probs.sum()  # Renormalize

                # Sample one wage per individual using predicted probabilities
                sampled_wage = np.random.choice(wages, p=probs)
                pred_wages_list.append(sampled_wage)

            pred_wages = np.array(pred_wages_list)
            pred_wages = pred_wages[np.isfinite(pred_wages)]

            if len(pred_wages) < 10:
                continue

            # Create KDE for smooth density curves
            obs_kde = gaussian_kde(obs_wages)
            pred_kde = gaussian_kde(pred_wages)

            # Create wage grid for plotting
            wage_min = min(obs_wages.min(), pred_wages.min())
            wage_max = max(obs_wages.max(), pred_wages.max())
            wage_grid = np.linspace(wage_min, wage_max, 200)

            # Evaluate KDEs
            obs_density = obs_kde(wage_grid)
            pred_density = pred_kde(wage_grid)

            # Create plot
            fig, ax = plt.subplots(figsize=(10, 6))

            ax.plot(wage_grid, obs_density, label='Observed', color='blue', linewidth=2)
            ax.fill_between(wage_grid, obs_density, alpha=0.3, color='blue')

            ax.plot(wage_grid, pred_density, label='Predicted', color='green', linewidth=2, linestyle='--')
            ax.fill_between(wage_grid, pred_density, alpha=0.2, color='green')

            ax.set_xlabel('Log Hourly Wage')
            ax.set_ylabel('Density')
            ax.set_title(f'Wage Distribution: Observed vs Predicted\n{group_labels.get(group_key, group_key)}')
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Add mean values as text
            obs_mean = obs_wages.mean()
            pred_mean = pred_wages.mean()
            ax.text(0.05, 0.95,
                   f'Observed mean: {obs_mean:.3f}\nPredicted mean: {pred_mean:.3f}',
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            fig.tight_layout()
            output_path = output_dir / f'{prefix}{group_key}_wage_distribution.png'
            fig.savefig(output_path, dpi=150)
            plt.close(fig)
            plot_paths[f'{group_key}_wage_dist'] = output_path

        except Exception as e:
            LOGGER.error(f"Error creating wage distribution plot for {group_key}: {e}")

    return plot_paths
```

**Call this function after the hours distribution plots:**

```python
if mnl_base:
    hours_dist_plots = plot_hours_distribution_comparison(parsed, mnl_base, plot_output_dir, prefix)
    plot_paths.update(hours_dist_plots)

    wage_dist_plots = plot_wage_distribution_comparison(parsed, mnl_base, plot_output_dir, prefix)
    plot_paths.update(wage_dist_plots)
```

---

### 6. Display New Plots in HTML Report

**Add new section in HTML template (around line 2100, after existing plots):**

```python
# After utility indifference curves section, add:

# Hours Distribution Plots
hours_dist_plots_html = ""
hours_dist_images = [p for name, p in plot_paths.items() if '_hours_dist' in name]
if hours_dist_images:
    hours_dist_plots_html = '<h3>📊 Hours Distribution: Observed vs Predicted</h3><div class="plot-grid">'
    for plot_path in hours_dist_images:
        rel_path = plot_path.name
        hours_dist_plots_html += f'<div class="plot-item"><img src="{rel_path}" alt="Hours Distribution"></div>'
    hours_dist_plots_html += '</div>'

# Wage Distribution Plots
wage_dist_plots_html = ""
wage_dist_images = [p for name, p in plot_paths.items() if '_wage_dist' in name]
if wage_dist_images:
    wage_dist_plots_html = '<h3>💰 Wage Distribution: Observed vs Predicted</h3><div class="plot-grid">'
    for plot_path in wage_dist_images:
        rel_path = plot_path.name
        wage_dist_plots_html += f'<div class="plot-item"><img src="{rel_path}" alt="Wage Distribution"></div>'
    wage_dist_plots_html += '</div>'

# Insert these into the plots section (around line 2100):
plots_section += hours_dist_plots_html
plots_section += wage_dist_plots_html
```

---

## Summary of Files to Modify

1. **`scripts/enhanced/RURO_post_estimation_styled.py`** (main file):
   - Add `n_iterations` parameter and logic (5 locations)
   - Flip indifference curve axes (1 location, ~10 lines)
   - Replace hardcoded specification sections with dynamic builders (2 new functions + 1 replacement)
   - Add hours distribution plotting function (~80 lines)
   - Add wage distribution plotting function (~100 lines)
   - Update HTML template to include new plots (~20 lines)

**Total estimated changes:** ~250 lines of additions/modifications

---

## Testing Checklist

After implementing:

1. ✅ Run post-estimation and verify n_iterations appears in "Elapsed Time & Iterations" section
2. ✅ Check that indifference curves have leisure on x-axis and consumption on y-axis
3. ✅ Verify Hours Opportunity and Wage Equation sections show only estimated parameters
4. ✅ Confirm hours distribution histograms appear with observed vs predicted side-by-side
5. ✅ Confirm wage distribution density curves appear with observed vs predicted overlay
6. ✅ Test with different specifications (base, AC2013, v2, loc_empirical)

---

**Created by:** Claude Sonnet 4.5
**Date:** 2026-01-28
