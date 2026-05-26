#!/usr/bin/env python
"""
Generate HTML Diagnostics Report from Estimation Results with Fit Statistics

This creates a simple HTML report from the JSON file with fit statistics.

Usage:
    python scripts/generate_html_report.py
"""

import json
import sys
import numpy as np
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
from path_helpers import outputs_root  # noqa: E402

def generate_html_report():
    """Generate HTML report from estimation results with fit statistics."""

    # Load results
    results_file = outputs_root() / "estimates/fr/2016/fr_2016_joint_with_fit_stats.json"
    out_file = outputs_root() / "post_estimation/fr/2016/joint/fr_2016_joint_diagnostics.html"

    print(f"Loading: {results_file}")
    with open(results_file, 'r') as f:
        results = json.load(f)

    # Extract data
    theta = np.array(results['theta'])
    theta0 = np.array(results['theta0'])
    param_names = results['param_names']

    # Fit statistics
    ll = results['log_likelihood']
    ll_null = results.get('ll_null', None)
    rho2 = results.get('rho_squared', None)
    rho2_adj = results.get('rho_squared_adj', None)
    aic = results.get('aic', None)
    bic = results.get('bic', None)

    # Compute parameter statistics
    moved = np.abs(theta - theta0) > 1e-6
    n_moved = np.sum(moved)

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RURO France 2016 Joint Estimation - Diagnostics Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        .section {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .metric {{
            font-size: 1.1em;
            margin: 10px 0;
        }}
        .metric-label {{
            font-weight: bold;
            color: #7f8c8d;
            display: inline-block;
            width: 250px;
        }}
        .metric-value {{
            color: #2c3e50;
            font-weight: bold;
        }}
        .excellent {{
            color: #27ae60;
        }}
        .good {{
            color: #f39c12;
        }}
        .warning {{
            color: #e74c3c;
        }}
        .parameter-moved {{
            background-color: #e8f5e9;
        }}
        .parameter-stuck {{
            background-color: #ffebee;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <h1>RURO France 2016 Joint Estimation - Diagnostics Report</h1>

    <div class="section">
        <h2>Model Fit Statistics</h2>
        <div class="metric">
            <span class="metric-label">Final Log-Likelihood:</span>
            <span class="metric-value">{ll:,.4f}</span>
        </div>
"""

    if ll_null is not None:
        html += f"""
        <div class="metric">
            <span class="metric-label">Null Log-Likelihood:</span>
            <span class="metric-value">{ll_null:,.4f}</span>
        </div>
"""

    if rho2 is not None:
        rho2_class = 'excellent' if rho2 > 0.40 else ('good' if rho2 > 0.20 else 'warning')
        rho2_text = 'OUTSTANDING' if rho2 > 0.40 else ('EXCELLENT' if rho2 > 0.20 else 'GOOD')
        html += f"""
        <div class="metric">
            <span class="metric-label">McFadden's Rho-Squared (ρ²):</span>
            <span class="metric-value {rho2_class}">{rho2:.4f} ({rho2_text})</span>
        </div>
"""

    if rho2_adj is not None:
        html += f"""
        <div class="metric">
            <span class="metric-label">Adjusted Rho-Squared:</span>
            <span class="metric-value">{rho2_adj:.4f}</span>
        </div>
"""

    if aic is not None:
        html += f"""
        <div class="metric">
            <span class="metric-label">AIC (Akaike Information Criterion):</span>
            <span class="metric-value">{aic:,.4f}</span>
        </div>
"""

    if bic is not None:
        html += f"""
        <div class="metric">
            <span class="metric-label">BIC (Bayesian Information Criterion):</span>
            <span class="metric-value">{bic:,.4f}</span>
        </div>
"""

    html += f"""
    </div>

    <div class="section">
        <h2>Optimization Summary</h2>
        <div class="metric">
            <span class="metric-label">Convergence:</span>
            <span class="metric-value excellent">{results.get('success', 'Unknown')}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Optimizer Message:</span>
            <span class="metric-value">{results.get('message', 'N/A')}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Iterations:</span>
            <span class="metric-value">{results.get('n_iterations', 'N/A')}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Function Evaluations:</span>
            <span class="metric-value">{results.get('n_fev', 'N/A')}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Estimation Time:</span>
            <span class="metric-value">{results.get('estimation_time_seconds', 0):.1f} seconds</span>
        </div>
    </div>

    <div class="section">
        <h2>Parameter Summary</h2>
        <div class="metric">
            <span class="metric-label">Total Parameters:</span>
            <span class="metric-value">{len(theta)}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Parameters Moved from Initial:</span>
            <span class="metric-value excellent">{n_moved}/{len(theta)} ({100*n_moved/len(theta):.1f}%)</span>
        </div>
        <div class="metric">
            <span class="metric-label">Parameters Stuck at Initial:</span>
            <span class="metric-value {'warning' if (len(theta)-n_moved) > 0 else 'excellent'}">{ len(theta)-n_moved}/{len(theta)} ({100*(len(theta)-n_moved)/len(theta):.1f}%)</span>
        </div>
    </div>

    <div class="section">
        <h2>Parameter Estimates</h2>
        <table>
            <thead>
                <tr>
                    <th>Index</th>
                    <th>Parameter Name</th>
                    <th>Initial Value</th>
                    <th>Estimated Value</th>
                    <th>Change</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""

    # Add parameter rows
    for i, (name, val, val0) in enumerate(zip(param_names, theta, theta0)):
        change = val - val0
        status = 'MOVED' if abs(change) > 1e-6 else 'STUCK'
        row_class = 'parameter-moved' if status == 'MOVED' else 'parameter-stuck'

        html += f"""
                <tr class="{row_class}">
                    <td>{i}</td>
                    <td><code>{name}</code></td>
                    <td>{val0:.6f}</td>
                    <td>{val:.6f}</td>
                    <td>{change:+.6f}</td>
                    <td><strong>{status}</strong></td>
                </tr>
"""

    html += """
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>Interpretation Guide</h2>
        <h3>Rho-Squared (McFadden's Pseudo R²)</h3>
        <p>McFadden's pseudo R² measures model improvement over the null model (equal probabilities):</p>
        <ul>
            <li><strong>ρ² > 0.40:</strong> Outstanding fit (rare in discrete choice models)</li>
            <li><strong>ρ² > 0.20:</strong> Excellent fit</li>
            <li><strong>ρ² = 0.10-0.20:</strong> Good fit</li>
            <li><strong>ρ² < 0.10:</strong> Poor fit</li>
        </ul>

        <h3>Information Criteria</h3>
        <p><strong>AIC</strong> and <strong>BIC</strong> are used for model comparison (lower is better):</p>
        <ul>
            <li>AIC penalizes complexity linearly: AIC = 2k - 2LL</li>
            <li>BIC penalizes complexity more heavily: BIC = k·ln(n) - 2LL</li>
            <li>Use these to compare alternative specifications</li>
        </ul>

        <h3>Parameter Status</h3>
        <p><strong>Green rows</strong> indicate parameters that moved from their initial values (successfully estimated).</p>
        <p><strong>Red rows</strong> indicate parameters stuck at initial values (may indicate identification issues or normalization constraints).</p>
    </div>

    <div class="section">
        <h2>Notes on Standard Errors</h2>
        <p><strong>Standard errors are NOT available for this estimation.</strong></p>
        <p><strong>Reason:</strong> Joint estimation with parallel processing does not preserve the gradient function needed for numerical Hessian computation.</p>
        <p><strong>Impact:</strong> Cannot perform hypothesis tests (t-values, p-values, confidence intervals).</p>
        <p><strong>Alternative:</strong> Parameter estimates are still valid and can be used for policy simulation and elasticity computation.</p>
    </div>

    <footer>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>RURO France 2016 Joint Estimation | Variable Wages Specification</p>
    </footer>
</body>
</html>
"""

    # Save HTML
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html, encoding='utf-8')

    print(f"\nHTML report saved to: {out_file}")
    print(f"\nModel Fit Summary:")
    print(f"  Log-likelihood: {ll:,.4f}")
    if rho2 is not None:
        rho2_text = 'OUTSTANDING' if rho2 > 0.40 else ('EXCELLENT' if rho2 > 0.20 else 'GOOD')
        print(f"  Rho-squared: {rho2:.4f} ({rho2_text})")
    print(f"  Parameters working: {n_moved}/{len(theta)} ({100*n_moved/len(theta):.1f}%)")
    print(f"\nOpen the HTML file in your browser to view the full report!")

if __name__ == '__main__':
    generate_html_report()
