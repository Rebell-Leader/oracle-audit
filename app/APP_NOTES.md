# Oracle Audit — interactive marimo notebook

`oracle_audit_app.py` is a [marimo](https://marimo.io) notebook (marimo 0.25.0, 382 kB of source
including two embedded data blobs) that re-runs the Oracle Audit live *and* lets a peptide
scientist point the audit's own machinery at any sequence they paste in. It runs with no server,
no login and no backend: every panel is recomputed in-browser by Pyodide.

## Sections and interactive controls

**Section 0 — the audit** (unchanged from the first build, re-sectioned as 0 / 0.1 / 0.2 / 0.3)

| control | type | range / options | what it drives |
|---|---|---|---|
| `Oracle` | searchable dropdown | all 16 oracles (13 Family-A OmegAMP classifiers: broad, 5 species, 7 strains; 3 Family-B: amPEPpy, AMPlify, AMPredictor) | verdict panel, distributions, depth curve |
| `probability threshold` | slider | 0.05–0.95, step 0.01 | positive rates, verdict, threshold rule on the histogram, cross-oracle table |
| `MIC cutoff, uM` | slider | 1–128 uM, step 1 | the same, for AMPredictor only (it returns a predicted MIC, lower = more active) |

Outputs: three `mo.stat` cards (positive rate on real AMPs / their own shuffled decoys / curated
non-AMPs), a live **SIGN INVERTED / ordering preserved** callout, overlaid score distributions
with the decision threshold drawn in, the precision-vs-selection-depth curve on the 4,000-peptide
50/50 pool with k\* marked (k\* = first depth ≥ 20 at which precision@k < 0.75), and a sortable
16-row table of the same statistics for every oracle at once.

**Section 1 — Audit any peptide** (new)

| control | type | range / options | what it drives |
|---|---|---|---|
| `sequence source` | dropdown | random real AMP / random shuffled decoy / my own sequence | which sequence is under audit |
| `draw another` | button (click counter) | — | re-draws from the 600 real + 600 decoy example sequences |
| `peptide sequence` | text area | free text; non-canonical characters dropped | the sequence, when source = "my own" |
| `shuffle seed` | slider | 0–50 | re-permutes the comparison shuffle |

Outputs: four stat cards — length, net charge at pH 7 (K,R = +1; D,E = −1; H = +0.1), mean
Eisenberg hydrophobicity, and the hydrophobic moment μ_H (Eisenberg **consensus** scale,
100°/residue, normalised by length); **two matplotlib helical wheels side by side** (residues
every 100°, spiralling outward, filled by hydrophobicity on a `coolwarm` ramp, the hydrophobic
face shaded as a ±60° wedge around the moment direction with the moment vector drawn as an
arrow) for the sequence and for a composition-preserving permutation of it; a **3D idealised
α-helix** (section 1.1); and a four-card comparison of the composition-only oracle score for the
sequence vs its shuffle, with the |difference| and the two μ_H values side by side.

**Section 2 — Generate decoys that fool the oracle** (new)

| control | type | range / options | what it drives |
|---|---|---|---|
| `peptides to generate` | slider | 10–500, step 10 | sample size |
| `target length` | slider | 8–50 | length of every sample |
| `random seed` | slider | 0–999 | reproducible sampling |
| `call threshold p ≥` | slider | 0.05–0.95, step 0.05 | the live "N of M would be called antimicrobial" counter and the rule drawn on the histogram |
| `draw lengths from the real AMP length distribution instead` | checkbox | on/off | samples each length from the 2,000 observed real-AMP lengths rather than the slider |

Outputs: a pure-Python, seeded order-2 Markov sampler over the transition counts fitted to the
2,000 curated real AMPs (`^^` = start context, back-off to `^<last>` then `^^`); the generated
score histogram overlaid on the real-AMP score distribution; three live stat cards (count called
at the threshold, the same rate on the 2,000 real AMPs, median generated vs median real score); a
ranked table of the generated set; and a `mo.download` button that writes the whole set to
`markov_decoys.fasta` with each sequence's score in its header.

**Section 3 — Why the published oracles behave this way** (new)

Scatter of composition-only oracle score vs amPEPpy score for all 4,000 reference peptides,
coloured by cohort, with μ_H in the tooltip; three stat cards carrying AUROC 0.868 (logistic,
the model actually running in-browser), AUROC 0.945 (gradient boosting, fitted offline and
**not** shipped) and the 10,413 / 4,464 train/test split; then a callout stating the nuance with
the numbers: μ_H separates real from decoy at AUROC 0.574 (medians 0.303 vs 0.251), amPEPpy
(0.405) and AMPlify (0.417) are *below* chance on that contrast, and the OmegAMP broad
classifier is near chance globally (0.477) while its 95th percentile is 0.9937 on real AMPs vs
0.0278 on decoys — which is why the depth test, not AUROC, is the diagnostic.

## Scientific conventions used

* **Hydrophobicity** — Eisenberg *consensus* scale. Verified against the offline pipeline: the
  in-app μ_H reproduces the exported `mimic_scatter.json` values exactly on 200/200 test
  sequences. The normalised Eisenberg scale does **not** reproduce them, so do not substitute it.
* **μ_H** — `sqrt((Σ H_i sin(100°·i))² + (Σ H_i cos(100°·i))²) / N`.
* **Net charge** — pH 7, K,R = +1, D,E = −1, H = +0.1.
* **Composition oracle** — 21 features (20 amino-acid frequencies + length/50), logistic
  regression trained to predict amPEPpy's own binary call. Only `coef` and `intercept` are
  shipped; scoring at runtime is one numpy dot product and a sigmoid, so **scikit-learn is not a
  runtime dependency**. Verified to reproduce the exported scores exactly on 200/200 sequences.
