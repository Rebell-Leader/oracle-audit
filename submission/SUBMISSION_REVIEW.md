# Submission review and changes

Reviewed 22–23 October 2026. Scope: Python diagnostics, notebook, released scores,
submission copy, original video and the written voiceover script.

## Assessment

The useful contribution is an inspectable audit tool: compare model call rates
and follow known-positive enrichment as selection depth grows. The sequence
explorer gives a clear illustration of a composition-only model's limitation.
The original submission presented a stronger biological and causal conclusion
than its data support. The revised version presents the existing cohort results
as exploratory and states the experiment still needed.

## Findings that affect the conclusion

1. **The control cohorts are not paired.** Only 87 of 2,000 amino-acid composition
   signatures overlap between `ref_MarLys_AMPs` and `ref_shuffled_decoys`, counting
   multiplicity. The original cohort builder independently samples positives from
   `amp-challenge-2027/data/antibacterial.fasta` and shuffled sequences from
   `OmegAMP/data/activity-data/synthetic-data/shuffled-AMP-sequences.fasta`.
   Both model families see the same cohorts, but the cohorts are not matched to
   each other. Rates and depth curves therefore do not isolate sequence order.
   Added explicit notices and `--require-paired` to reject unmatched controls.

2. **AMPredictor's direction was reversed in the CLI and writeup.** It predicts
   MIC, not probability. Lower is better, consistent with the upstream
   [repository](https://github.com/ruihan-dong/AMPredictor) and
   [paper](https://elifesciences.org/articles/97330). The raw table reaches values
   above 1,000; using `score >= 0.5` does not measure AMP-positive probability.
   At MIC ≤16 µM, 48.8% of known AMPs, 50.5% of the shuffle cohort and 20.9% of
   curated non-AMPs pass. Corrected ranking: precision@100 0.79; first below 0.75
   from k=20 is 123. Withdrawn the saturation and “never clears the floor” claims.

3. **Depth definitions disagreed.** The CLI subtracted one from a zero-based
   array index, producing values two below the first failing depth. It checked
   from k=1; the app checked from k=20. The app also used stable ties, while the
   CLI used seed-0 random ties. Both now rank positives followed by controls,
   break ties with the same seed-0 permutation and check from k=20. The return
   values distinguish the first failing depth and its preceding depth. A curve
   may recover after that first crossing.

4. **The notebook rounded its stored scores.** That introduced ties absent from
   the CSV and changed rankings, particularly at the numerical floor. Replaced
   the score blob with exact CSV values. All 16 full curves now match the CLI.

5. **The sampler was described as running the published oracle.** It runs a
   logistic surrogate trained to imitate amPEPpy calls. Identical peptide/shuffle
   scores are guaranteed by those composition-only inputs; they are not evidence
   that amPEPpy gives identical scores. Relabelled the demo and script.

6. **The literature and biological claims were too broad.** Thirty abstracts and
   five full texts cannot establish that nobody in the field uses shuffled
   controls. Untested shuffles are not confirmed inactive peptides; related
   OmegAMP heads are not independent replications. Removed claims about peer
   review failure, universal model-family superiority and untested classifiers.

## Recomputed reference results

| Model | Known-AMP pass rate | Shuffle-cohort pass rate | Precision@100 | First k below 0.75 from k=20 |
|---|---:|---:|---:|---:|
| amPEPpy, score ≥0.5 | 66.75% | 87.50% | 0.92 | 267 |
| AMPlify, score ≥0.5 | 65.75% | 87.55% | 0.90 | 242 |
| OmegAMP broad, score ≥0.5 | 14.35% | 0.00% | 1.00 | 693 |
| AMPredictor, MIC ≤16 µM | 48.80% | 50.50% | 0.79 | 123 |

These numbers describe the supplied cohorts and original model outputs. They are
not an independent re-run of checkpoint inference or estimates of experimental
hit rate. Precision here treats the known-AMP cohort as positives and the shuffle
cohort as controls for bookkeeping, without establishing negative activity labels.

## Copy and video

Rewrote the README, one-pager, submission form, writeup, post, notebook copy,
data cards and voiceover script around concrete actions and measured results.
Removed rhetoric such as “the scientific heart,” “the money shot,” “the sign is
inverted” as a claim about the full ranking, and “why nobody caught it.” The UI
retains SIGN INVERTED as a defined threshold-rate label used in the requested
recording instructions.

The original MP4 is 3:43.96 at 1920×1080, 25 fps. Its audio is silent (mean/max
volume about −91 dB); there is no spoken recording to transcribe. Reviewed its
visuals with extracted frames. It uses static panels, small charts and captions
that clip at the frame edge. Its main figure also includes the AMPredictor error.
The old video is retained as an archive and is superseded by the revised output.

The new recording uses actual headless Google Chrome, the corrected local WASM
export, a 1920×1080 viewport and visible pointer. It waits for the notebook before
starting the usable footage. The raw MP4 is silent, as RECORD_VIDEO.md requests.
The revised overview adds readable charts and context around that capture. Its
voiceover remains a separate human-readable script; no artificial voice is used.
The public HF deployment was opened and booted, but was not modified.

## Verification and remaining work

Eight regression tests cover lower-is-better scoring, depth boundary cases,
minimum depth, deterministic ties, composition multiset counts and invalid inputs.
`video/verify_analysis.py` executes all 34 notebook cells, checks the table shape
and missing values, records composition overlap and compares all 16 full curves
against the CLI. Recording metadata and browser errors are in
`video/capture_manifest.json`.

Before making the original composition-control claim, generate exact shuffles of
the selected 2,000 known AMPs and score them with the original checkpoints, saving
parent IDs, seeds and checkpoint hashes. No new wet-lab or model inference result
is fabricated here. Training overlap, uncertainty estimates, surrogate fitting
reproducibility and independent activity validation remain open.

## Provenance inspected outside this checkout

Read-only source: `/home/obi/AMP_challenge/build_cohorts.py`.
SHA-256: `1d47fabf9fe4436c3d7097a4ca81f2df33e59dec6f81842c0571a5ee01cb5920`.
The composition mismatch can be reproduced from this repository alone; this
external source explains the independent sampling that produced it.


## Source-project follow-up (23 October)

Inspected `/home/obi/AMP_challenge`, including `build_cohorts.py`, `gen_pools.py`,
both score runners, the AMPredictor wrapper and OmegAMP's synthetic-data and
classifier dataset builders. The source confirms the independent cohort sampling
identified above. Additional source checks are saved in
`package/source_provenance.json`; regenerate them with:

```bash
python package/check_source_provenance.py /path/to/AMP_challenge
```

### Reference labels and source-pool overlap

- **45 exact sequences occur in both released reference AMP and non-AMP cohorts.**
  The sequence alone therefore cannot determine both cohort labels consistently.
  Reconcile assay, strain, concentration and activity definitions before treating
  these cohorts as clean biological positives and negatives.
- **861 of the 877 non-AMP references also occur in the full 39,448-sequence
  antibacterial reference FASTA.** This is a source-label conflict, not proof
  that either biological annotation is necessarily wrong. The files do not carry
  enough harmonised assay evidence to settle it here.
- **All 2,000 shuffle controls and all 877 non-AMP references occur in OmegAMP
  negative-data source pools.** Its dataset builder includes those source files,
  labels them negative, then removes positive/negative overlaps. The released
  AMP cohort also contains 197 sequences from OmegAMP's curated-positive pool.
  Exact fitted checkpoint training membership is not established by source-pool
  membership alone. The comparison must not be described as a demonstrated
  generalisation advantage without auditing checkpoint splits.
- OmegAMP's own classifier evaluation code explicitly generates shuffled controls.
  This is further reason to avoid a broad statement that nobody checks shuffles.

### What the sampler source establishes

`gen_pools.py` implements five sampling modes: an order-3 Markov sampler,
unconditional and targeted OmegAMP diffusion, ProtGPT2, and an ESM-2 masked
resampling procedure. These are different procedures, not five independent
activity validations. The target is 5,000 canonical 8–50-residue unique outputs
per mode; the cohort builder then samples up to 2,000 per pool.

The ESM-2 procedure starts from the same antibacterial reference FASTA, performs
six sweeps masking about 25% of positions, and excludes exact copies of seeds
in the current batch. That does not establish exclusion of the full reference
library or sequence-family independence. ProtGPT2 outputs are cleaned to canonical
residues and length filtered. Generator novelty, reference overlap and similarity
need explicit measurements rather than an assumption that generated means novel.

The audit's interactive order-2 sampler remains a separate demonstration from the
order-3 sampler used for the released generator cohort.

The AMPredictor wrapper explicitly back-transforms log10 MIC with `10**x` and
returns MIC in µM. This independently confirms the scoring-direction correction
made during the first review.

### Required before stronger claims

Create exact shuffles with parent IDs and seeds; harmonise positive/negative
activity labels; remove conflicting and training-overlapping sequences according
to an explicit protocol; then rescore with pinned checkpoints. The source project
was inspected read-only. No sampling, retraining or model inference was launched,
and no new model experiment was run. The raw capture predates these additional
findings; the revised overview closing screen and voiceover now disclose them.
