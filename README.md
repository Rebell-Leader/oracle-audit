# Oracle Audit

**Benchmark-validity diagnostics for generative antimicrobial-peptide (AMP) design.**

Submission to the Open Scientific Intelligence (OSI) Hackathon 2026 — bucket: *Hypothesis Generation and Evaluation*.

## The finding

Generative AMP design is scored almost entirely by *in-silico oracles*: published AMP classifiers that
stand in for a wet-lab MIC assay. We audited two families of these oracles against the same
14,977-sequence cohort set and found that **they disagree in sign on the central validity contrast.**

At the conventional `p >= 0.5` threshold:

| Cohort | amPEPpy | AMPlify | OmegAMP broad-classifier |
|---|---|---|---|
| Real curated AMPs (n=2000) | 66.8 % | 65.8 % | 14.4 % |
| **Composition-preserving shuffled decoys** (n=2000) | **87.5 %** | **87.6 %** | **0.0 %** |
| Curated non-AMPs (n=877) | 77.8 % | 79.8 % | 0.3 % |

The widely used published classifiers (Family B) call *shuffled decoys* antimicrobial more often than
they call *real antimicrobial peptides* antimicrobial. Any generator ranked by these oracles is being
rewarded for reproducing amino-acid composition, not for activity. Hard-negative-trained classifiers
(Family A) order the same three cohorts correctly.

## Why it has gone unnoticed: selection depth

Both families look fine at the depth their own papers report. Screening real AMPs out of a 50/50 pool
against shuffled decoys, **every oracle reaches precision@100 = 1.00** — and precision@100 is the
standard reported metric. The families separate only deeper in the ranking: precision falls below 0.75
at k = 125 (AMPredictor) and k = 342 (amPEPpy), versus k = 729 for OmegAMP's broad classifier.

Real pipelines select far deeper than k = 100. A submission pipeline we examined selected the top
50,000 of a 998,452-sequence pool by mean percentile rank of amPEPpy + AMPredictor — a depth at which
those oracles are near chance on the decoy contrast.

## What this repo gives you

1. **`oracle_audit.py`** — two drop-in diagnostics that run against *any* scorer, not just these:
   - **sign test** — does the oracle rank composition-preserving decoys above real positives?
   - **depth test** — precision as a function of selection depth, and the depth at which it breaks.
2. **The audit dataset** — per-peptide scores for 14,977 sequences x 16 oracles (13 Family-A, 3 Family-B)
   across 9 cohorts, released as a tidy table with a data card.
3. **An interactive marimo notebook** — pick an oracle, move the threshold, watch the verdict and the
   depth curve recompute live. Runs in the browser with no login and no server (WASM export).

## Recommendation for benchmark designers

Deep filtering should use hard-negative-trained classifiers; Phase-1-style published oracles belong only
in a shallow final re-rank; and every evaluation should hold out one oracle from each family as a
cross-family control, with a composition-preserving shuffled-decoy cohort reported alongside.

## Provenance

All cohorts, scores and the depth analysis were produced during the hackathon window on the authors'
own hardware. Oracle weights come from their original publications; see `DATA_CARD.md` for per-oracle
provenance and licence caveats.
