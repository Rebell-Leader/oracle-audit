# Adaption Labs track — training the oracle the audit says is missing

The audit's negative result is that the published AMP oracles are blind to composition-preserving
shuffles. The constructive test is whether that discrimination is learnable at all, so we fine-tuned a
general-purpose model on exactly the contrast the published oracles fail.

- **Data:** 4,000 balanced examples built from this repo's cohorts — 2,000 real curated AMPs vs 2,000
  composition-preserving shuffles of real AMPs. 3,600 train (`hardneg_train.csv`, uploaded to Adaption
  with `processing_mode="raw"`), 400 held out (`hardneg_holdout.csv`, never uploaded).
- **Platform:** Adaption Python SDK 0.15.0 — `datasets.upload_file` -> `datasets.get_status` ->
  `autoscientist.create`.
- **Run:** `google/gemma-3-4b-it`, training method `instruction`, max 3 iterations, target win rate
  0.70. Dataset `94df0d0b-85e7-43b6-aa1f-b572d6252cf3`, run `ac56c29d-78fa-4e01-95f9-91689f4d72fe`,
  launched 2026-10-22 21:16 UTC.
- **Status:** completed. See the result section below. The held-out set and
  `score_holdout()` are included so the finished checkpoint can be scored with the audit's own sign
  test — real recall and decoy recall reported separately, which is the whole point: an oracle that
  calls everything antimicrobial (AMPredictor flags >99% of every cohort) scores well on one and not
  the other.

We are not claiming a trained oracle as a result. The attempt ran to completion and did not
produce a working oracle; the numbers are below.

## Result (run completed 22 Oct 2026, 22:29 UTC)

The run **succeeded**: 3 of 3 iterations in 73 minutes. Best win rate **0.5281** against a
0.70 target, so AutoScientist's own objective was not met. Its training record converged
(loss 13.12 -> 0.147, eval_loss 0.146 at step 63; LoRA r=32, alpha=64, 3 epochs, lr 3e-5,
cosine schedule) — the low loss reflects learning the one-word answer format, not the
discrimination.

### Held-out check with the audit's own sign test

400 rows that were never uploaded, scored by comparing the log-probability of `real` against
`shuffled`. Real-recall and decoy-recall are reported separately, because a model that answers
one label for everything looks good on one and useless on the other.

| Model | Prompt format | Accuracy | Real recall | Decoy recall | Predicted "real" |
|---|---|---:|---:|---:|---:|
| AutoScientist LoRA | chat template | 0.488 | 0.000 | 1.000 | 0.0% |
| AutoScientist LoRA | plain | 0.500 | 0.717 | 0.272 | 72.3% |
| Base gemma-3-4b-it | chat template | 0.488 | 0.024 | 0.974 | 2.5% |
| Base gemma-3-4b-it | plain | 0.510 | 0.785 | 0.221 | 78.3% |

**The fine-tune did not learn the discrimination.** It sits at chance (0.488-0.500) and is
degenerate: under the chat template it answers `shuffled` for every one of the 400 sequences,
and under plain concatenation it answers `real` for 72% of them. The base model is equally at
chance. Fine-tuning moved the collapse point, not the discrimination.

Two honest qualifications. First, the training task inherits the **unpaired-cohort flaw**
described in the repository README: the positives and the shuffle cohort come from different
source files, so the label partly tracks provenance rather than residue order, and this result
must not be read as "sequence order is unlearnable". Second, this is one recipe at one scale —
3,600 examples, LoRA on a 4B model — not evidence about what a larger or better-posed training
run could do.

### Reproducing the evaluation

`eval_holdout.py` runs it. Two details are needed to make the released checkpoint load at all:

1. The adapter declares its base as `togethercomputer/gemma-3-4b-it`, which is not a public
   repository; we substituted **`google/gemma-3-4b-it`** and state that substitution with the
   numbers above.
2. The adapter's tensors are named for the **text-only** Gemma-3 layout
   (`base_model.model.model.layers.*`), while `google/gemma-3-4b-it` is the multimodal variant
   whose language tower lives under `model.language_model.*`. Loading it as shipped leaves every
   `lora_B` at its zero initialisation, so the adapter silently has **no effect** — the first
   evaluation we ran returned numbers identical to the base model to four decimals, which is how
   we caught it. `checkpoint/extracted_mm` holds the remapped copy; after remapping, all 238
   language-tower `lora_B` tensors are non-zero and the next-token logits shift by up to 1.17.

The checkpoint itself is not committed (225 MB compressed, ~520 MB extracted); download it with
`client.autoscientist.download("ac56c29d-78fa-4e01-95f9-91689f4d72fe")`.
