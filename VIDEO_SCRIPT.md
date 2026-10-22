# Oracle Audit — video script (v2, matches oracle_audit_video.mp4, 3:44)

Silent cut; add voiceover on top. Beats below are the exact slide boundaries in the encoded file.
A browser-agent recording of the live app (see RECORD_VIDEO.md) can replace the 2:54-3:18 slide.

## 0:00-0:14 — Title
"Oracle Audit. Every generative model for antimicrobial peptides is scored by the same thing: a
published classifier standing in for a wet-lab assay. We asked a simple question about those classifiers."

## 0:14-0:46 — The shuffle test
"Take two thousand real, curated antimicrobial peptides. Now shuffle each one — same amino acids,
same composition, order destroyed. Those shuffles are not peptides anyone believes are active.
Then ask the field's standard oracles which set looks antimicrobial."

## 0:46-1:22 — The inversion
"amPEPpy calls 87.5 percent of the shuffles antimicrobial, and only 66.8 percent of the real peptides.
AMPlify agrees: 87.6 against 65.8. It also flags 78 percent of curated non-AMPs. The oracle ranks the
decoys above the real thing. The sign is inverted."

## 1:22-1:44 — Not universal
"This is not a statement about classifiers in general. On exactly the same three cohorts, OmegAMP's
hard-negative-trained classifier orders them correctly: zero percent of shuffles, nought-point-three
percent of non-AMPs, 14 percent of real AMPs. Across all sixteen oracles the split is clean — three of
three published oracles inverted, thirteen of thirteen hard-negative oracles correct."

## 1:44-2:24 — Selection depth
"Here is why this survived peer review. At precision-at-100 — the depth these papers report — the
oracles look comparable: nought-point-nine-two, nought-point-nine-oh, one-point-zero. They only diverge
deeper down the ranking, where real campaigns actually select. Precision falls below 0.75 at k equals
265 and 240 for the published oracles, against 691 for the hard-negative classifier. And AMPredictor
never clears the floor at all — it flags over ninety-nine percent of every cohort, real or shuffled.
One pipeline we examined took the top fifty thousand of nine hundred ninety-eight thousand candidates
ranked by two of these oracles."

## 2:24-2:54 — The mechanism
"Why does this happen? Shuffles preserve composition exactly, so an oracle that is really a composition
detector cannot see them. That is measurable: a twenty-one-feature model — amino-acid frequencies and
length — trained to predict amPEPpy's own call reproduces it at an AUROC of nought-point-nine-four-five.
Order does carry signal; the hydrophobic moment separates real from shuffled at nought-point-five-seven.
The published oracles sit below chance on it."

## 2:54-3:18 — What we built
"So we packaged the audit. A sign test and a depth test that run against any scorer. The interactive
version lets you paste a peptide and see its helical wheel and 3D amphipathic face beside its shuffle:
hydrophobic moment nought-point-seven-one versus nought-point-zero-three, and the composition oracle
gives both the identical score of nought-point-eight-eight. There is a Markov decoy generator built in —
a trivial order-two chain produces peptides the oracle calls antimicrobial at nearly the real-AMP rate."

## 3:18-end — Close
"The dataset — fourteen thousand nine hundred seventy-seven peptides by sixteen oracles — is released
with a data card. Our recommendation to benchmark designers: filter deep with hard-negative-trained
classifiers, use the published oracles only as a shallow final re-rank, and always hold out one oracle
from each family as a cross-family control. Thanks for watching."

## Valency line (drop in anywhere, 8 s)
"We surveyed the literature through Valency Bond: of thirty screened papers that generate and score AMPs
in silico, zero report any composition-preserving decoy control."
