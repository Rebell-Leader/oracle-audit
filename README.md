# Oracle Audit

**Benchmark-validity diagnostics for generative antimicrobial-peptide (AMP) design.**

Submission to the Open Scientific Intelligence (OSI) Hackathon 2026 — bucket: *Hypothesis Generation and Evaluation*.

## The finding

Generative AMP design is scored almost entirely by *in-silico oracles*: published AMP classifiers that
stand in for a wet-lab MIC assay. We audited two families of these oracles against the same
14,977-sequence cohort set (9 cohorts, 16 oracles) and found that **they disagree in sign on the central validity contrast.**

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

The published oracles look strong at the depth their own papers report. Screening real AMPs out of a
4,000-sequence 50/50 pool against shuffled decoys, amPEPpy reaches precision@100 = 0.92 and AMPlify
0.90, against 1.00 for OmegAMP's broad classifier (AMPredictor is already at 0.79). Precision@100 is
the standard reported metric, and at that depth the three look comparable.

The families separate deeper in the ranking. Precision falls below 0.75 at **k = 265** (amPEPpy) and
**k = 240** (AMPlify), versus **k = 691** for OmegAMP's broad classifier — a 2.6x difference in usable
selection depth, invisible at the depth everyone reports. AMPredictor never clears the floor at all:
it flags >99% of every cohort, real or shuffled.

Across all 16 oracles the split is clean: **3 of 3 Family-B oracles are sign-inverted; 13 of 13
Family-A oracles are not.**

Real campaigns do not stop at a hundred. A submission pipeline we examined selected the top
50,000 of a 998,452-sequence pool by mean percentile rank of amPEPpy + AMPredictor — roughly 200x
deeper than the depth at which those oracles still hold precision.

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

## Literature grounding (Valency Bond)

We used the Valency Bond MCP connector to check how the field actually evaluates generators. Of 45
screened corpus records, 30 both generate candidate peptides and evaluate them in silico; 28 of those
30 do not name their evaluation oracle in the abstract, and **0 of 30 mention any decoy or
composition-preserving shuffled-sequence control**. For the 5 most-cited papers we read the methods:
all 5 score with their own internal classifier, 2 additionally apply published third-party oracles
(HydrAMP: AMPlify, CAMPR3-rf, STM; AMP-Designer: CAMP, AMP Scanner, Macrel) — every one of which
belongs to the single conventionally-trained family our audit shows is sign-inverted — and none
applies a shuffled-sequence control. *More than one oracle is not more than one oracle family.*
Screening of the other 25 papers is abstract-level, so "oracle not named" means not stated, not not used.

## Sponsor tracks used

- **Valency (Bond MCP)** — literature grounding; see `lit/valency_claim.md` and `lit/oracle_practice_survey.csv`.
- **Marimo** — the interactive audit notebook (`app/oracle_audit_app.py`), WASM-exported;
  live at https://huggingface.co/spaces/avaliev/oracle-audit
- **Adaption** — a hard-negative oracle fine-tune launched on AutoScientist; see `adaption/README.md`.
- **Hugging Face** — dataset: https://huggingface.co/datasets/avaliev/oracle-audit-amp-scores

Quick start:

```bash
python package/oracle_audit.py --scores package/oracle_audit_scores_wide.csv --all
```

## Provenance

All cohorts, scores and the depth analysis were produced during the hackathon window on the authors'
own hardware. Oracle weights come from their original publications; see `DATA_CARD.md` for per-oracle
provenance and licence caveats.
