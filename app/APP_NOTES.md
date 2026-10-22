# Oracle Audit notebook

The notebook runs locally with marimo or in the browser through its WASM export.
The audit panels use 4,977 stored reference/submission rows from the released
CSV. Python recomputes rates and curves; it does not run the original checkpoints.

## What runs where

- Threshold rates, depth curves and the cross-model table use stored full-precision
  model scores. Both the CLI and app use the same seed-0 tie rule and pool order.
- The explorer computes charge, hydrophobicity and hydrophobic moment from a
  sequence, then constructs an exact shuffle. Wheels assume 100° per residue.
- The 3D view is an idealised CA/CB helix, not a structure prediction. Two viewers
  use 3Dmol.js from a CDN. Offline, the wheels remain available.
- The composition-only logistic surrogate imitates amPEPpy's calls. It is not
  amPEPpy and does not predict measured activity. Stored AUROC values are offline
  training summaries, not recomputed model fits.
- The order-2 Markov sampler scores its output with that surrogate. The downloaded
  FASTA contains surrogate scores.

## Data limitation

The known-AMP and shuffle cohorts were sampled independently. Only 87 of 2,000
compositions overlap. Their rates and depth curves are exploratory cohort
comparisons, not an exact composition-matched experiment. The explorer's own
sequence/shuffle comparison is exact. See `../SUBMISSION_REVIEW.md`.

AMPredictor returns raw predicted MIC: lower is better. Its default positive
cutoff is MIC ≤16 µM. All other models use score ≥0.5 by default. Changing a call
threshold changes rates; it does not change a full-pool ranking curve.

## Build

```bash
uv run --with marimo==0.25.0 --with numpy --with pandas --with altair --with matplotlib \
  marimo run app/oracle_audit_app.py
uv run --with marimo==0.25.0 --with numpy --with pandas --with altair --with matplotlib \
  marimo export html-wasm app/oracle_audit_app.py -o app/site --mode run
python -m http.server 8765 --bind 127.0.0.1 --directory app/site
```

`docs/` mirrors `app/site/` for publication. The static HTML and single-file WASM
HTML are alternative exports. Browser-runtime packages still need network access
on an uncached first load; the embedded data avoid additional data-file fetches.

`_app_template.py` mirrors the notebook with `@@DATA_B64@@` and `@@ASSETS_B64@@`
placeholders. Its placeholder values must be replaced before execution.

## Verification

`video/verify_analysis.py` executes all 34 cells, checks the 14,977-row released
table and its composition overlap, and verifies all 16 full depth curves match
the CLI exactly. `package/test_oracle_audit.py` covers numerical regressions.

The public HF app and corrected local WASM export both booted in headless Google
Chrome. The local app's controls, charts and 3D canvases are exercised during
`video/record_walkthrough.py`. Screenshots and metadata accompany the capture.
This replaces the previous build's “not verified in a browser” status.

No public deployment is updated by these local build or recording commands.
