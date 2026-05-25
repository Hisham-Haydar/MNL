# JMP Multi-Year Data Strategy v3.1: Pooled Estimation, ID Engineering, CPI Harmonisation, and Temporal Validation — Strategy Memo v3.1

Date: 2026-05-18

Revision history: v3.1 supersedes v3 with two targeted cleanup
revisions identified in the v3 review. The substantive content of
v3 — the seven corrections to v2 documented in the v3 revision
history, the structural framing of pooled multi-year estimation
as a structural extension, the CPI harmonisation design, the
overlap arithmetic, the temporal-validation design, the verdict
architecture, and the package hygiene rules — is preserved
unchanged in v3.1. The v3.1 revisions are:

(R8) The v3 §6 Element I4 description of the missing-value rule
under string UID encoding produced an internal type inconsistency:
the UID column was described as containing string values for
valid identifiers and the integer 0 for absent relationships,
which is not realisable under any conventional dataframe or
parquet schema (a single column cannot hold both string and
integer values). The v3.1 design resolves the inconsistency by
making the numeric `int64` encoding the operational default and
preserving the string composite as an optional human-readable
audit representation. The choice aligns with the package-hygiene
preference for vectorised numeric operations and produces a
type-consistent UID column. The revisions cover §6 Elements I3
and I4 and §12 Rule H3.

(R9) Table 2 in v3 §6 carried `(audit)` placeholders for
identifier-column maxima that were already established by the
raw-data inspection underlying the v2 → v3 revision. The v3.1
revision fills in those known maxima for `idperson_raw` (2017),
`idorigperson_raw` (2015), `idhh_raw` (all three years), and
`idorighh_raw` (all three years).

Specification class: strategy memo. The memo proposes a sequenced
empirical extension of the M1-clean structural specification to a
multi-year sample. It does not authorise implementation; its
outputs are a methodological design that subsequent implementation
prompts will build upon.

Reference documents:
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` (the accepted 2016
  baseline)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md` (the M1-clean
  structural specification)
- `docs/JMP_multi_year_and_cross_validation_strategy_memo_v3.md`
  (the superseded v3 memo)
- `docs/JMP_multi_year_and_cross_validation_strategy_memo_v2.md`
  (the further-superseded v2 memo)
- `docs/JMP_multi_year_and_cross_validation_strategy_memo_v1.md`
  (the further-superseded v1 memo)
- `Prompts/JMP_ability_vs_opportunity_framework_v1.md` (the welfare
  framework)
- `euromod_fr_2015_2017_standard_income_concepts.csv` and
  `euromod_fr_2015_2017_output_variable_index.csv` (the EUROMOD
  FR data inventory)

---

## 1. Framing

The v3.1 memo treats pooled 2015–2017 estimation as an intended
structural extension of the M1-clean specification rather than as
a deferred robustness exercise. The reframing rests on three
premises.

First, the 2016 M1-clean baseline retains weakly identified
components. The three negative-variance parameters in the singles
consumption block (`beta_c_sm`, `beta_c_sf`, `theta_c_singles`)
constitute a sample-size-sensitive identification limitation that
may be resolved by larger sample size. The welfare-critical
parameters `beta_ll`, `beta_E_gsur`, and the seven region dummies
are precisely identified in 2016, but their standard errors should
tighten relative to the 2016-only baseline under pooled estimation.
The gain will be smaller than the naive $\sqrt{3}$ benchmark once
the 2016-2017 household overlap and cluster-robust inference are
accounted for, but it should still improve the precision of any
welfare decomposition computed from them.

Second, the pooled estimation produces a new empirical object
whose estimands differ from the single-year M1-clean estimands.
The preference parameters under pooling are time-invariant by
assumption; the opportunity parameters absorb additional year-
specific employment-opportunity variation through year fixed
effects; the wage parameters reflect the average wage process
over the pooled period rather than a single year's wage process.
The pooled specification is consequently a structural extension
demanding its own verdict process rather than an incremental
robustness check.

Third, the raw-data findings established that the operational
design of the pooled sample is not arbitrary. The 2016 and 2017
cross-sections share 76.8 per cent of households, while the 2015
cross-section is disjoint from both. This structure dictates that
"pool three years" is not a single design but a family of designs
indexed by the chosen treatment of the 2016–2017 overlap. The v3.1
memo specifies three operational variants of the pooled design and
recommends a staged implementation that begins with the cleanest
identified variant.

The single-year M1-clean baseline remains the JMP's preferred
specification until a pooled specification earns its own SA2-style
verdict. The pooled work supplements the single-year baseline
during this transition and may replace it under the promotion
criteria specified in §11.

---

## 2. The raw-data findings and their econometric significance

The inspection of `U:\EUROMOD-STORAGE\Data\FR` established the
household and person counts and the pairwise overlap structure
summarised in Table 1.

| Year | EUROMOD file | Households | Persons | Overlap with 2015 (hh) | Overlap with 2016 (hh) | Overlap with 2017 (hh) |
|---|---|---|---|---|---|---|
| 2015 | `FR_2015_a2.txt` | 11,390 | 26,558 | — | 0 | 0 |
| 2016 | `FR_2016_a3.txt` | 11,459 | 26,560 | 0 | — | 8,796 |
| 2017 | `FR_2017_a2.txt` | 11,068 | 25,309 | 0 | 8,796 | — |

The structural pattern is unambiguous. The 2015 cross-section is
*disjoint* from the 2016 and 2017 cross-sections; the latter two
are *substantially overlapping*. The 8,796 households appearing
in both 2016 and 2017 constitute 76.8 per cent of the 2016 file
and 79.5 per cent of the 2017 file. The 2015 file shares zero
households with either of the other two.

*Local raw inventory caveat.* The local raw France inventory at
`U:\EUROMOD-STORAGE\Data\FR` does not include an `FR_2014_*`
file; the available year sequence jumps from 2012 to 2015. The
immediate adjacent-year extension supported by the local data is
therefore 2015–2017 rather than 2014–2017. If a 2014 cross-
section is required for any future extension, it must first be
obtained, validated against the EUROMOD FR_2014 system, and
incorporated into the local inventory; this is not within the
scope of the present strategy memo.

The overlap pattern is consistent with the EU-SILC rotating-panel
structure, in which a four-year rotation cycle introduces and
retires sub-samples annually. The 2015 EUROMOD baseline year draws
on a cross-section whose rotation groups had been replaced by the
time of the 2016 and 2017 EUROMOD baseline years; the 2016 and
2017 EUROMOD baseline years draw on overlapping cross-sections in
which the central rotation cohort is present in both. Verifying
the exact mapping between EUROMOD baseline years and EU-SILC
rotation groups is a separate technical question; for the
econometric purposes of this memo, the overlap structure is taken
as observed.

The econometric significance of the overlap structure is that
*pooling is not a single operation*. Three distinct pooling
configurations are now visible:

(P1) *Pool 2015 + 2017.* The two cross-sections are household-
disjoint. The stacked sample contains 22,458 households (11,390 +
11,068) with zero repeated observations. Standard errors computed
under independence are correctly specified, conditional on within-
year EU-SILC sampling assumptions. The pooled sample size is
approximately 1.95 times the single-year sample size. The
configuration is *not* identified under the v3.1 §7 baseline
parameterisation (which uses 2016 as the year-effect reference)
because 2016 is absent from the sample; if (P1) is pursued, it
requires a different parameterisation in which the reference year
is 2015.

(P2) *Pool 2015 + 2016.* Likewise household-disjoint. The
stacked sample contains 22,849 households (11,390 + 11,459) with
zero repeated observations. Standard errors under independence
are correctly specified. The pooled sample size is approximately
2.00 times the single-year sample size. The configuration is
identified under the v3.1 §7 baseline parameterisation: the 2016
year-effect reference is preserved, and a single year dummy for
2015 absorbs the year-specific variation.

