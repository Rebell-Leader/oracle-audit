# Recording instructions for a browser agent

Goal: a screen recording of the live Oracle Audit app, to be cut into the submission video in place of
the static app screenshot. Target length **45-60 seconds**, no narration (voiceover is added later).

## Setup

- URL: **https://huggingface.co/spaces/avaliev/oracle-audit**
  (direct, no HF chrome: https://avaliev-oracle-audit.static.hf.space/)
- Viewport **1920x1080**, browser zoom 100%, cursor visible, no extensions/overlays.
- The app is a marimo WASM notebook: it boots Pyodide on load. **Wait until the first plot renders
  before starting the recording** (roughly 10-25 s). Do not record the loading spinner.
- Record at 25-30 fps to `oracle_audit_app_capture.mp4` (H.264).

## Shot list (hold each state still for the stated time — slow, deliberate moves)

1. **(5 s)** Top of the notebook: title and the intro paragraph. Scroll smoothly to the peptide explorer.
2. **(12 s)** *Audit any peptide*: click **load a random real AMP**. Let the helical wheel, the 3D helix
   and the metrics render. Hold 3 s. Then **rotate the 3D helix** with one slow drag (about 180 degrees)
   so the amphipathic face is visible. Hold 2 s.
3. **(10 s)** Still in the explorer: compare the sequence against its shuffle — hold on the two
   side-by-side helical wheels for 4 s (this is the money shot: identical composition, different face),
   then hold 3 s on the two composition-oracle scores showing they barely differ.
4. **(10 s)** *Oracle selector*: open the dropdown, select **ampeppy**. Hold on the verdict panel until
   "SIGN INVERTED" is clearly legible (3 s). Then switch to **broad-classifier** and hold on the
   corrected ordering (3 s).
5. **(8 s)** Drag the **threshold slider** from 0.5 down to ~0.2 and back, so the verdict and the cohort
   rates visibly recompute. Hold at the end state 2 s.
6. **(10 s)** *Generate decoys*: set n to a few hundred with the slider, let the Markov sampler run, and
   hold on the "N of M generated peptides would be called antimicrobial" counter and the histogram.
7. **(8 s)** *Depth curve*: hold on the precision-vs-k plot with the 0.75 floor line and the k markers.
8. **(5 s)** Scroll to the provenance footer and stop.

## Notes

- If the 3D viewer does not load, skip step 2's rotation and spend that time on the helical wheels instead.
- Mouse movement between shots should be slow; sudden jumps read badly at 1080p.
- Do not resize the window mid-recording (marimo re-lays-out and plots re-render).
- Deliver the raw capture; it will be cut into the submission video — no titles or transitions needed.
