# Oracle Audit — interactive marimo notebook

`oracle_audit_app.py` is a [marimo](https://marimo.io) notebook (marimo 0.25.0) that re-runs the
Oracle Audit live: pick any of the **16 oracles** (13 Family-A OmegAMP classifiers — broad, 5
species, 7 strains — plus Family-B amPEPpy, AMPlify, AMPredictor), move the decision threshold,
and watch four things recompute from per-peptide scores — the positive rate on real AMPs vs
their own composition-preserving shuffled decoys vs curated non-AMPs, a live **SIGN INVERTED /
ordering preserved** verdict, overlaid score distributions for the three reference cohorts, and
the precision-vs-selection-depth curve on the 50/50 real-AMP/decoy pool with k\* (the depth at
which precision@k first falls below 0.75, k ≥ 20) marked. A closing table runs the same audit
across all 16 oracles at once. **To run it locally:** `pip install marimo altair numpy pandas`
then `marimo edit oracle_audit_app.py` (or `marimo run oracle_audit_app.py` for the read-only
app). **WASM export path:** `marimo export html-wasm oracle_audit_app.py -o site/ --mode run`
(requires `uv` on PATH to resolve the script's inlined dependencies) produces the no-login,
no-server bundle in `site/` — serve it with `python -m http.server --directory site`, or drop
the directory on any static host (GitHub Pages / Cloudflare Pages; `.nojekyll` is already
included). `oracle_audit_app.wasm.html` is the same export as one self-contained file
(`--single-file`, assets from CDN) that opens directly in a browser, and
`oracle_audit_static.html` is the non-interactive `marimo export html` fallback with all cell
outputs baked in. The scores for the four reference cohorts (4,977 peptides × 16 oracles) are
embedded in the notebook as a gzip+base64 blob (~260 kB), so the exported app fetches no data
at runtime; the full source tables (`cohorts.json`, `scores_familyA.npz`, `scores_familyB.npz`,
`dual_family_summary.csv`, `tail_precision.csv`, covering all 14,977 sequences) are copied
under `data/` for provenance.