(P3) *Pool 2015 + 2016 + 2017.* The 2015 sub-sample is disjoint
from the other two; the 2016 and 2017 sub-samples share 8,796
households. The stacked sample contains 33,917 observation rows
but only 25,121 unique households (11,390 + 11,459 + 11,068 −
8,796). Among the unique households, 8,796 are repeated
(appearing in both 2016 and 2017) and 16,325 are singletons
(appearing in exactly one year). The 8,796 repeated households
contribute $8{,}796 \times 2 = 17{,}592$ observation rows, while
the 16,325 singleton households contribute 16,325 rows. The
repeated-household share of stacked rows is therefore $17{,}592 /
33{,}917 = 51.9$ per cent, and the singleton share is $16{,}325 /
33{,}917 = 48.1$ per cent. Standard errors under naive
independence are biased downward by the overlap; cluster-robust
standard errors at the household level are required for valid
inference.

The corrected arithmetic in (P3) — slightly more than half of the
stacked observation rows derive from repeated households —
strengthens the case for cluster-robust inference relative to the
weaker figures that appeared in the v2 memo. The overlap is not a
marginal complication; it is a defining property of the (P3)
configuration that determines the appropriate inferential
procedure.

A fourth conceptual configuration deserves note for completeness:

(P4) *Pool 2016 + 2017 only.* The overlap structure (77–80 per
cent) places this configuration closer to a balanced panel than
to a pooled cross-section. Estimating it as a pooled cross-section
without explicit panel modelling would be econometrically
incorrect. (P4) is therefore *not* recommended as a pooled-
estimation design; it would more naturally support an explicit
two-period panel model, which is beyond the scope of the M1-clean
extension and is noted only as a methodological possibility for
future work.

---

## 3. Why pooled estimation is now a structural extension, not a robustness check

The v1 memo's recommendation was Variant B — cross-year structural
replication — on the grounds that pooled estimation imposed costs
exceeding its evidentiary returns at the M1-clean stage. The v3.1
reframing, inherited from v2 and v3, accepts that pooled
estimation is a structural extension whose evidentiary returns are
not captured by the cross-year replication framework. Three
returns distinguish pooling from replication.

First, *parameter identification*. Cross-year replication produces
three separately identified parameter vectors; pooled estimation
produces a single parameter vector estimated against all available
variation. For weakly identified components — the singles
consumption joint-identification limitation being the canonical
case — only pooled estimation can resolve the limitation through
sample-size augmentation. Cross-year replication would reproduce
the same limitation in each of the three single-year estimations.

Second, *welfare-baseline integration*. The pooled estimates
produce a single set of structural parameters consistent across
years, against which the JMP's welfare decomposition can be
computed without ambiguity over which year's estimates to use.
Cross-year replication generates three sets of estimates; the
welfare decomposition computed from any one of them carries the
qualification that the other two might have produced different
decompositions. The pooled estimates avoid this ambiguity
structurally.

Third, *temporal generalisation*. The pooled estimates are
constructed against the 2015–2017 period and consequently
represent the labour-supply behaviour of the French metropolitan
prime-age population over that period. The 2016-only estimates
represent only the 2016 cross-section. For a JMP whose substantive
claim concerns the structure of opportunity and well-being in
contemporary France, the pooled estimates carry stronger
generalisability than the single-year estimates.

The reframing accepts the costs identified in v1 — data pipeline
replication, year fixed effect design, clustered uncertainty
inference, welfare interpretation, project sequencing — and
designs operational responses to each. The remainder of the memo
articulates these responses.

---

## 4. Feasibility audit (Section A)

The pooled estimation requires confirmation that the operational
prerequisites are in place. The feasibility audit is the first
implementation step and is sequenced before any structural
implementation work.

The audit covers six conditions.

*Condition F1 — EUROMOD installation.* The EUROMOD FR_2015,
FR_2016, and FR_2017 systems must be installed and configured in
the project's EUROMOD environment. The audit confirms that the
three systems can be invoked from the project's EUROMOD runner
script.

*Condition F2 — Raw EU-SILC microdata.* The EU-SILC microdata
files corresponding to the EUROMOD baseline years 2015, 2016, and
2017 must be available in the project's data directory. The
inspection of `U:\EUROMOD-STORAGE\Data\FR` has already confirmed
the presence of these files for the three years. The audit
verifies that the files are the canonical inputs to the EUROMOD
runs and that no version mismatches exist between the files in
the data directory and the files expected by the EUROMOD systems.

*Condition F3 — Eurostat sources for GSUR.* The Eurostat sources
required by the GSURv2 specification —
`lfst_r_lfu3rt__custom_19204794` (regional unemployment by NUTS-2
× sex × education × age) and `lfst_r_lfsd2pop` (population
denominators) — must be available for 2015 and 2017 in the same
form as for 2016. The Eurostat data warehouse publishes both
series back to 2009, so the data is expected to be available
pending audit confirmation; the audit retrieves the 2015 and 2017
extracts and verifies that they match the structure of the 2016
retrieval used in the GSURv2 v2.1 work.

*Condition F4 — INSEE benchmark.* The INSEE BDM series 001688526
(national unemployment-rate benchmark) must be available for 2015
and 2017. The series is published continuously; the data is
expected to be available pending audit confirmation. The audit
retrieves the annual values for the two years and records them
for use in the L5 national-benchmark validation step of the
GSURv2 lookup for each year.

*Condition F5 — INSEE CPI series.* The INSEE consumer price index
series for the harmonisation procedure must be available for
2015, 2016, and 2017. The audit retrieves the index values for
the three years and records the source URL.

*Condition F6 — EUROMOD output variable comparability.* The
EUROMOD output variables required by the RURO pipeline — the
disposable income components, the wage variables, the hours
variables, and the demographic variables — must be available in
the same form across the three EUROMOD systems. The audit cross-
references the project's
`euromod_fr_2015_2017_standard_income_concepts.csv` and
`euromod_fr_2015_2017_output_variable_index.csv` against the
2016 RURO pipeline's variable list and identifies any variables
present in 2016 but absent in 2015 or 2017 (or vice versa). Any
discrepancies are documented and resolved before the multi-year
pipeline runs.

The audit produces a feasibility report
(`Results/JMP_multi_year_feasibility_audit_v1.md` or equivalent)
that records the status of each condition and, if any condition
fails, identifies the operational response. If all six conditions
pass, the audit authorises the subsequent pipeline implementation
steps.

The feasibility audit is methodologically independent of the
M1-naive verdict and the welfare-measurement decisions memo. It
can be executed at any point after the M1-clean verdict and is
recommended as the immediate next operational step in the multi-
year track.

---

## 5. CPI harmonisation design (Section B)

The pooled estimation requires that monetary variables be
expressed in a common real-price unit across the three years. The
v3.1 memo specifies that CPI harmonisation occurs *after* EUROMOD
has been run in each native policy year, and that only the
resulting monetary outputs are harmonised. The tax-benefit system
operates in nominal terms within each policy year; the harmonised
real values enter the RURO estimation only.

The harmonisation design rests on six explicit decisions.

*Decision D1 — Base year.* The base year is 2016. The choice
preserves continuity with the existing M1-clean baseline: the
2016-harmonised monetary scale is identical to the 2016 native
scale (CPI factor of unity), so the 2016 sub-sample in the pooled
data is byte-identical to the existing 2016 MNL parquets in
monetary terms. The 2015 and 2017 monetary variables are expressed
in 2016 prices. The choice also simplifies the interpretation of
any cross-year comparison between the pooled estimates and the
existing single-year M1-clean estimates.

*Decision D2 — CPI source.* The CPI source is the INSEE consumer
price index, annual average, all-items, all-household
(Indice des prix à la consommation, moyenne annuelle, ensemble
des ménages, France métropolitaine). The series is published by
INSEE on its public data portal (api.insee.fr) and is the
canonical price index for the French metropolitan economy.

