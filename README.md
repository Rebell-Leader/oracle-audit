# Oracle Audit

> **Control-cohort correction:** The released known-AMP and shuffle cohorts were
> sampled from different source files. Only 87 of 2,000 amino-acid compositions
> overlap. The rates and depth curves below describe those separate cohorts;
> they do not isolate sequence order. A genuinely paired, rescored experiment
> is still needed. The explorer does construct an exact shuffle of each input.
> The AMP/non-AMP cohorts also share 45 exact sequences with conflicting labels.
> Training-source overlap is documented; exact checkpoint split overlap is unresolved.


Check a peptide scoring model before using it to select new candidates.

Built for the OSI Hackathon 2026, Hypothesis Generation and Evaluation track.

## The question

Antimicrobial peptides (AMPs) are short proteins with antimicrobial activity.
Design pipelines use prediction models, sometimes called *oracles*, to choose
which generated peptides to test. Do those scores distinguish known AMPs from
sequences with the same amino acids in a different order?

We scored 14,977 peptides with 16 models. The main control compares 2,000 curated
AMPs with 2,000 sequences from a separate shuffle cohort. Shuffling preserves length
and amino-acid composition. **The shuffles are untested controls, not confirmed
inactive peptides.**

## Results on the reference cohorts

Percentage passing a score threshold of 0.5:

| Cohort | amPEPpy | AMPlify | OmegAMP broad |
|---|---:|---:|---:|
| Known AMPs (2,000) | 66.8% | 65.8% | 14.4% |
| Shuffled AMPs (2,000) | 87.5% | 87.6% | 0.0% |
| Curated non-AMPs (877) | 77.8% | 79.8% | 0.3% |

amPEPpy and AMPlify call more shuffles positive than known AMPs. OmegAMP broad
shows the opposite threshold contrast, but also misses most known AMPs at this
threshold. This comparison alone does not establish which model best predicts
experimental activity.

We also rank the 2,000 known AMPs and 2,000 shuffle-cohort sequences together. Precision@k is the
fraction of known AMPs among the first k entries; it is not experimental hit rate.

| Model | Precision@100 | First k with precision < 0.75, checking from k=20 |
|---|---:|---:|
| amPEPpy | 0.92 | 267 |
| AMPlify | 0.90 | 242 |
| OmegAMP broad | 1.00 | 693 |
| AMPredictor | 0.79 | 123 |

Ties use a fixed random permutation, seed 0. These are first crossings, not the
largest depths where precision ever exceeds the floor. Values depend on the
reference pool, its 50/50 mixture and the tie rule.

**AMPredictor predicts MIC, not probability.** Lower is better. At MIC ≤16 µM,
48.8% of known AMPs and 50.5% of shuffles pass. Earlier materials incorrectly
used a probability threshold and reversed its ranking; those results are superseded.
The score table contains raw MIC outputs for this model.

## What you can use

- [Diagnostics and CLI](package/oracle_audit.py): compare positive rates at a
  threshold, then inspect precision across selection depths. The “sign test” is
  a descriptive rate comparison, not a statistical significance test.
- [Score table](package/oracle_audit_scores_wide.csv): 14,977 sequences × 16 models,
  across nine cohorts. See the [data card](package/DATA_CARD.md).
- [Interactive notebook](app/oracle_audit_app.py): change scorer and threshold,
  compare a sequence with its exact shuffle, and sample new control sequences.
- [Submission overview](submission/ONE_PAGER.md), [writeup](submission/WRITEUP.md),
  [voiceover script](submission/VIDEO_SCRIPT.md) and [review of this submission](submission/SUBMISSION_REVIEW.md).

```bash
uv run --with numpy --with pandas python package/oracle_audit.py \
  --scores package/oracle_audit_scores_wide.csv --all
```

For an additional MIC-like scorer, use `--lower-is-better COLUMN` and set its
cutoff with `--threshold`. AMPredictor automatically uses `--mic-cutoff` (default 16).

## What the explorer shows

The browser runs a 21-feature logistic surrogate trained to imitate amPEPpy's
binary calls, using amino-acid frequencies and length. It is **not amPEPpy**.
The stored held-out AUROC is 0.868; an offline gradient-boosted surrogate reports
0.945. These values measure agreement with model calls, not biological activity.
The repository includes surrogate weights and reported metrics, but not a full
training pipeline or saved train/test indices; we have not independently refit it.

A composition-only model gives a peptide and its shuffle identical scores by
construction. Helical wheels illustrate how order can change a geometric feature.
The 3D helix is idealised, not a structure prediction. The Markov demo scores
samples with the surrogate; it does not test whether the original model is fooled.

## Scope and next steps

Report shuffled controls and precision at the selection depth you intend to use.
Check performance on independent activity data before choosing a screening model.
The 13 OmegAMP heads are related models, not 13 independent replications. We have
not audited training overlap, calibrated scores, or measured shuffled-peptide
activity. This audit does not prove that hard-negative training caused the difference.

The Valency survey screened 30 relevant abstracts and inspected five full texts.
No shuffled control was mentioned in those abstracts or found in those five texts.
That is a result about this sample, not the entire field; see
[the survey and its limits](lit/valency_claim.md).

## Repository layout

| Path | Contents |
|---|---|
| [`package/`](package) | Diagnostics, CLI, tests, released score table, data card, provenance check |
| [`app/`](app) | The marimo notebook, its assets and the exported WASM bundle |
| [`lit/`](lit) | Valency Bond literature survey and its stated limits |
| [`adaption/`](adaption) | Hard-negative fine-tune: data builder, held-out set, run record |
| [`docs/`](docs) | GitHub Pages copy of the exported app |
| [`submission/`](submission) | Hackathon entry copy: overview, writeup, post, form answers, review, scripts |
| [`media/`](media) | Video build scripts, captured stills and verification records |

## Reproduce the checks

```bash
python -m pytest package/test_oracle_audit.py -q          # 8 unit tests on the diagnostics
python media/verify_analysis.py                           # notebook curves vs the released table
python package/check_source_provenance.py <source-project> # cohort overlap and source membership
```

The last verification run recorded all 16 notebook curves matching the CLI across 14,977 rows,
87 overlapping compositions between the reference cohorts, and 45 sequences shared between the
AMP and non-AMP cohorts ([`media/analysis_verification.json`](media/analysis_verification.json),
[`package/source_provenance.json`](package/source_provenance.json)).

## Links and build

- [Public app](https://huggingface.co/spaces/avaliev/oracle-audit)
- [Dataset](https://huggingface.co/datasets/avaliev/oracle-audit-amp-scores)
- [Build and verification notes](app/APP_NOTES.md)
- [Revised overview video (2:30)](oracle_audit_video_revised.mp4)
- [Voiced overview](oracle_audit_video_voice.mp4)
- [Raw Chrome capture (60 seconds)](media/oracle_audit_app_capture.mp4)
- [Recording instructions](submission/RECORD_VIDEO.md)

Public deployments may lag the revised local files. No remote publication is
performed by the recording workflow.

## Source-project follow-up

Inspection of the original source found **45 exact sequences shared by the AMP
and non-AMP reference cohorts**. All shuffle and non-AMP references also occur in
negative-data source pools read by OmegAMP's dataset builder; exact checkpoint
training membership remains unverified. These findings require label and split
reconciliation before stronger validation claims. See the
[source-project follow-up](submission/SUBMISSION_REVIEW.md#source-project-follow-up-23-october)
and [reproducible provenance check](package/check_source_provenance.py).
