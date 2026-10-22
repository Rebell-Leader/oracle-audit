---
license: cc-by-4.0
tags: [antimicrobial-peptides, benchmark, model-evaluation, proteins, biology]
pretty_name: Oracle Audit - AMP evaluation-oracle score set
---

# Data card — Oracle Audit: per-peptide scores from 16 in-silico AMP oracles

**Files**
| file | shape | description |
|---|---|---|
| `oracle_audit_scores_wide.csv` | 14,977 rows x 20 cols | one row per peptide; `sequence_id, cohort, sequence, length` + one column per oracle |
| `oracle_audit_scores.parquet` | 239,632 rows | long format: `sequence_id, cohort, sequence, length, oracle, family, score` |
| `oracle_audit_verdicts.csv` | 16 rows | per-oracle sign test + depth test verdicts |
| `oracle_audit.py` | — | reusable diagnostics module + CLI |

14,977 peptides x 16 oracles = 239,632 scores. No missing values.

## Cohorts

| cohort | n | what it is / how it was built |
|---|---|---|
| `markov_order3` | 2,000 | order-3 Markov chain fitted to AMP residue composition, sampled de novo |
| `omegamp_uncond` | 2,000 | OmegAMP diffusion model, unconditional samples |
| `omegamp_targeted` | 2,000 | OmegAMP diffusion model, species/strain-conditioned samples |
| `protgpt2` | 2,000 | ProtGPT2 autoregressive protein LM samples, length-filtered to AMP range |
| `esm2_gibbs` | 2,000 | ESM-2 masked-LM Gibbs sampling from AMP-like seeds |
| `ref_MarLys_AMPs` | 2,000 | **positive reference**: curated real antimicrobial peptides |
| `ref_shuffled_decoys` | 2,000 | **separate shuffle reference**: sampled from OmegAMP shuffled-AMP data, independently of the known-AMP cohort. Only 87/2,000 compositions overlap; these are not paired controls. These are untested controls, not experimentally confirmed negatives; a composition-only model cannot distinguish a peptide from its own shuffle |
| `ref_nonAMPs` | 877 | **negative reference**: curated non-antimicrobial peptides |
| `submitted_top100` | 100 | the top-100 peptides actually submitted to a real AMP design competition, selected from a 998,452-sequence pool by mean percentile rank of amPEPpy + AMPredictor |

Sequence IDs are `<cohort>_<5-digit index>` and preserve the row order of the source `cohorts.json`.

## Oracles

**Family A — hard-negative-trained classifiers (13 columns, OmegAMP).** `broad-classifier`
(general AMP activity), 5 `species-*-classifier` columns (*A. baumannii*, *E. coli*,
*K. pneumoniae*, *P. aeruginosa*, *S. aureus*) and 7 `strains-*-classifier` columns (named ATCC
strains). Scores are activity probabilities in [0, 1]. These models were trained with
composition-matched/shuffled hard negatives in the negative set.

**Family B — published scorers (3 columns).** `ampeppy` and `amplify`
return AMP probabilities in [0, 1], thresholded at ≥0.5. `ampredictor` is a
MIC regressor: its raw outputs are not probabilities, and lower is better.
The audit uses MIC ≤16 µM for calls and ascending raw MIC for ranking.
AMPredictor's upstream model is described in
[the authors' repository](https://github.com/ruihan-dong/AMPredictor) and
[paper](https://elifesciences.org/articles/97330).

## Known caveats

1. **Provenance / licence.** All oracle weights are the *original published checkpoints* obtained
   from their respective publications and repositories (amPEPpy, AMPlify, AMPredictor, OmegAMP).
   No model was retrained or fine-tuned here. The scores in this dataset are derived outputs; the
   licences of the underlying models govern reuse of the models themselves, and anyone
   redistributing the weights must consult each original licence. Cohort sequences derive from
   public curated AMP databases and from the generative models named above.
2. **AMPredictor correction.** Earlier materials treated MIC as a probability
   and ranked it backwards. Corrected: 48.8% known AMPs and 50.5% shuffles pass
   MIC ≤16 µM; precision@100 is 0.79, and the first precision<0.75 crossing
   from k=20 is 123. The old saturation claim is withdrawn.
3. **Scores are not calibrated across families.** Family A probabilities are far lower in absolute
   terms than Family B's for the same peptide. Compare *ranks and orderings within an oracle*, not
   raw values across oracles.
4. **Shuffled decoys are a composition control, not a biological negative.** A shuffle can in
   principle be active; these separately sampled cohorts support descriptive rate and ranking
   comparisons, not isolation of sequence order or a claim about any single control.
5. **Tie handling.** Several oracles produce heavily tied scores. `depth_test` breaks ties with a
   fixed random permutation (seed 0), matching the notebook. Results can change under a different tie rule.
   The first failing depth is checked from k=20; a curve may recover later.

6. **Evidence coverage.** Exact checkpoint hashes, source database versions, the
   score-generation pipeline and a training-overlap audit are not included in this
   release. The metadata above records the project's stated provenance, not an
   independently reproduced model inference run. The 13 OmegAMP heads are related
   models; threshold-rate ordering does not establish experimental accuracy.

7. **Unpaired reference cohorts.** The source cohort builder independently samples
   positives from `amp-challenge-2027/data/antibacterial.fasta` and controls from
   `OmegAMP/data/activity-data/synthetic-data/shuffled-AMP-sequences.fasta`.
   Only 87 of 2,000 composition signatures match as multisets. These contrasts
   confound cohort composition with sequence order. Use `--require-paired` to
   reject such input for a paired audit. Source excerpt and hashes are recorded
   in `SUBMISSION_REVIEW.md` (in the GitHub repository, under `submission/`).

8. **Conflicting reference labels.** There are 45 exact sequences shared by the
   released AMP and non-AMP reference cohorts. Also, 861/877 non-AMP references
   appear in the full antibacterial source library. Activity definitions across
   assays, strains and cutoffs have not been harmonised; do not assume clean
   binary ground truth from these file labels.
9. **OmegAMP source-pool reuse.** All 2,000 shuffle and 877 non-AMP references are
   present in negative-data pools read by OmegAMP's dataset builder; 197 reference
   AMPs occur in its curated-positive pool. This establishes source-pool overlap,
   not membership in the exact fitted checkpoint training split. See
   `source_provenance.json` and the source-project follow-up in submission/SUBMISSION_REVIEW.md.
