# Record the Oracle Audit notebook

Deliver a **60-second silent app capture**, 1920×1080, 25 fps, H.264.
Narration is supplied separately in VIDEO_SCRIPT.md. A 2:30 overview combines
context and corrected charts with this capture.

## Source and setup

Record the corrected local WASM export, served at `http://127.0.0.1:8765/`.
The public HF app was checked, but has not been updated with these revisions.
Do not record its superseded scientific claims for the revised submission.

```bash
python -m http.server 8765 --bind 127.0.0.1 --directory app/site
uv run --with numpy --with pandas --with marimo==0.25.0 --with altair \
  --with matplotlib --with playwright python video/record_walkthrough.py
```

The script uses `/usr/bin/google-chrome` in headless mode. It requires Playwright's
FFmpeg helper (`playwright install ffmpeg`) and system `ffmpeg` for H.264 output.
It waits for Pyodide, controls and plots, then trims startup from the output.
Viewport and device scale remain fixed. A small pointer follows actual mouse
coordinates because headless Chrome does not capture an operating-system cursor.
No app values, chart contents or results are replaced for the recording.

## Shot plan

Times include scrolling and interactions; small timing shifts are recorded in
the capture manifest. The old shot list summed to 78 seconds despite specifying
a 45–60 second target; this version fits the requested one-minute capture.

| Approx. time | Action |
|---|---|
| 0–5 s | Hold the title and short explanation, including the cohort limitation. |
| 5–12 s | Scroll to the explorer; load a random real AMP; hold the wheels. |
| 12–17 s | Show the idealised 3D views and slowly drag the first helix. |
| 17–22 s | Return to the side-by-side helical wheels. |
| 22–26 s | Hold the identical composition-surrogate scores and feature comparison. |
| 26–35 s | Select amPEPpy, hold SIGN INVERTED; select OmegAMP broad, hold its rates. |
| 35–41 s | Drag the threshold down near 0.2, then back to 0.5; let rates recompute. |
| 41–49 s | Generate a few hundred sequences; hold the surrogate counter and histogram. |
| 49–55 s | Hold the full-width depth curve and 0.75 reference line. |
| 55–60 s | Scroll to provenance and stop. |

The shuffled reference cohort is separately sampled, not paired to the known-AMP
cohort. The explorer constructs an exact shuffle of the entered sequence. The
sampler uses a surrogate, not the original amPEPpy model. Keep those distinctions
in the narration and captions. The threshold slider changes rates, not the
full-pool ranking curve.

## Outputs and checks

- `media/oracle_audit_app_capture.mp4`: raw silent capture, no title cards or transitions.
- `oracle_audit_video_revised.mp4` (repo root): 2:30 silent overview with charts and live capture.
- `video/capture_manifest.json`: timings, source, viewport and browser errors.
- `video/capture_*.png`: checkpoints for visual review.
- `video/build_overview.py`: reproducible chart and overview assembly.

Check the encoded video with `ffprobe`, decode it with `ffmpeg`, and inspect
frames from the actual MP4 before delivery. A screenshot of the page alone does
not verify framing or timing in the encoded video.
