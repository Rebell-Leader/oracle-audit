# OSI Hackathon 2026 — submission form answers

**Project title:** Oracle Audit — the benchmark that scores shuffled decoys above real antimicrobial peptides
**Bucket:** Hypothesis Generation and Evaluation
**Code:** https://github.com/Rebell-Leader/oracle-audit
**Live interactive app (no login):** http://sciway.me/oracle-audit/
**Dataset:** https://huggingface.co/datasets/avaliev/oracle-audit-amp-scores
**One-page summary:** https://github.com/Rebell-Leader/oracle-audit/blob/main/ONE_PAGER.md
**Video:** (post publicly, paste link here)

**Two-sentence summary.** In-silico AMP classifiers are the de-facto scoring function for generative
peptide design; we audited 16 of them over 14,977 peptides and found the three most widely used ones
rank composition-preserving shuffled decoys *above* real curated AMPs (87.5% vs 66.8% at p>=0.5), while
hard-negative-trained classifiers order the same cohorts correctly. We release the two diagnostics that
expose this (a sign test and a selection-depth test, runnable against any scorer), the full score
dataset, and an interactive marimo notebook that recomputes the verdict live.

**Sponsor tracks used.**
- **Valency (Bond MCP):** literature grounding — `semantic_search_papers` (8 queries) and
  `search_by_abstract` (4 queries) over 221 corpus records; 45 screened, 30 generative+in-silico, 0 of
  30 reporting a composition-preserving decoy control. Table: `lit/oracle_practice_survey.csv`.
- **Marimo:** the interactive audit notebook, exported to WASM and served with no login or server.
- **Hugging Face:** the audit dataset released as a public dataset with a data card.
