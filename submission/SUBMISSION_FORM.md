# OSI Hackathon 2026 — submission answers

> **Control-cohort correction:** The released known-AMP and shuffle cohorts were
> sampled from different source files. Only 87 of 2,000 amino-acid compositions
> overlap. The rates and depth curves below describe those separate cohorts;
> they do not isolate sequence order. A genuinely paired, rescored experiment
> is still needed. The explorer does construct an exact shuffle of each input.
> The AMP/non-AMP cohorts also share 45 exact sequences with conflicting labels.
> Training-source overlap is documented; exact checkpoint split overlap is unresolved.


**Project title:** Oracle Audit — checking the models that select antimicrobial peptides

**Bucket:** Hypothesis Generation and Evaluation

**Code:** https://github.com/Rebell-Leader/oracle-audit

**App:** https://huggingface.co/spaces/avaliev/oracle-audit

**Dataset:** https://huggingface.co/datasets/avaliev/oracle-audit-amp-scores

**Summary:** https://github.com/Rebell-Leader/oracle-audit/blob/main/ONE_PAGER.md

**Video:** https://drive.google.com/file/d/1idgrumJqcUbqA8D8fI3JtMnAefjvvfh0/view?usp=sharing (Google Drive, publicly viewable). In-repo copies: `media/oracle_audit_video_voice.mp4` (voiced) and `media/oracle_audit_video_revised.mp4` (2:30 silent).

**Direct MP4 (mirror):** https://raw.githubusercontent.com/Rebell-Leader/oracle-audit/main/media/oracle_audit_video_revised.mp4

The overview is silent; the voiceover script is provided in `VIDEO_SCRIPT.md`.

**Two-sentence summary.** We checked 16 peptide scoring models across 14,977
sequences and found that amPEPpy and AMPlify call a larger fraction of a separately
sampled shuffle cohort positive than the known-AMP cohort at a 0.5 threshold.
We release the scores, two reusable diagnostics and an interactive notebook to
inspect threshold behaviour and selection depth; shuffled controls are untested,
so the results do not establish biological inactivity or experimental hit rates.

**Sponsor tools used in the project.**

- **Valency Bond:** literature search; 30 relevant abstracts and five full texts
  checked for shuffled controls. See `lit/valency_claim.md` for scope and limits.
- **Marimo:** interactive notebook and browser export.
- **Hugging Face:** public app and dataset hosting.
- **Adaption:** exploratory fine-tuning run; no completed validation result included.

**Evidence limits.** Only 87/2,000 compositions overlap between the two reference
cohorts; 45 exact sequences also carry conflicting AMP/non-AMP cohort labels.
The controls occur in OmegAMP negative-data source pools, while exact checkpoint
training membership remains unverified. These are exploratory results, not a
paired experiment or an independent validation of OmegAMP generalisation.

The repository contains the revised materials and local app exports. The public
HF app and dataset have not been redeployed as part of this update.