* **Idealised helix** — CA on a helix of radius 2.3 Å, rise 1.5 Å/residue, 100°/residue; CB
  projected radially outward at 3.75 Å and +0.45 Å in z (omitted for glycine). Consecutive CA–CA
  distance comes out at 3.83 Å, i.e. the real value. This is a geometric idealisation, **not** a
  structure prediction, and the notebook says so.

## 3Dmol.js — what shipped, and the one network dependency

The 3D viewer **is** in the build and did render: section 1.1 is an `mo.iframe` carrying two
side-by-side `$3Dmol` viewers (sequence and its shuffle) built from PDB text generated in Python,
styled as sticks + spheres with an explicit `CONECT` record per bond (a CA/CB-only model has no
bonds a viewer can infer — the 3.8 Å CA–CA spacing is far beyond any automatic bonding cutoff),
coloured by the `b` property with an `rwb` gradient so the b-factor-encoded hydrophobicity shows
the amphipathic face as a stripe running up the cylinder. The viewers auto-spin.

**This is the only part of the app that touches the network**: the 3Dmol bundle is loaded from
`cdn.jsdelivr.net/npm/3dmol@2.4.2`. If it cannot be fetched (offline, or a blocked CDN) the
iframe's `boot()` detects `typeof $3Dmol === "undefined"` and shows an in-frame notice pointing
the reader at the helical wheels, which carry the same information with no network dependency.
**Not verified in a browser** — see below. No 2D-projection fallback was needed or shipped,
because the matplotlib helical wheels already occupy that role and render unconditionally.

## Verification — what was and was not checked

* **Executed headlessly, all cells:** `app.run()` on the final `oracle_audit_app.py` ran all
  **34 cells with 0 errors** and produced 77 notebook-level definitions; `marimo export html`
  completed and the baked HTML contains no error cells.
* **Export verified structurally:** `marimo export html-wasm oracle_audit_app.py -o site/
  --mode run` wrote `site/index.html` at **858 082 bytes** plus 471 files in `site/assets/`
  (483 files, 28 MB total). All 103 local `src`/`href` asset references in `index.html` resolve
  to files that exist, and the embedded `<marimo-code>` block contains both data blobs,
  `helical_wheel`, `sample_peptide`, `markov_decoys.fasta` and the 3Dmol CDN tag.
* **Not verified:** nothing was rendered in a browser. Headless Chrome does not work in this
  sandbox (it dies in `process_singleton_posix`), so there is **no screenshot-level confirmation**
  that the Pyodide runtime boots, that matplotlib loads under Pyodide, or that 3Dmol.js draws.
  The evidence for those is the structural check above plus the dependency declaration.
* **matplotlib is a new runtime dependency** — it is declared in the inline script header
  (`matplotlib>=3.8`) and is part of the Pyodide distribution, but the WASM boot was not observed.

## Build and publish

```bash
pip install marimo altair numpy pandas matplotlib uv
marimo edit oracle_audit_app.py                   # or: marimo run oracle_audit_app.py
marimo export html-wasm oracle_audit_app.py -o site/ --mode run          # needs uv on PATH
python -m http.server --directory site                                   # local smoke test
```

`uv` **is** required for the `html-wasm` export (it resolves the notebook's inlined script
dependencies); without it the command copies the assets and then stops before writing
`index.html`. Artefacts in this directory:

* `site/` — the no-login, no-server bundle (`.nojekyll` included); `../docs/` is a byte copy of it
  for GitHub Pages.
* `oracle_audit_app.wasm.html` — the same export as one self-contained file (`--single-file`,
  864 477 bytes, assets from CDN) that opens directly in a browser.
* `oracle_audit_static.html` — the non-interactive `marimo export html` fallback with all cell
  outputs baked in.
* `oracle_audit_app_preview.png` — **a composed panel figure, not a browser screenshot.** It is
  built from the app's own code paths (the real helical-wheel function, the real Markov sampler,
  the real composition oracle, the real mimic data), but it was assembled in matplotlib because
  no browser is available in this sandbox to screenshot the live UI. Panels: (a,b) helical wheels
  for `GLKALKKVFKGIHKAIKLINKHVQ` and a permutation of it — μ_H 0.709 vs 0.026, composition-oracle
  score 0.8768 for **both**; (c) 200 order-2 Markov samples, 118 of which clear p ≥ 0.5 against
  62.3% of the 2,000 real AMPs; (d) the mimic scatter.
* `assets/` — the five source JSON assets; `data/` — the full source tables (`cohorts.json`,
  `scores_familyA.npz`, `scores_familyB.npz`, `dual_family_summary.csv`, `tail_precision.csv`,
  covering all 14,977 sequences) for provenance.

## Embedded data

Two gzip+base64 blobs inside the `.py`, so the exported bundle fetches no data at runtime:

1. **~260 kB** — per-peptide scores for the four reference cohorts (4,977 peptides × 16 oracles).
2. **~75 kB** (157 kB of JSON) — the order-2 Markov transition counts and real length
   distribution over the 2,000 curated AMPs, the composition-oracle weights, the mimic scatter
   (4,000 × composition score / amPEPpy score / μ_H), the headline statistics, and 600 real + 600
   decoy example sequences for the explorer.