*Decision D3 — CPI factors.* Let $\mathrm{CPI}_t$ denote the
INSEE annual CPI level for year $t$. The harmonisation factor for
year $t$ relative to base year 2016 is

$$\phi_t = \frac{\mathrm{CPI}_{2016}}{\mathrm{CPI}_t}.$$

Each monetary variable $M_t$ observed in year $t$ is harmonised
to $M^{\mathrm{real}}_t = \phi_t \cdot M_t$. The CPI values for
2015, 2016, and 2017 are retrieved from INSEE and recorded in the
feasibility audit; the corresponding factors $\phi_{2015}$,
$\phi_{2016} = 1$, and $\phi_{2017}$ are recorded in the pooled-
sample configuration file.

*Decision D4 — Variables transformed.* The following monetary
variables are transformed by the harmonisation factor:

1. Disposable income (the consumption argument in the RURO
   utility function).
2. Gross wage variables (hourly and annual, used in the wage-
   opportunity block).
3. Non-labour income components entering the disposable-income
   calculation.

The transformation is applied at the alternative-row level (post
EUROMOD, post tax-benefit calculation, before the RURO precompute
step). The transformation is multiplicative and operates on the
nominal monetary value $M_t$ in year $t$ to produce the harmonised
value $M^{\mathrm{real}}_t$.

*Decision D5 — Variables not transformed.* The following
variables are *not* transformed and remain in their native scale:

1. Hours of work (already in physical hour-per-week units).
2. Demographic variables (age, sex, education, region, occupation,
   household composition).
3. Binary indicators (`working`, `educL`, `educH`, the seven
   `drgn{k}` region indicators, occupation indicators).
4. The GSUR variable (already in proportion units; year-specific
   by construction).
5. The hours-band shifters and occupation shifters in the M1-clean
   specification.

The non-transformation of non-monetary variables is verified as a
separate validation step in the pooled-sample construction.

*Decision D6 — Ordering of operations.* The harmonisation is
applied *after* EUROMOD has been run in each native policy year.
The tax-benefit system operates on nominal income in the native
policy year and produces the disposable income and component
variables in nominal native-year terms. The harmonisation
transforms these outputs into real 2016-base terms for the RURO
estimation. The ordering is not optional: applying CPI
harmonisation *before* EUROMOD would distort the tax-benefit
calculation by mis-scaling the bracket thresholds, allowance
amounts, and benefit eligibility cutoffs that EUROMOD applies in
nominal native-year terms.

The CPI harmonisation produces a transformed dataset whose
monetary values are in real 2016 prices but whose tax-benefit
calculations are preserved as native-year nominal operations. The
RURO estimation operates on the harmonised real values.

A validation procedure confirms the harmonisation. For each year
$t \in \{2015, 2017\}$, the validation computes the mean
disposable income in nominal native-year terms, applies the
harmonisation factor, and verifies that the resulting harmonised
mean equals the pre-harmonisation mean multiplied by $\phi_t$ to
within machine precision. The validation also confirms that the
non-monetary variables in Decision D5 are byte-identical before
and after harmonisation.

---

## 6. Stacked-ID design (Section C)

The pooled estimation requires globally unique household and
person identifiers that distinguish records across years without
overwriting the raw EUROMOD identifiers. The v3.1 design preserves
the raw identifiers under separate column names and adds derived
unique identifiers for the stacked-processing operations. The
operational default in v3.1 is the numeric `int64` encoding, with
the string composite retained as an optional human-readable audit
representation. The shift in default from v3 reflects the package-
hygiene preference for vectorised numeric operations and resolves
the column-type inconsistency that arose under the v3 string-
default treatment of missing relationship identifiers.

The design rests on six elements.

*Element I1 — Preserved raw identifiers.* The pooled dataset
preserves the following raw EUROMOD identifiers under explicit
"raw" suffixes:

```
survey_year       (int32, year ∈ {2015, 2016, 2017})
idhh_raw          (int64, raw EUROMOD household identifier)
idperson_raw      (int64, raw EUROMOD person identifier)
idfather_raw      (int64, raw EUROMOD father identifier; 0 if absent)
idmother_raw      (int64, raw EUROMOD mother identifier; 0 if absent)
idpartner_raw     (int64, raw EUROMOD partner identifier; 0 if absent)
idorighh_raw      (int64, raw EUROMOD original-household identifier)
idorigperson_raw  (int64, raw EUROMOD original-person identifier)
```

The raw identifiers are byte-identical to the values in the
EUROMOD output files. Their preservation ensures that any
subsequent overlap diagnostic, clustered standard-error
computation, or panel-sensitivity analysis can be performed
against the original identifier space without information loss.

*Element I2 — Globally unique working identifiers.* The pooled
dataset constructs derived unique identifiers under explicit
"uid" suffixes:

```
idhh_uid          (int64, globally unique household identifier)
idperson_uid      (int64, globally unique person identifier)
idfather_uid      (int64, globally unique father identifier; 0 if absent)
idmother_uid      (int64, globally unique mother identifier; 0 if absent)
idpartner_uid     (int64, globally unique partner identifier; 0 if absent)
```

The unique identifiers are constructed by a configurable encoding
scheme that is collision-proof, reversible, and type-consistent
within each column.

*Element I3 — Encoding scheme.* The operational default is a
numeric encoding of the form

$$\mathrm{id}_{\mathrm{uid}} = B \cdot \mathrm{year} + \mathrm{id}_{\mathrm{raw}},$$

where $B$ is a configurable integer base satisfying $B >
\max_t \max_i \mathrm{id}_{\mathrm{raw},i,t}$ across all years
$t$ and all identifier columns $i$ in the pooled sample. The
resulting UID is `int64`, vectorisable, and amenable to fast
hash-based joins and group-by operations. The encoding is
collision-proof under the $B$-magnitude condition: for any two
records with the same year, the encoded values differ in the
raw-identifier component; for any two records with different
years, the encoded values differ in the year-multiplier component.
The encoding is reversible:

$$\mathrm{survey\_year} = \mathrm{id}_{\mathrm{uid}} \div B, \quad
\mathrm{id}_{\mathrm{raw}} = \mathrm{id}_{\mathrm{uid}} \bmod B.$$

Table 2 summarises the maximum identifier magnitudes observed in
the inspected France raw files and the corresponding minimum safe
base $B$.

| Identifier column | 2015 max | 2016 max | 2017 max | Observed max | Min safe $B$ |
|---|---|---|---|---|---|
| `idperson_raw` | 147,840,002 | 9,378,990,002 | 467,130,003 | $9.38 \times 10^9$ | $> 10^{10}$ |
| `idorigperson_raw` | 147,840,002 | 9,379,830,001 | 9,379,750,001 | $9.38 \times 10^9$ | $> 10^{10}$ |
| `idhh_raw` | 1,478,400 | 93,789,900 | 4,671,300 | $9.38 \times 10^7$ | $> 10^{8}$ |
| `idorighh_raw` | 1,478,400 | 93,789,900 | 4,671,300 | $9.38 \times 10^7$ | $> 10^{8}$ |

The overall minimum safe base across all identifier columns and
all years in the planned pooled sample is $10^{10}$, driven by
the person-level identifiers. The recommended base, providing one
order of magnitude of headroom against future identifier growth
or addition of further years, is $B = 10^{11}$. Under $B =
10^{11}$, the maximum UID value occurring in the pooled sample
is bounded above by $10^{11} \cdot 2017 + 9.38 \times 10^9
\approx 2.02 \times 10^{14}$, comfortably within the `int64`
representable range of $9.22 \times 10^{18}$.

An alternative human-readable encoding is provided for audit and
debugging purposes:

$$\mathrm{id}_{\mathrm{uid,str}} = \texttt{"\{year\}:\{id\}\textunderscore raw\}"}$$

