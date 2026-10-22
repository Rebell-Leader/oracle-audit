# Valency literature grounding — how generative-AMP papers evaluate their generators

**Source:** Valency Bond MCP connector (arXiv / PubMed / bioRxiv partitions of the Valency corpus), queried 2026-10-22.
All counts below are counts of papers *we actually screened*. Nothing is extrapolated to the field as a whole.

## Citable sentences

1. We screened **45** distinct Valency-corpus records (2019-2026) returned by eight semantic and four abstract-FTS queries on generative antimicrobial-peptide design, of which **30** both generate candidate peptide sequences and evaluate them in silico.
2. Of those 30 generative papers, only **2** name any in-silico evaluation oracle in the abstract and **2** indicate two or more independent classifier families; the remaining **28** (93%) do not state their evaluation oracle in the abstract at all — we record this as "not stated in abstract" rather than guessing.
3. **0 of 30** abstracts mention any negative or decoy control for the in-silico evaluation, and **none** mentions a composition-preserving shuffled- or scrambled-sequence control.
4. For the **5** most-cited generative papers in the set we retrieved full text (one further paper, Multi-CGAN, was closed-access and could not be checked): **5/5** score their candidates with their own internal classifier or discriminator, **2/5** additionally apply published third-party oracles (HydrAMP: AMPlify, CAMPR3-rf, STM; AMP-Designer: CAMP, AMP Scanner, Macrel) — all of which are conventionally-trained AMP classifiers, i.e. the same oracle family our audit shows ranks shuffled decoys above real AMPs — and **0/5** apply a composition-preserving shuffled/scrambled-sequence control.

**Interpretation for the audit:** "more than one oracle" is not the same as "more than one oracle family". In the five full texts we checked, every published oracle applied belongs to a single methodological family (conventionally-trained AMP classifiers trained against generic non-AMP negatives); no paper we screened reports the composition-preserving shuffled-decoy contrast on which the two oracle families in our audit disagree in sign.

## Evidence limits (read before quoting)

- Screening of the 30 generative papers is **abstract-level** except for the 5 papers where full text was retrieved; abstract-level "oracle not named" means *not stated*, not *not used*.
- Oracle-use calls in the full-text rows were made from methods-section context windows, excluding tools that appear only as related-work citations.
- The corpus is the Valency corpus (arXiv/PubMed/bioRxiv partitions), not all of the literature; recall is query-limited.
- 15 of the 45 screened records were retained in the CSV but fall outside the generative+in-silico core set (reviews, pure predictors, benchmarks).

## Five most relevant papers (Valency IDs for citation)

| Valency ID | Year | Paper | DOI | Oracles applied (full text) | Shuffled-decoy control |
|---|---|---|---|---|---|
| `36922490` | 2023 | Discovering highly potent antimicrobial peptides with deep generative model HydrAMP | 10.1038/s41467-023-36994-z | AMPlify; CAMPR3-rf; STM | no |
| `40043127` | 2025 | Discovery of antimicrobial peptides with notable antibacterial potency by an LLM-based foundation model | 10.1126/sciadv.ads8932 | CAMP; AMP Scanner; Macrel | no |
| `39319609` | 2024 | ProT-Diff: A Modularized and Efficient Strategy for De Novo Generation of Antimicrobial Peptide Sequences by Integrating Protein Language and Diffusion Models | 10.1002/advs.202406305 | AMP classifier (own MLP); MIC predictor (own MLP) | no |
| `36618982` | 2022 | Application of a deep generative model produces novel and diverse functional peptides against microbial resistance | 10.1016/j.csbj.2022.12.029 | QSAR random forest; QSAR support vector machine | no |
| `40447738` | 2025 | AMPGen: an evolutionary information-reserved and diffusion-driven generative model for de novo design of antimicrobial peptides | 10.1038/s42003-025-08282-7 | XGBoost-based discriminator; LSTM-based scorer | no |

## Sponsor-track note (Valency Bond methods called)

This survey was built entirely through the Valency Bond MCP connector, calling `semantic_search_papers` (8 queries, 25 results each) and `search_by_abstract` (4 queries, 25 results each) to assemble 221 distinct corpus records, with paper IDs, DOIs, citation counts and abstracts taken from the returned records; full text for the five highest-cited generative papers was then retrieved by DOI for methods-level verification.
