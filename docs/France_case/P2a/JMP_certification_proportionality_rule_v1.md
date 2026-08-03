# JMP Certification Proportionality Rule v1

**Status:** Binding programme-governance rule  
**Applies from:** JMP-M05C Increment B closure onward  
**Decision-maker:** Principal Investigator and ChatGPT JMP Deputy Programme Director

## 1. Purpose

The JMP exists to produce a credible economics paper and a usable research
package. Software certification is instrumental to scientific validity; it is
not an independent programme objective.

Review depth must therefore be proportionate to the scientific and disclosure
risk of the task.

## 2. Blocking defect classes

A review finding may block progression only when it materially affects at least
one of the following:

1. econometric or statistical correctness;
2. use of the accepted likelihood, data, parameter map, estimate, Hessian, or
   covariance formula;
3. actual execution of the claimed production path;
4. reproducibility of a reported numerical result;
5. provenance or mutation of accepted artifacts;
6. persistence or disclosure of household-level or otherwise restricted data;
7. irreversible corruption, overwrite, or loss of accepted evidence;
8. violation of an explicit paper-facing interpretation rule.

## 3. Nonblocking defect classes

The following are ordinarily recorded as technical debt rather than used to
stop the JMP:

- theoretical bypasses requiring a caller to rewrite or monkeypatch source;
- internal API purity beyond what the production runner uses;
- stylistic refactors;
- helper visibility with no production or disclosure consequence;
- redundant metadata;
- additional security hardening beyond the declared threat model;
- proof-format or documentation imperfections that do not prevent reproduction;
- hypothetical lifecycle states not used by the approved workflow.

A nonblocking issue may still be fixed when the correction is trivial and
localized, but it does not justify another open-ended review cycle.

## 4. Review-scope rule

Every review must begin from a pre-registered finite gate list.

The reviewer may identify new blocking findings only when they fall within
Section 2. Other findings are recorded as nonblocking technical debt.

Reviews are not invitations to broaden the threat model or redesign internal
software architecture.

## 5. Production-path rule

Tests supporting a production claim must execute the actual production
functionality under review. Replacing the evaluator, reducer, serializer, or
runner with a fixture invalidates that proof.

Bounded fixtures may reduce sample size or substitute synthetic inputs, but
they may not replace the subject whose behavior is claimed.

## 6. Remediation rule

For each increment:

- one implementation review;
- at most one bounded correction;
- one focused verification of that correction.

A second broad rejection is not followed by another general hardening cycle.
The programme manager either:

1. accepts documented nonblocking limitations;
2. orders one closed-form correction of a genuine Section-2 blocker; or
3. redesigns or abandons the feature.

## 7. Current application

For JMP-M05C Increment B:

- the numerical and econometric core is accepted;
- residuals concerning T-22 caller override and post-write grade validation are
  mechanical implementation defects;
- the unrestricted `extra=` persistence channel is a genuine disclosure blocker;
- all three are sufficiently localized to close together through one finite,
  test-first mechanical correction;
- no further broad Increment-B audit is authorized.