(for example, `"2016:9378990002"`). The string encoding is not
the operational default and is *not* stored in the canonical
pooled parquets; it is generated on demand from the `int64` UID
through a documented utility function. The string representation
is useful for spot-checks of individual records and for human
inspection of identifier-level diagnostics but does not enter the
pipeline's vectorised operations.

*Element I4 — Missing-value rule for relationship identifiers.*
The relationship identifiers `idfather_raw`, `idmother_raw`, and
`idpartner_raw` carry a value of 0 in the EUROMOD output to
indicate that the relationship does not exist (no father in the
household, no partner, etc.). Under the numeric `int64` encoding,
the missing-value rule preserves this absence semantically:

$$\mathrm{idfather}_{\mathrm{uid}} = \begin{cases} 0 & \text{if } \mathrm{idfather}_{\mathrm{raw}} = 0 \\ B \cdot \mathrm{year} + \mathrm{idfather}_{\mathrm{raw}} & \text{otherwise.} \end{cases}$$

The identical rule applies to `idmother_uid` and `idpartner_uid`.
The rule is type-consistent within a single `int64` column: both
the zero value (missing) and the encoded values (present) are
representable as `int64` without conversion to a different type.
The zero value is unambiguous as a missing-relationship marker
because the smallest valid encoded value is $B \cdot
\min(\mathrm{year}) + \min(\mathrm{id}_{\mathrm{raw}}) \geq
10^{11} \cdot 2015 + 1 > 2 \times 10^{14}$, which is many orders
of magnitude larger than zero.

Under the optional string encoding, the corresponding missing-
value representation is a `NULL`/`NA` value (not the literal
string `"0"`), preserving the same semantic distinction in the
string-encoded space.

*Element I5 — Relationship-identifier consistency.* The
relationship identifiers within a given year reference other
persons in the *same* year. The `_uid` versions of these
identifiers are constructed using the same year value as the
referencing person, ensuring that the household-link structure
within each year is preserved in the `_uid` identifier space. The
consistency property is verified in the pooled-sample
construction step: for every non-zero `idfather_raw` in the
sample, the corresponding `idfather_uid` must match the
`idperson_uid` of the father in the same `survey_year`.

*Element I6 — Two-layer ID coexistence and division of labour.*
The pooled dataset carries both layers of identifiers as separate
columns. The `_uid` identifiers serve a purely *engineering*
purpose: stacking-stage uniqueness, MNL alternative-row indexing,
parquet integrity, downstream joins where year-disambiguation is
required. The `_raw` identifiers — specifically `idhh_raw` and
`idorighh_raw` — serve the *inferential* purpose: detection of
the 2016–2017 household overlap and computation of cluster-robust
standard errors at the raw household level under treatment T1 of
§8. The two roles must not be conflated. Clustering on `idhh_uid`
would treat the 2016 and 2017 appearances of the same raw
household as independent clusters, defeating the purpose of the
cluster-robust correction. Clustering must be at the raw
household level (`idhh_raw` or `idorighh_raw`), which preserves
the within-household serial correlation that the correction is
designed to account for.

The empirical equivalence of `idhh_raw` and `idorighh_raw` for
overlap-counting purposes is recorded in the inspection: both
identifier columns produce the same 2016–2017 overlap count of
8,796 households. The feasibility audit confirms which of the two
is the more stable identifier across the EUROMOD output files
(in particular, whether `idorighh_raw` is preserved across
person-level operations that might modify `idhh_raw` for split or
merged households) and records the audit's recommendation as
the canonical clustering key.

---

## 7. Pooled 2015–2017 estimation design (Section D)

The pooled estimation extends the M1-clean specification to a
multi-year sample. The structural content of M1-clean is
preserved unchanged; the extension consists of year-specific
opportunity shifters that absorb the residual year-fixed variation
in the employment-opportunity index.

The design rests on six elements.

