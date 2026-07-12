# Occupation wage-separation diagnostic (decision-note §4)

## Sex F  (n=730)
eta^2(log wage ~ loc4) = **0.213**

|   loc4 |   count |   mean |   std |   min |   10% |   25% |   50% |   75% |   90% |   max |
|-------:|--------:|-------:|------:|------:|------:|------:|------:|------:|------:|------:|
|      1 |     138 |  2.394 | 0.405 | 1.155 | 1.935 | 2.211 | 2.412 | 2.575 | 2.789 | 4.551 |
|      2 |     141 |  2.333 | 0.485 | 0.8   | 1.722 | 2.173 | 2.421 | 2.65  | 2.818 | 3.556 |
|      3 |      99 |  2.55  | 0.254 | 1.617 | 2.262 | 2.441 | 2.549 | 2.717 | 2.85  | 3.222 |
|      4 |     352 |  2.805 | 0.389 | 1.035 | 2.353 | 2.587 | 2.8   | 3.023 | 3.264 | 4.285 |

IQR by loc4: 1: [2.21,2.57], 2: [2.17,2.65], 3: [2.44,2.72], 4: [2.59,3.02]

## Sex M  (n=611)
eta^2(log wage ~ loc4) = **0.128**

|   loc4 |   count |   mean |   std |   min |   10% |   25% |   50% |   75% |   90% |   max |
|-------:|--------:|-------:|------:|------:|------:|------:|------:|------:|------:|------:|
|      1 |     234 |  2.527 | 0.409 | 0.724 | 2.092 | 2.347 | 2.525 | 2.739 | 2.948 | 4.426 |
|      2 |      61 |  2.572 | 0.448 | 1.554 | 2.011 | 2.302 | 2.519 | 2.759 | 3.236 | 3.903 |
|      3 |      33 |  2.534 | 0.441 | 1.01  | 2.248 | 2.358 | 2.536 | 2.801 | 2.973 | 3.389 |
|      4 |     283 |  2.857 | 0.418 | 1.076 | 2.4   | 2.652 | 2.867 | 3.118 | 3.352 | 4.06  |

IQR by loc4: 1: [2.35,2.74], 2: [2.30,2.76], 3: [2.36,2.80], 4: [2.65,3.12]

## Verdict (rule: eta2>~0.10-0.15 => conditional; <0.05 => keep unconditional)
DECISION: SEPARATED (eta^2 F=0.213, M=0.128; both >= the 0.10-0.15 threshold) -> occupation-conditional wage draws ADOPTED for the next rebuild (P2), per the pre-committed rule in JMP_conditional_wage_on_occupation_decision_note_v1. Accepted-wage selection caveat flagged per note §4.

Caveat (per note §4): accepted-wage selection, flagged not fixed.