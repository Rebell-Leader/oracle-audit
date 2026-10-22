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
| `ref_shuffled_decoys` | 2,000 | **hard decoy reference**: per-sequence random permutations of the curated real AMPs — identical amino-acid composition and length, destroyed sequence order. A valid AMP oracle must score these *below* the real AMPs; a composition-only oracle cannot tell them apart |
| `ref_nonAMPs` | 877 | **negative reference**: curated non-antimicrobial peptides |
| `submitted_top100` | 100 | the top-100 peptides actually submitted to a real AMP design competition, selected from a 998,452-sequence pool by mean percentile rank of amPEPpy + AMPredictor |

Sequence IDs are `<cohort>_<5-digit index>` and preserve the row order of the source `cohorts.json`.

## Oracles

**Family A — hard-negative-trained classifiers (13 columns, OmegAMP).** `broad-classifier`
(general AMP activity), 5 `species-*-classifier` columns (*A. baumannii*, *E. coli*,
*K. pneumoniae*, *P. aeruginosa*, *S. aureus*) and 7 `strains-*-classifier` columns (named ATCC
strains). Scores are activity probabilities in [0, 1]. These models were trained with
composition-matched/shuffled hard negatives in the negative set.

**Family B — widely-used published classifiers (3 columns).** `ampeppy` (amPEPpy, random-forest
AMP classifier), `amplify` (AMPlify, attentive BiLSTM), `ampredictor` (AMPredictor, graph/feature
hybrid, score here used as an antimicrobial probability). Scores are probabilities in [0, 1];
conventional decision threshold p >= 0.5.

## Known caveats

1. **Provenance / licence.** All oracle weights are the *original published checkpoints* obtained
   from their respective publications and repositories (amPEPpy, AMPlify, AMPredictor, OmegAMP).
   No model was retrained or fine-tuned here. The scores in this dataset are derived outputs; the
   licences of the underlying models govern reuse of the models themselves, and anyone
   redistributing the weights must consult each original licence. Cohort sequences derive from
   public curated AMP databases and from the generative models named above.
2. **`ampredictor` saturates.** It assigns p >= 0.5 to >99% of every cohort including curated
   non-AMPs, so its threshold-level positive rate carries almost no information; its depth-test
   curve is the informative diagnostic.
3. **Scores are not calibrated across families.** Family A probabilities are far lower in absolute
   terms than Family B's for the same peptide. Compare *ranks and orderings within an oracle*, not
   raw values across oracles.
4. **Shuffled decoys are a composition control, not a biological negative.** A shuffle can in
   principle be active; the claim this dataset supports is about *ordering* (real AMPs should
   outrank their own shuffles on average), not about any single decoy.
5. **Tie handling.** Several oracles produce heavily tied scores. `depth_test` breaks ties with a
   fixed random permutation (seed 0), which is the conservative choice; precision@k values can
   shift by a few percent under a different tie rule.
