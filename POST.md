Generative antimicrobial-peptide design is scored by in-silico oracles — published classifiers standing in for a wet-lab assay.

So we ran the simplest check there is. Take 2,000 real curated AMPs. Shuffle each one: same amino acids, order destroyed. Ask the oracles which set looks antimicrobial.

amPEPpy flags 87.5% of the shuffles and 66.8% of the real peptides. AMPlify: 87.6% vs 65.8%. They rank the decoys ABOVE the real thing.

It isn't classifiers in general — hard-negative-trained classifiers order the same cohorts correctly (0.0% decoys / 14.4% real AMPs). Across 16 oracles: 3/3 published oracles sign-inverted, 13/13 hard-negative oracles fine.

Why nobody caught it: at precision@100 — the depth these papers report — everything looks fine. The families only diverge deeper, where real campaigns actually select: precision breaks at k=265 and k=240 vs k=691. One pipeline we examined took the top 50,000 of 998,452 candidates ranked by two of the inverted oracles.

And the field doesn't run the check: of 30 generative-AMP papers screened via Valency Bond, 0 report a composition-preserving decoy control.

Oracle Audit, built for the Open Scientific Intelligence Hackathon 2026:
- sign test + depth test, runnable against any scorer
- 14,977 peptides x 16 oracles released with a data card
- an interactive audit that recomputes the verdict live in your browser

Code: https://github.com/Rebell-Leader/oracle-audit
Data: https://huggingface.co/datasets/avaliev/oracle-audit-amp-scores
Live app: https://huggingface.co/spaces/avaliev/oracle-audit

#MachineLearning #ProteinDesign #AMP #OpenScience
