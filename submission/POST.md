Our peptide generator could produce a million candidates. Choosing which ones deserved a lab test was the harder problem.

We were searching for **antimicrobial peptides (AMPs)**: short chains of amino acids that can kill microbes. Some disrupt bacterial membranes and work against bacteria resistant to existing antibiotics. We need more effective, safe candidates because [new antibacterial treatments are not keeping up with resistance](https://www.who.int/observatories/global-observatory-on-health-research-and-development/monitoring/antibacterial-products-in-clinical-development-for-priority-pathogens/).

AI helps explore possible sequences. But copying the ingredients and short patterns of known AMPs does not guarantee that a new peptide will work. Their order helps determine how the molecule interacts with a bacterium. A promising candidate also needs to spare human cells—[properties that ultimately require experimental testing](https://www.nature.com/articles/s41467-023-36994-z).

We cannot make and test a million peptides. So we use prediction models, called **oracles**, to choose a shortlist.

**A generator and its judge can make the same mistake.**

A scorer can rely heavily on amino-acid composition. A generator optimising that score can then produce convincing-looking candidates whose activity is still uncertain. Adding several similar judges can leave that blind spot intact.

That is why we built **Oracle Audit** for the OSI Hackathon: a toolkit for checking the scoring models before trusting them to choose experiments.

We released **14,977 sequences scored by 16 models**, reusable audit code, and an interactive browser app. You can:

- **Shuffle a peptide:** keep its ingredients, change their order, and see how its chemical arrangement changes.
- **Inspect the judge:** compare scores on AMP references and shuffle controls.
- **Choose a realistic shortlist size:** see whether a model still enriches AMP references when you select hundreds of candidates, rather than just its top 100.

Our initial comparison found that amPEPpy and AMPlify called more of the shuffle cohort positive than the AMP reference cohort. That motivates a closer test: these cohorts were sampled separately and have unresolved label conflicts, so a clean paired experiment comes next.

**Our proposal is to evaluate the generator and its judge together:** use shuffled controls, check training overlap, and measure performance at the depth you actually select. Then validate activity independently.

The aim is practical: help researchers spend their lab budget on candidates with stronger evidence behind them.

[Try the app](https://huggingface.co/spaces/avaliev/oracle-audit) · [Watch the demo](https://drive.google.com/file/d/1idgrumJqcUbqA8D8fI3JtMnAefjvvfh0/view?usp=sharing) · [Code](https://github.com/Rebell-Leader/oracle-audit) · [Data](https://huggingface.co/datasets/avaliev/oracle-audit-amp-scores)
