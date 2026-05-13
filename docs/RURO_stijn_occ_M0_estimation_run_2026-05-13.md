# RURO Stijn Occupation M0 Estimation Run

Date: 2026-05-13

## Purpose

This note records the first completed France 2016 `M0_stijn_occ` preference
estimation after the occupation-draw rebuild passed the Gate-A canaries.

This is a run record, not a new specification. The active specification is:

```text
scripts/enhanced/estimation_spec_stijn_occ_M0.yaml
```

## Data Preconditions

The estimation uses the rebuilt continuous MNL files:

```text
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet
```

The rebuild and validation are documented in:

```text
Results/RURO_stijn_occ_M0_full_rebuild_report_v1.md
Results/_canary_stijn_occ_M0_results.json
```

The final pre-estimation canary status was:

```text
C1-C9: 9/9 PASS
```

Important data convention:

```text
loc4 = -1  non-worker / non-work alternative
loc4 = -2  observed working row with unknown occupation
loc4 = 1   routine-manual reference group
loc4 = 2   nonroutine-manual
loc4 = 3   routine-cognitive
loc4 = 4   nonroutine-cognitive
```

`loc4 = -2` is not an occupation category. It is retained only for a small
number of observed working alternatives and contributes zero to the
occupation-opportunity layer because M0 estimates only `loc4 = 2/3/4`
dummies, with `loc4 = 1` omitted.

## Command

The completed estimation command was:

```powershell
python .\scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/stijn_occ/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "scripts/enhanced/estimation_spec_stijn_occ_M0.yaml" `
  --auto-timestamp `
  --verbose
```

No job-choice warm start was used.

## Run Folder

```text
U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/stijn_occ/gamspy/
  estimation_spec_stijn_occ_M0/run_2026-05-13_11-27-40
```

Files written:

```text
estimation.log
estimation_results.json
estimation_results_singles_male.csv
estimation_results_singles_female.csv
estimation_results_couples.csv
estimation_summary.txt
identification_diagnostics.txt
specification_used.yaml
```

The `outputs/` tree is ignored by git in the current workspace. These files
are available locally but are not committed unless explicitly force-added.

## Estimation Result

Core status:

```text
Specification: stijn_occ_M0
Wage specification: vw
Solver: GAMSPy CONOPT, vectorized
Status: SolveStatus.NormalCompletion (ModelStatus.OptimalLocal)
Total observations: 425,300
Total groups: 4,253
Parameters: 52
Iterations: 29
Joint log-likelihood: -6499.8809125096595
Total walltime: 300.9167904853821 seconds
Proposal correction: -log(prior), applied once per alternative
Opportunity centering: enabled within each choice set
Bound hits: 0
```

The same joint parameter vector is reported under the three result labels
(`singles_male`, `singles_female`, `couples`) because the model was estimated
jointly.

## Key Estimated Opportunity Components

Employment and hours opportunity:

```text
beta_E        = -2.614801
beta_h_pt1    = -0.520320
beta_h_pt2    =  0.372057
beta_h_ft     =  1.463250
beta_E_gsur   = -0.771874
beta_E_educH  =  0.257516
```

Wage opportunity / Mincer equation:

```text
beta_w0       =  2.041081
beta_w_educL  = -0.047567
beta_w_educH  =  0.305522
beta_w_pexp   =  0.017370
beta_w_pexp2  = -0.000206
sigma         =  0.423160
```

Occupation opportunity, reference `loc4 = 1`:

```text
beta_occ_2_sm = -1.512858
beta_occ_3_sm = -2.172559
beta_occ_4_sm =  0.017525

beta_occ_2_sf = -0.014742
beta_occ_3_sf = -0.574523
beta_occ_4_sf =  0.793362

beta_occ_2_cm = -1.470735
beta_occ_3_cm = -2.206059
beta_occ_4_cm =  0.486156

beta_occ_2_cf =  0.205000
beta_occ_3_cf = -0.190384
beta_occ_4_cf =  1.146012
```

## Identification Diagnostics

The run converged and no parameters hit bounds, but Hessian diagnostics warn
that this first M0 result is not yet final-paper-ready without further review:

```text
hessian_condition_number: 67638896031.10768
hessian_negative_eigenvalues: 2
hessian_near_zero_eigenvalues(|eig|<=1e-8): 0
negative_variances_from_varcov: 2
bounded_hits_total: 0
```

Interpretation: the likelihood has a local optimum, but the covariance and
standard-error diagnostics suggest weak identification or strong parameter
correlation for part of the parameter vector. The next review should inspect
standard errors, weak-identification panels, and possibly whether a simpler
occupation or opportunity specification is needed.

## Post-Estimation Output

Post-estimation was run from the completed result and the report was later
regenerated with spec-driven opportunity equations:

```text
U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/stijn_occ/gamspy/
  estimation_spec_stijn_occ_M0/run_2026-05-13_12-10-38/
  fr_2016_stijn_occ_gamspy_specdriven_post_estimation_report_20260513_121058.html
```

The report fix is documented in:

```text
docs/RURO_stijn_occ_post_estimation_report_fix_v1.md
```

Known remaining reporting issue: the new spec-driven opportunity sections are
correct, but the legacy `Group-Specific Parameters` section is still present
and can show parameters from other groups under a group heading. Treat the
new `Parameter Estimates by Category` section as authoritative until that
legacy section is removed or rewritten.

## GAMSPy License Note

The first attempt after the data rebuild failed because GAMSPy used the bundled
demo license:

```text
.venv/Lib/site-packages/gamspy_base/gamslice.txt
```

After installing the student/research GAMSPy license, the same command ran
successfully. This was an environment issue, not a data, specification, or
estimator-code issue.

## Next Steps

1. Fix or suppress the misleading legacy `Group-Specific Parameters` block in
   the HTML report for joint/spec-driven runs.
2. Review standard errors and weak-identification diagnostics before treating
   the estimates as paper-ready.
3. Decide whether M0 is acceptable as the baseline or whether a simplified
   robustness run is needed because of the Hessian warning.
4. If results are to be shared through git, commit this documentation and the
   code/spec files, but do not commit large ignored output files unless there
   is an explicit reason.
