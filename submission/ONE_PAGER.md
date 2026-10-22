# Oracle Audit

> **Control-cohort correction:** The released known-AMP and shuffle cohorts were
> sampled from different source files. Only 87 of 2,000 amino-acid compositions
> overlap. The rates and depth curves below describe those separate cohorts;
> they do not isolate sequence order. A genuinely paired, rescored experiment
> is still needed. The explorer does construct an exact shuffle of each input.
> The AMP/non-AMP cohorts also share 45 exact sequences with conflicting labels.
> Training-source overlap is documented; exact checkpoint split overlap is unresolved.


**Check the scoring model before selecting peptides.**

OSI Hackathon 2026 · Hypothesis Generation and Evaluation

[Code](https://github.com/Rebell-Leader/oracle-audit) ·
[App](https://huggingface.co/spaces/avaliev/oracle-audit) ·
[Data](https://huggingface.co/datasets/avaliev/oracle-audit-amp-scores)

## Problem

Peptide design tools use prediction scores to choose candidates for lab testing.
We ask whether those scores distinguish known antimicrobial peptides (AMPs) from
shuffled versions containing exactly the same amino acids.

## Test and result

We collected scores for 14,977 peptides from 16 models. The main comparison uses
2,000 curated AMPs, a separately sampled 2,000-sequence shuffle cohort, and 877 curated non-AMPs.

At a 0.5 threshold, amPEPpy calls **87.5% of shuffles** positive versus **66.8% of
known AMPs**. AMPlify gives **87.6% versus 65.8%**. OmegAMP broad gives **0.0% versus
14.4%**, while missing most known AMPs at that threshold.

Ranking a 50/50 AMP/shuffle pool shows why selection depth matters. Precision@100
is 0.92, 0.90 and 1.00 respectively. The first depth below 0.75, checking from k=20,
is **267, 242 and 693** with a fixed random tie rule. These fractions measure known
AMP enrichment, not experimental success.

AMPredictor is a MIC regressor: lower is better. At MIC ≤16 µM, 48.8% of known AMPs
and 50.5% of shuffles pass. Treating its outputs as probabilities is incorrect.

## Deliverables

A CLI and notebook provide two checks: compare positive rates at a chosen threshold,
and plot precision over selection depth. The dataset includes all 239,632 scores.
The browser explorer compares a peptide and its shuffle with helical wheels and
an idealised helix. A composition-only surrogate illustrates why identical
composition produces identical scores. A Markov sampler supplies new controls.

## Limits and practical use

Shuffles are untested controls, not confirmed negatives. Related OmegAMP heads are
not independent experiments, and training overlap has not been audited. The
surrogate imitates model calls; it does not predict measured activity. Use these
checks to question a screening metric, then validate candidates experimentally.

A Valency-assisted survey found no shuffle control mentioned in 30 relevant
abstracts or in the five full texts inspected. That does not establish absence
across the field. Marimo provides the browser notebook; Hugging Face hosts the
app and dataset. The Adaption training run has completed: best win rate 0.528 against a 0.70 target,
and at chance on a 400-row held-out check (accuracy 0.488-0.500), collapsing to one
label. It is reported as a failed attempt at the fix, not as a result.
