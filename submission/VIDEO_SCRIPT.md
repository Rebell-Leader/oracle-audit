# Oracle Audit — revised voiceover and edit plan

Target: about 2½ minutes at a calm pace. The app capture is silent, as requested
in RECORD_VIDEO.md. This script is ready for a human voiceover; the original MP4
contains a silent audio track and no recorded narration to transcribe.

## 0:00–0:20 — Question

“Peptide design tools can generate thousands of candidates. A scoring model helps
choose which ones to test. We asked a simple question: does that score respond to
sequence order, or mostly to the amino acids in the sequence?”

## 0:20–0:45 — Control and result

“We compared two thousand known antimicrobial peptides with a separate cohort of
two thousand shuffled-AMP sequences. These cohorts were sampled independently;
they are not matched pairs, so this comparison does not isolate sequence order. At a threshold of point
five, amPEPpy calls eighty-seven point five percent of shuffles positive, compared
with sixty-six point eight percent of known AMPs. AMPlify shows a similar gap.
The shuffled sequences have not been tested in a lab, so they are not proven negatives.”

## 0:45–1:05 — Depth

“We also ask what happens when you select more sequences. In a balanced pool of
known AMPs and separately sampled shuffle controls, amPEPpy has ninety-two percent known AMPs in its top hundred.
That fraction falls as selection goes deeper. The notebook lets you inspect the
whole curve, rather than relying on one number near the top.”

## 1:05–2:05 — Live notebook (use the 60-second capture)

“Here is the audit in the browser. First, load a known peptide and compare it with
its shuffle. The helical wheels show how residue order changes the hydrophobic
pattern around an ideal helix. The three-dimensional view is an illustration,
not a prediction of the folded structure.

“The composition-only surrogate gives both sequences the same score because it
receives the same features. This surrogate imitates amPEPpy calls; it is not the
original model.

“Now switch the scoring model. amPEPpy calls more shuffles positive. OmegAMP broad
shows the opposite contrast at this threshold, although it also misses most known
AMPs. Moving the threshold changes the call rates.

“The simple sampler generates more control sequences. These are scored by the
surrogate, so high scores do not show that the original model is fooled. Finally,
the depth curve shows the fraction of known AMPs as we select more candidates.”

## 2:05–2:30 — Scope and release

“We release scores for fourteen thousand nine hundred and seventy-seven sequences
from sixteen models, plus the notebook and reusable checks. The reference cohorts
are unpaired, forty-five sequences have conflicting cohort labels, and checkpoint
training overlap remains unresolved. Next, reconcile those labels and score exact
paired controls. Use independent activity data before trusting a score to choose
experiments.”

## Editing notes

Keep each chart readable. Use the new recording rather than the composed preview
image. Do not reuse the old figures: they reverse AMPredictor's direction and
contain superseded depth values. The revised overview is silent with readable
on-screen captions; add the voiceover above in the final audio edit if desired.
