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
- **Status at submission:** running (iteration 0 of 3 at the time of writing). The held-out set and
  `score_holdout()` are included so the finished checkpoint can be scored with the audit's own sign
  test — real recall and decoy recall reported separately, which is the whole point: an oracle that
  calls everything antimicrobial (AMPredictor flags >99% of every cohort) scores well on one and not
  the other.

We are not claiming a trained oracle as a result. We are claiming the audit, the dataset, and a
launched, reproducible attempt at the fix.
