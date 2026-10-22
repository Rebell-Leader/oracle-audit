# Oracle Audit — 4-minute video script
(Target 3:40 spoken. Plain delivery, no speed-up. Screen = figure, then the live marimo app.)

## 0:00-0:35 — The hook  [slide: Panel A of the figure]
"Every generative model for antimicrobial peptides is scored by the same thing: a published
classifier standing in for a wet-lab assay. We asked a simple question about those classifiers.
Take two thousand real, curated antimicrobial peptides. Now shuffle each one — same amino acids,
same composition, order destroyed. Those shuffles are not peptides anyone believes are active.
Then ask the field's standard oracles which set looks antimicrobial.
amPEPpy calls 87 percent of the shuffles antimicrobial, and only 67 percent of the real peptides.
AMPlify agrees: 88 against 66. The oracle ranks the decoys above the real thing. The sign is inverted."

## 0:35-1:20 — It is not universal  [same panel, point to Family A bars]
"This is not a statement about classifiers in general. On exactly the same three cohorts, OmegAMP's
hard-negative-trained classifier orders them correctly: zero percent of shuffles, nought-point-three
percent of curated non-AMPs, 14 percent of real AMPs. Two families of oracle, same inputs, opposite
verdicts about what the benchmark is even measuring. And a useful control: ProtGPT2 samples are
rejected by both families, so Family B is not simply permissive — it is specifically blind to
composition-preserving shuffles."

## 1:20-2:10 — Why nobody caught it  [slide: Panel B, depth curve]
"Here is why this survived peer review. Screen real AMPs out of a fifty-fifty pool against shuffled
decoys and every oracle gets precision-at-100 of exactly one-point-zero. Precision-at-100 is the
metric these papers report. The families only diverge deeper down the ranking. Precision falls below
0.75 at k equals 125 for AMPredictor, 342 for amPEPpy — but 729 for the hard-negative classifier.
Roughly a six-fold difference in usable selection depth, entirely invisible at the depth everyone
reports."

## 2:10-2:50 — Why it matters now  [slide: the 50,000-of-998,452 number]
"Real campaigns do not stop at a hundred. A submission pipeline we examined took the top fifty
thousand from a pool of nine hundred ninety-eight thousand, ranked by two Family-B oracles averaged
together — a depth where those oracles are near chance on the decoy contrast. Generative-peptide
benchmarks are being built on this right now, and the leaderboard they produce may be ranking
composition matching rather than activity."
[If the Valency survey lands: "We surveyed the generative-AMP literature through Valency Bond — of N
papers that generate and score candidates, M report only a single oracle family and J report any
composition-preserving decoy control."]

## 2:50-3:40 — What we built  [screen: live marimo app]
"So we packaged the audit. Two diagnostics that run against any scorer: a sign test, and a depth test.
The dataset — 14,977 sequences scored by 16 oracles across nine cohorts — is released with a data card.
And this is the interactive version: pick any oracle, move the threshold, and the verdict and the
depth curve recompute live. It runs in the browser, no login, no server.
Our recommendation to benchmark designers is one line: filter deep with hard-negative-trained
classifiers, use the published oracles only as a shallow final re-rank, and always hold out one oracle
from each family as a cross-family control. Thanks for watching."