*Element E1 — Specification name.* The pooled M1-clean
specification is named `ruro_occ_M1_clean_pooled`. The provenance
relation to the single-year M1-clean specification is preserved
through the YAML's `specification.description` field. The
implementation-prompt deliverable produces a separate YAML at
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean_pooled.yaml`,
not a modification of the existing M1-clean YAML.

*Element E2 — Year fixed effects with 2016 as reference.* The
pooled specification adds year indicators to the
`market_opportunity` block, with 2016 as the reference category.
The choice of reference year preserves continuity with the
M1-clean single-year specification: the year-2016 coefficient is
normalised to zero, and the year-2015 and year-2017 coefficients
are interpretable as employment-opportunity utility shifts
relative to 2016.

The added parameters in the (P3) 2015 + 2016 + 2017 configuration
are:

```
beta_E_year2015   (working-interacted coefficient on year_2015 indicator)
beta_E_year2017   (working-interacted coefficient on year_2017 indicator)
```

In the (P2) 2015 + 2016 configuration, only one year dummy is
added (`beta_E_year2015`), with 2016 as the implicit reference
through its presence in the sample. The (P2) parameter count is
therefore $53 + 1 = 54$; the (P3) parameter count is $53 + 2 =
55$. Each year-effect parameter receives an initial value of
zero, a bounds specification of $[-10, 10]$, and `applies_to:
"household"` following the convention established in the M1-clean
YAML for the region dummies.

*Element E3 — Identification of the (P1) 2015 + 2017
configuration.* The (P1) configuration is *not* identified under
the baseline parameterisation specified in E2. With 2016 absent
from the sample, the two year dummies for 2015 and 2017 would
perfectly span the sample and be collinear with the baseline
working term in the market-opportunity block. If (P1) is
estimated, it requires a separately parameterised specification
in which the reference year is 2015 and only one year dummy
(`beta_E_year2017`) is added; the parameter count is then $53 +
1 = 54$. The (P1) variant under this reparameterisation is a
*different* identified specification than (P2) and (P3), with a
different reference category, and is not directly comparable to
the (P3) primary specification in the year-effect coefficients.

For the v3.1 sequencing, (P1) is not the recommended first clean
pooled estimation. The recommended first clean pooled estimation
is (P2), which preserves the 2016-reference parameterisation and
the comparability with the (P3) final estimation. (P1) may
optionally be pursued as a sensitivity exposure under the
reparameterised specification described above, but is not the
primary path.

*Element E4 — Wage-block year fixed effects.* Year fixed effects
in the wage-opportunity block are *not* added in the baseline
pooled specification. The CPI harmonisation already removes
nominal wage growth, leaving residual real wage variation that is
small over the 2015–2017 period (real wages grew approximately
1 per cent annually in metropolitan France over this period).
Whether the residual real wage variation warrants wage-block year
fixed effects is documented as a robustness check, not as part of
the baseline pooled specification. A sensitivity-only
specification, `ruro_occ_M1_clean_pooled_wageY`, adds two wage-
block year intercepts (`beta_w0_year2015`, `beta_w0_year2017`)
and is estimated as a robustness exposure under the (P3)
configuration only.

*Element E5 — Sample selection.* The pooled sample comprises the
metropolitan France singles (age 25 to 65) and couples (age 25
to 65) from each of 2015, 2016, and 2017, subject to the same
sample-perimeter restrictions established for the single-year
M1-clean baseline (`drgn1 ∈ {1, ..., 8}`; exclusion of DOM and
extra-regio). The sample-selection criteria are applied within
each year and the resulting selected subsamples are stacked.

The pooled sample size, after sample selection, is expected to be
on the order of 12,000 households (approximately three times the
2016 metropolitan singles + couples count of 4,253), but the
precise count depends on the year-by-year application of the
sample-selection criteria. The expected pooled-sample overlap
between 2016 and 2017 selected households is on the order of
1,800 couples and 1,700 singles, but these figures are
extrapolations from the raw-file overlap before the 2015 and 2017
RURO pipelines have been built and the sample selection applied.
The implementation report must replace these expected magnitudes
with the observed selected-sample overlap counts after the
pooled-sample construction is complete; the SA2 verdict refers to
the observed counts rather than to the expected magnitudes.

*Element E6 — Pooled-sample MNL parquet construction.* The pooled
estimation operates against a single set of MNL parquets stacking
the relevant years. The construction follows the GSURv2 v2.1
pipeline applied year by year, with the resulting per-year
parquets stacked into a single pooled parquet pair (naming
convention `fr_2015_2017_RURO_mnl__singles.parquet` and
`fr_2015_2017_RURO_mnl__couples.parquet` for the three-year
configuration; analogous names for the two-year configuration).
The stacked parquets carry both raw identifiers (per §6 Element
I1) and unique identifiers (per §6 Element I2); the `survey_year`
column is preserved for downstream filtering and diagnostics.

The CPI harmonisation (§5) is applied at the alternative-row
level during the pooled-parquet construction. The monetary
variables (disposable income, gross wage, non-labour income) are
in real 2016 prices in the stacked parquets.

*Element E7 — Estimation protocol.* The pooled estimation uses
the same multistart and convergence protocol as the M1-clean
single-year estimation: three independent starts; warm-start from
the M1-clean 2016 parameter vector for the 53 inherited
parameters; zero initialisation for the year-effect parameters;
CONOPT solver via vectorised GAMSPy. Acceptance requires
identical log-likelihood across all three starts to within
machine precision and a bit-identical parameter vector. The
estimation walltime is expected to be approximately two to three
times the M1-clean walltime, depending on the configuration
((P2) approximately doubles, (P3) approximately triples).

The pooled-estimation deliverables follow the M1-clean pattern:
estimation report, post-estimation diagnostics, M1-specific
supplementary diagnostics (Wald tests on region dummies and on
year dummies, region and year covariance sub-blocks, GSUR-region-
year Hessian sub-block eigenvalues).

The pooled specification is *not* accepted as the preferred
baseline by default. The promotion criteria in §11 govern whether
the pooled estimates replace the single-year M1-clean estimates
as the JMP's primary structural baseline.

---

## 8. Treatment of repeated households and standard errors (Section E)

The 76.8 per cent household overlap between 2016 and 2017 means
that the pooled (P3) sample contains 8,796 households appearing
in both years and 16,325 households appearing in exactly one year.
The 8,796 repeated households contribute 17,592 observation rows
treated, under the naive independence assumption, as 17,592
independent draws; under the correct clustering, they contribute
8,796 independent household clusters with two observations each.
The corrected arithmetic of §2 establishes that 51.9 per cent of
stacked observation rows in (P3) derive from repeated households.

The downward bias in naive standard errors depends on the
within-household serial correlation of the labour-supply choice
process; for prime-age stable households whose 2016 and 2017
observations are substantially similar (a common case), the bias
can be substantial. The fraction of (P3) rows derived from
repeated households is large enough that cluster-robust inference
is not optional for the (P3) primary specification.

The v3.1 memo proposes three operational treatments of the
clustering issue.

*Treatment T1 — Cluster-robust standard errors at the raw
household level.* Under this treatment, the pooled estimation
produces point estimates under the standard joint log-likelihood
and the standard errors are computed using a cluster-robust
sandwich estimator clustered at the `idorighh_raw` (or
`idhh_raw`) level. The sandwich estimator is

$$\widehat{V}_{\mathrm{cluster}} = \widehat{H}^{-1} \left( \sum_g \widehat{g}_g \widehat{g}_g^\top \right) \widehat{H}^{-1},$$

where $g$ indexes the unique households (clusters),
$\widehat{g}_g$ is the sum of the score-vector contributions from
the observation rows of cluster $g$, and $\widehat{H}$ is the
Hessian of the joint log-likelihood. The clustering key is the
raw household identifier (`idhh_raw` or `idorighh_raw`,
determined by the feasibility audit per §6 Element I6), *not* the
engineering UID, because the cluster-robust correction is
designed to account for within-cluster correlation across years
and clustering on the UID would treat each year's appearance of
the same household as an independent cluster.

The procedure is standard for clustered maximum-likelihood
estimation. The implementation requires computing the per-
observation score vectors and aggregating to the cluster level.
The CONOPT solver does not natively produce per-observation
scores; an implementation step is therefore required to compute
the scores explicitly post-convergence and to aggregate them to
the cluster level.

Treatment T1 is the preferred final treatment under the v3.1 memo
because it correctly accounts for the within-cluster correlation
without restricting the sample.

*Treatment T2 — Naive Hessian-based standard errors, labelled
provisional.* Under this treatment, the pooled estimation
produces point estimates and naive Hessian-based standard errors
following the M1-clean single-year protocol. The standard errors
are explicitly labelled as provisional pending the implementation
of cluster-robust inference; the relevant verdict and any JMP
text based on the provisional standard errors carry an explicit
qualification.

Treatment T2 is the interim treatment recommended for the first
pooled-estimation pass. It permits the structural content of the
pooled estimates to be evaluated against the M1-clean baseline
before the cluster-robust inference infrastructure is built. The
provisional label ensures that no welfare-decomposition inference
is conducted using the naive standard errors.

*Treatment T3 — Independence-preserving sample selection.* Under
this treatment, the pooled sample is restricted to a configuration
in which no household appears in more than one year. The (P1) and
(P2) configurations of §2 satisfy this restriction; the (P3)
configuration does not. Restriction options include:

(T3a) Pool 2015 and 2017 only, dropping 2016 entirely. The
stacked sample is 22,458 households with zero repeats and
approximately 1.95 times the single-year sample size. The
configuration requires the (P1)-reparameterised year-effect
specification (§7 E3).

(T3b) Pool 2015 and 2016 only, dropping 2017 entirely. The
stacked sample is 22,849 households with zero repeats and
approximately 2.00 times the single-year sample size. The (P2)
specification with one year dummy (`beta_E_year2015`) is used.

(T3c) Pool all three years with one observation per household
selected via a documented selection rule (for instance, the
earliest year for repeated households, or a random selection at
the household level). The stacked sample is 25,121 unique
households with zero repeats and approximately 2.20 times the
single-year sample size. The (P3) specification with two year
dummies is used.

Treatment T3 is recommended as a sensitivity exposure rather than
as the primary pooled-estimation treatment. The (T3c)
restriction, while attractive for its sample-size properties,
requires a documented selection rule whose implications for the
welfare interpretation are non-trivial; the (T3a) and (T3b)
restrictions discard a non-trivial fraction of available data and
may produce estimates whose precision is materially worse than
the (P3) pooled estimates under cluster-robust inference.

The recommended sequencing of treatments is:

1. *First clean pooled estimation: (P2) 2015 + 2016, under naive
   independence (T2).* The (P2) sample has zero overlap, so the
   independence assumption is correct subject to within-year
   EU-SILC clustering. The 2016 year-effect reference is
   preserved, and the (P2) specification is parameterisationally
   comparable to (P3). The interim result establishes whether
   pooled estimation produces estimates materially different
   from the M1-clean single-year estimates.

2. *Full-data pooled estimation: (P3) 2015 + 2016 + 2017, under
   naive inference (T2) initially.* The interim result
   establishes whether the full-data pooling produces estimates
   materially different from the (P2) clean pooled estimation
   and the M1-clean single-year baseline.

3. *Cluster-robust inference (T1) implemented as a separate
   computational step on the (P3) estimates.* The cluster-robust
   standard errors supersede the T2 provisional standard errors
   for the (P3) configuration.

4. *(T3) sensitivity exposures as a robustness check on the (P3)
   results.* The choice of (T3a), (T3b), or (T3c) for the
   sensitivity exposure is determined at the implementation
   stage; (T3c) is the most informative if a defensible
   selection rule can be specified.

The sequenced approach permits incremental learning about the
pooled-estimation structure before the cluster-robust inference
infrastructure is built. It also permits the (P2) clean-design
estimates to serve as a benchmark against which the (P3) overlap-
inclusive estimates are compared. The substitution of (P2) for
(P1) as the first clean pooled estimation is the principal
correction relative to the v2 sequencing.

---

## 9. Temporal validation design (Section F)

The raw-data findings invalidate one of the v1 memo's
recommendations. The v1 memo proposed a single-year out-of-sample
prediction exercise (training on 2016, predicting 2017) as a
low-cost supplement to the cross-year replication. The 76.8 per
cent household overlap between 2016 and 2017 means that this
exercise would not constitute genuine out-of-sample prediction:
most of the 2017 households appearing as the "test set" were in
the 2016 "training set" by household identity, and the prediction
exercise would partly recover the in-sample parameters rather
than test temporal transport.

The corrected temporal-validation design uses household-disjoint
year pairs. Two clean configurations are available.

*Configuration V1 — Train on 2015, test on 2016 or 2017.* The
2015 cross-section is disjoint from both 2016 and 2017 at the
household level. Training on 2015 and predicting either 2016 or
2017 outcomes is a genuine out-of-sample temporal-transport
test. Recommended choice: train on 2015, test on 2017, which
provides the longest temporal gap (two years).

*Configuration V2 — Train on 2016, test on a household-disjoint
2017 subsample.* The 2017 households not appearing in the 2016
sample (approximately 2,272 households, or 20.5 per cent of the
2017 file) constitute a household-disjoint subsample of 2017.
Training on the full 2016 sample and predicting outcomes for
this 2017 subsample produces a genuine out-of-sample test,
although the test set is smaller than under V1.

The recommended temporal-validation procedure uses V1: train on
the 2015 sample, estimate the M1-clean specification, apply the
estimated parameters to the 2017 alternative sets, and compare
the predicted choice probabilities and marginal distributions to
the observed 2017 outcomes. The comparison uses standard fit
metrics (participation rates by group, mean hours by group,
hours-bin distributions, occupation shares) and the predictive
log-likelihood evaluated on the 2017 sample.

A complementary diagnostic compares the V1 predicted outcomes to
the *2017-trained* parameter vector's in-sample predictions on
the same 2017 sample. The difference between V1 predictions
(2015-trained applied to 2017) and 2017-trained predictions
quantifies the temporal-transport error.

The temporal-validation exercise is *separate* from the pooled
estimation. The pooled estimation uses all available data for
joint identification; the temporal validation uses non-overlapping
years to test transport. The two exercises are methodologically
orthogonal and answer different questions.

Configuration V2 (train on 2016, test on 2017-only-subsample) is
documented as a sensitivity alternative for completeness but is
not recommended as the primary validation design because the test
set is small (~2,272 households) and the temporal gap is short
(one year).

---

## 10. Whether the 2016 baseline remains primary (Section G)

The 2016 M1-clean SA1-STANDS verdict is in place. The pooled
specification is a new empirical object that must earn its own
verdict before replacing the 2016 baseline as the JMP's preferred
structural specification. The v3.1 memo retains the v3
articulation of the criteria for promotion.

The default position is that *the 2016 single-year M1-clean
estimates remain the JMP's primary structural baseline until the
pooled specification earns a SA2-style verdict*. The default
preserves the verdict-document chain established by the
M0c_b2_GSURv2 verdict and the M1-clean verdict; each new
empirical object earns its own acceptance through the same
procedural pathway. The pooled specification does not inherit
M1-clean's verdict.

Three transitional uses of the pooled estimates are permissible
during the interim period:

(U1) The pooled estimates can be reported as a robustness
exposure in the JMP's robustness section, paralleling the M1-naive
sensitivity exposure for the ability-versus-opportunity partition
(R2). The pooled exposure tests the temporal stability of the
M1-clean welfare results under multi-year estimation.

(U2) The pooled estimates can inform the welfare-measurement
decisions memo by providing additional empirical evidence on the
parameter ranges relevant to the welfare functional choice. The
decisions memo can specify how the welfare decomposition should
be presented under both single-year and pooled specifications,
once both are available.

(U3) The pooled estimates can be used to confirm or qualify the
single-year qualifications documented in the M1-clean verdict
(Q1 through Q4). If the pooled estimates resolve the
qualifications (for instance, if `beta_E_drgn8` becomes
individually significant at $p < 0.05$ under the larger pooled
sample), the resolution is documented in the welfare scaffold
without modifying the M1-clean single-year verdict.

The promotion criteria — the conditions under which the pooled
specification replaces the 2016 single-year M1-clean as the JMP's
primary baseline — are specified in §11.

---

## 11. Promotion criteria (Section G, continued)

The pooled specification is considered for promotion to JMP
primary baseline if and only if it earns a SA2-STANDS verdict
under the criteria specified below. The SA2 acceptance rule
parallels the §22 SA1 acceptance rule of the M1-clean design
memo but is adapted to the pooled-specification context.

*SA2-STANDS — Pooled specification accepted as the JMP's primary
structural baseline.* The proposed criteria are:

1. *Convergence.* Three independent multistart runs converge to
   identical log-likelihood and to bit-identical parameter
   vectors.
2. *Preference parameter stability.* All preference parameters
   shift by less than 5 per cent in absolute value relative to
   the 2016 single-year M1-clean estimates.
3. *Wage and occupation parameter stability.* All wage and
   occupation parameters shift by less than 5 per cent in
   absolute value relative to the M1-clean estimates.
4. *Region coefficient consistency.* The seven region coefficients
   `beta_E_drgn2` through `beta_E_drgn8` retain consistent signs
   (all positive relative to IDF) and individual magnitudes
   within 30 per cent of the M1-clean estimates.
5. *GSUR coefficient stability.* `beta_E_gsur` remains negative
   and statistically significant at $p < 0.01$, with magnitude in
   the interval $[-1.8, -0.6]$ (a slightly widened range relative
   to the M1-clean SA1-STANDS interval to accommodate genuine
   variation in the pooled estimation).
6. *Year fixed effect interpretability.* The two year dummies
   `beta_E_year2015` and `beta_E_year2017` are jointly significant
   at $p < 0.10$ and exhibit signs consistent with macroeconomic
   labour-market evidence for the period (rising in 2015,
   declining in 2017, relative to 2016).
7. *Hessian conditioning.* The condition number of the pooled
   Hessian is below $10^{12}$ (an order of magnitude wider than
   the M1-clean threshold to accommodate the larger sample).
8. *Resolution of singles consumption identification.* The pooled
   specification produces valid (non-negative-variance) standard
   errors for at least one of the three negative-variance
   parameters in the M1-clean specification (`beta_c_sm`,
   `beta_c_sf`, `theta_c_singles`). Full resolution of all three
   would be a strong promotion signal; partial resolution of one
   is sufficient for SA2-STANDS.
9. *Cluster-robust inference.* Cluster-robust standard errors
   under treatment T1 are computed and reported. Provisional T2
   standard errors are insufficient for SA2-STANDS; the cluster-
   robust inference must be in place.
10. *Fit diagnostics.* Participation, mean hours, hours-bin L1,
    wage, and occupation fit do not regress relative to the
    M1-clean single-year baseline by more than 1 percentage point
    or 0.5 hours in any group.

Under SA2-STANDS, the pooled specification becomes the JMP's
primary structural baseline; the M1-clean single-year estimates
are retained as a robustness exposure documenting temporal
sensitivity.

*SA2-REVISION — Pooled specification accepted with documented
qualifications.* This verdict applies when one or more SA2-STANDS
criteria fail by small margins. The pooled specification is
documented as the working specification with explicit
qualifications; the welfare scaffolding is implemented from the
pooled estimates with the qualifications recorded.

*SA2-OVERTURNED — Pooled specification rejected.* This verdict
applies when one or more of the following conditions hold: a
preference parameter shifts by more than 10 per cent; the Hessian
condition number exceeds $10^{13}$; multistart fails to converge;
the year fixed effects are jointly insignificant at $p > 0.20$
and the log-likelihood improvement over a pooled specification
*without* year fixed effects is less than 5 units (a no-year-
effect-needed signal indicating that the pooling is not
informationally augmented by year flexibility). Under SA2-
OVERTURNED, the pooled specification is documented as having
failed and the JMP defaults to the M1-clean single-year baseline
with the pooled work archived as a methodological investigation.

The SA2 verdict is a separate memo
(`docs/RURO_occ_M1_clean_pooled_verdict_v1.md`) that follows the
same structure as the M1-clean verdict. The criteria above are
proposed and may be revised in a successor memo if the pooled
estimation evidence indicates the thresholds require adjustment;
the revision is documented through the same provenance pathway as
the M1-clean SA1 thresholds.

---

## 12. Package hygiene

The pooled-estimation infrastructure is designed to be country-,
year-, and specification-agnostic in its core implementation.
France-specific and 2015–2017-specific elements are isolated in
configuration files and adapter modules; the reusable core
operates against the configured year list, CPI factors, and ID
encoding rules without reference to specific values.

Five hygiene rules govern the implementation.

*Rule H1 — Year list configurable.* The pooled-estimation
implementation accepts a year list as a configuration parameter.
The implementation does not hard-code the values 2015, 2016, and
2017; these are passed in through the configuration file and may
be replaced by alternative year lists (e.g., 2018–2020) without
code modification.

*Rule H2 — CPI factors configurable.* The CPI harmonisation
implementation accepts the CPI factor table as a configuration
parameter. The base year and the factor for each year are
configured, not hard-coded. Replacing the base year or adjusting
the factors for a different country's CPI series requires no
code modification.

*Rule H3 — ID stacking implemented generically with numeric
default and configurable encoding base.* The ID stacking utility
(the function constructing `_uid` identifiers from `_raw`
identifiers) defaults to the numeric `int64` encoding $B \cdot
\mathrm{year} + \mathrm{id}_{\mathrm{raw}}$ as the operational
representation in the canonical pooled parquets. The numeric
default is selected on package-hygiene grounds: `int64` UID
columns are type-consistent (the missing-value rule for
relationship identifiers operates within the same `int64` type
without conversion to a different type), vectorisable (the core
estimation and post-estimation routines operate on numeric arrays
without string-handling overhead), and amenable to fast hash-
based joins and group-by operations.

The numeric base $B$ is configurable. It is determined by the
feasibility audit on a country-and-year basis to satisfy
$B > \max(\mathrm{id}_{\mathrm{raw}})$ across all identifier
columns and all years in the planned pooled sample. The default
base $B = 10^{11}$ is appropriate for the currently inspected
France files and provides one order of magnitude of headroom; the
configuration permits adjustment for countries with larger
identifier spaces or for future France data with growing
identifier magnitudes.

An optional string composite encoding $\texttt{"\{year\}:\{id\}\textunderscore raw\}"}$ is
available as a human-readable audit and debugging representation.
The string encoding is *not* the operational default and is *not*
stored in the canonical pooled parquets; it is generated on
demand from the `int64` UID through a documented utility function
when human inspection of individual records is required.

The missing-value rule for relationship identifiers (per §6
Element I4) is enforced by the core utility: zero-valued raw
relationship identifiers map to zero-valued UIDs (under the
numeric default) or to `NULL`/`NA` values (under the optional
string encoding), not to year-prefixed encoded values.

*Rule H4 — No country-specific logic in reusable core.* The
reusable pooled-estimation core does not contain France-specific
or EUROMOD-FR-specific logic. France-specific operations (EUROMOD
system invocation, EU-SILC variable mapping, INSEE CPI retrieval)
are isolated in adapter modules that the core calls through a
documented interface. The core could, in principle, be applied to
any country's EUROMOD-derived data with the appropriate adapter
implementation.

*Rule H5 — Research scripts isolated from package core.* Any
one-off diagnostic script used only for the multi-year extension
work (e.g., the household-overlap inspection script that produced
the raw-data findings of §2) is located in the project's
`scripts/diagnostics/` directory rather than in the package's
reusable modules. Such scripts are documented as research-only
and are excluded from the package's release manifest.

The hygiene rules are not strict at the design-memo stage but
must be enforced at the implementation stage. The pooled-
estimation implementation prompt explicitly requires that the
implementation conform to H1 through H5; the implementation
report verifies conformance.

---

## 13. Sequencing within the project timeline

The multi-year track is sequenced relative to the JMP's primary
empirical track as follows.

1. *M1-clean verdict.* Completed.
2. *M1-naive implementation* (Claude Code Sonnet).
3. *M1-naive verdict* (Claude Project chat).
4. *Multi-year feasibility audit* (Claude Code Sonnet). The §4
   audit producing the feasibility report and authorising
   subsequent multi-year work. Approximately one focused session.
   The audit also records the maximum identifier magnitudes
   required by the §6 encoding scheme and the canonical
   clustering key (`idhh_raw` or `idorighh_raw`) for the cluster-
   robust inference of §8.
5. *Welfare-measurement decisions memo* (Claude Project chat).
   Methodologically independent of the multi-year track; can
   proceed in parallel with items 6 through 8.
6. *Multi-year pipeline implementation, Stage M1: CPI
   harmonisation utility and ID stacking utility* (Claude Code
   Sonnet). Implements the §5 and §6 designs as generic utilities
   conforming to the hygiene rules of §12, including the numeric
   `int64` default encoding for UIDs.
7. *Multi-year pipeline implementation, Stage M2: GSURv2 lookup
   construction for 2015 and 2017* (Claude Code Sonnet).
   Replicates the GSURv2 Stage A work for the additional years.
8. *Multi-year pipeline implementation, Stage M3: pooled MNL
   parquet construction* (Claude Code Sonnet). Stacks the
   year-specific MNL inputs, applies CPI harmonisation,
   constructs `_uid` identifiers, produces the pooled MNL
   parquets.
9. *Pooled estimation, (P2) configuration (2015 + 2016, no
   overlap)* (Claude Code Sonnet). The first clean pooled
   estimation, under naive Hessian inference (T2 provisional).
10. *Pooled estimation, (P3) configuration (2015 + 2016 + 2017,
    with overlap)* (Claude Code Sonnet). Under T2 provisional
    inference initially.
11. *Cluster-robust inference implementation* (Claude Code
    Sonnet). Implements treatment T1 as a post-estimation step
    on the (P3) estimates.
12. *SA2 verdict on pooled specification* (Claude Project chat).
    Applies the §11 promotion criteria.
13. *Temporal validation exercise* (Claude Code Sonnet, optional).
    Configuration V1 from §9 (train on 2015, test on 2017).
14. *Welfare scaffolding implementation* (Claude Code Sonnet),
    using whichever specification (single-year M1-clean or pooled
    SA2-promoted) is the JMP's primary baseline at this point.
15. *Welfare-decomposition computation and robustness exposures*.
16. *JMP draft and slides*.

Items 6 through 12 (the multi-year track) can proceed in parallel
with items 5 (welfare-measurement decisions memo) and 13
(temporal validation), reducing the critical path. The total
incremental walltime for the multi-year track is approximately
eight to ten weeks of focused work, of which the data pipeline
work (items 6 through 8) constitutes the majority.

Items 14 through 16 are sequenced after the SA2 verdict so that
the welfare scaffolding can operate against the appropriate
primary baseline. If the SA2 verdict is SA2-STANDS, the welfare
scaffolding operates against the pooled estimates; if SA2-
REVISION, the welfare scaffolding operates against the pooled
estimates with the documented qualifications; if SA2-OVERTURNED,
the welfare scaffolding operates against the M1-clean single-year
estimates and the pooled work is archived as a methodological
investigation.

---

## 14. Open questions and decisions

Four open questions remain for resolution at the implementation
or verdict stage.

*Open question O1 — Choice of pooled-estimation primary
configuration.* The §8 sequencing recommends estimating both (P2)
and (P3), with (P3) under cluster-robust inference as the
preferred final configuration. Whether (P2) or (P3) ultimately
constitutes the "primary" pooled estimate for SA2-verdict
purposes is determined by the comparison between the two: if the
(P3) cluster-robust estimates are precise enough to materially
supersede the (P2) estimates, (P3) is primary; if the cluster-
robust correction inflates the (P3) standard errors to the point
that (P2) provides comparable precision, (P2) is the more
defensible primary configuration. The SA2 verdict memo makes this
determination.

*Open question O2 — Welfare baseline under SA2-STANDS.* If the
pooled specification earns SA2-STANDS, the welfare decomposition
is computed against the pooled estimates. The reference
distribution for the welfare calculation is then a choice between
(a) the pooled distribution of households across the three years,
(b) a single year's distribution (likely 2016 for continuity),
and (c) the 2016 distribution weighted to reflect the pooled
household composition. The welfare-measurement decisions memo
articulates the appropriate choice; the multi-year strategy memo
does not pre-empt it.

*Open question O3 — Wage-block year fixed effects.* The §7
baseline pooled specification does not include wage-block year
fixed effects. Whether the residual real wage variation over
2015–2017 (approximately 1 per cent annually) warrants a
sensitivity specification with wage-block year intercepts is an
empirical question to be settled by the comparison between the
baseline pooled specification and the sensitivity specification
described in §7 E4. The sensitivity is documented as a robustness
exposure but is not part of the baseline pooled estimation.

*Open question O4 — Strong-Roemer interpretation under pooling.*
The framework memo's strong-Roemer interpretation (R9) of the
welfare results treats the within-circumstance variation as fully
preference-driven and consequently as responsibility-relevant.
Under pooled estimation, the within-circumstance variation
includes within-year variation across households, but also the
within-household variation across years (for the 8,796 repeat
households of 2016–2017). Whether this latter source of variation
is treated as preference-driven or as a residual unmodelled
opportunity component is a substantive welfare-interpretation
choice that the welfare-measurement decisions memo articulates.

The open questions do not block the multi-year implementation
work. Items 4 through 12 of the §13 sequence can proceed without
their resolution; the open questions are settled at the SA2
verdict stage and at the welfare-measurement decisions memo
stage.

---

## 15. What this memo replaces and what it does not authorise

This memo supersedes
`docs/JMP_multi_year_and_cross_validation_strategy_memo_v3.md`
through two targeted cleanup revisions documented in the revision
history. The substantive content of v3 not addressed by these
revisions is preserved unchanged in v3.1. The combined v2 → v3 →
v3.1 revision chain produces a memo that is conceptually
coherent, type-consistent in its ID design, evidence-based in its
identifier-magnitude figures, and operationally implementable
without ambiguity.

The memo does not authorise implementation of any of the listed
steps. The implementation prompts for each step are written
separately at the appropriate point in the §13 sequence. The memo
also does not authorise:

- Welfare-decomposition computation against any specification
  (pooled or single-year).
- Canonical MNL promotion of any data product.
- Modification of the M1-clean single-year specification.
- Stage B age-specific GSUR work.
- The François Maniquet pure-theory paper.

The immediate next operational step remains the M1-naive
implementation prompt for Claude Code Sonnet, as established in
the M1-clean verdict §19. The multi-year track is initiated at
step 4 of §13 (the multi-year feasibility audit) after the
M1-naive verdict is in place.

---

## 16. Summary of explicit answers to the user's seven questions

1. *How pooled 2015–2017 estimation will be constructed.* By
stacking the year-specific MNL parquets after CPI harmonisation
and stacked-ID engineering, with M1-clean's 53 parameters
preserved and year-effect parameters added to the market-
opportunity block. The (P3) 2015 + 2016 + 2017 configuration adds
two year dummies (`beta_E_year2015`, `beta_E_year2017`) with 2016
as the reference, yielding a 55-parameter specification. The (P2)
2015 + 2016 configuration adds one year dummy
(`beta_E_year2015`), yielding a 54-parameter specification. The
sequencing implements (P2) first as the first clean pooled
estimation, then (P3) as the full-data estimation under cluster-
robust inference.

2. *How CPI harmonisation is done after EUROMOD.* By running the
native-year EUROMOD systems to produce nominal monetary outputs
and then applying the CPI factor $\phi_t = \mathrm{CPI}_{2016} /
\mathrm{CPI}_t$ to disposable income, wage variables, and non-
labour income components at the alternative-row level (§5). The
base year is 2016; the CPI source is INSEE; non-monetary
variables are not transformed; the ordering is fixed (EUROMOD
first, then harmonisation).

3. *How raw IDs and stacked unique IDs coexist.* Through a two-
layer ID design (§6) in which the pooled dataset carries both
`_raw` identifiers (preserving the EUROMOD original values) and
`_uid` identifiers (constructed via a configurable encoding). The
operational default is the numeric `int64` encoding $B \cdot
\mathrm{year} + \mathrm{id}_{\mathrm{raw}}$ with $B = 10^{11}$
for the currently inspected France files; the recommended base
satisfies $B > \max(\mathrm{id}_{\mathrm{raw}}) = 9.38 \times
10^9$. The optional string composite encoding
`"{year}:{raw_id}"` is generated on demand as a human-readable
audit representation but is not the canonical column type. The
missing-value rule preserves zero-valued relationship identifiers
(no father, no mother, no partner) as zero in the numeric
encoding. The `_uid` columns serve engineering purposes only;
the `_raw` household identifiers serve as the clustering key for
cluster-robust inference.

4. *How the 2016–2017 household overlap is handled.* The 76.8 per
cent overlap (8,796 of approximately 11,400 households) is
acknowledged as a defining property of the (P3) sample structure
(§2). The corrected overlap arithmetic establishes that 51.9 per
cent of stacked observation rows in (P3) derive from repeated
households, strengthening rather than weakening the case for
cluster-robust inference. Three operational treatments are
specified (§8): cluster-robust standard errors at the raw
household level (T1, preferred final), naive Hessian standard
errors with provisional labelling (T2, interim), and
independence-preserving sample restriction (T3, sensitivity).

5. *What counts as true OOS validation given the overlap.* Only
year pairs with zero household overlap support genuine out-of-
sample validation (§9). The recommended configuration is V1:
train on 2015, test on 2017 (zero overlap, two-year temporal
gap). The v1 memo's recommendation of training on 2016 and
testing on 2017 is rejected because the 76.8 per cent overlap
contaminates the held-out set.

6. *Whether the 2016 baseline remains the primary JMP baseline
until the pooled model earns a new verdict.* Yes (§10). The
default position is that the M1-clean single-year SA1-STANDS
verdict governs until the pooled specification earns its own
SA2-style verdict. The pooled specification does not inherit
M1-clean's verdict.

7. *What evidence would justify promoting the pooled model over
the 2016-only model.* A SA2-STANDS verdict under the criteria of
§11, which require preference-parameter stability within 5 per
cent of M1-clean, region-coefficient and GSUR-coefficient
consistency, year fixed effects interpretable and significant,
Hessian conditioning preserved, partial or full resolution of the
singles consumption identification limitation, cluster-robust
inference in place, and fit diagnostics not regressing
materially. A SA2-REVISION verdict accepts the pooled
specification with documented qualifications; a SA2-OVERTURNED
verdict rejects the pooled specification and retains the M1-clean
single-year baseline.
