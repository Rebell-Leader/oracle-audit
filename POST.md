We built Oracle Audit to check the models used to select antimicrobial peptides.

> **Control-cohort correction:** The released known-AMP and shuffle cohorts were
> sampled from different source files. Only 87 of 2,000 amino-acid compositions
> overlap. The rates and depth curves below describe those separate cohorts;
> they do not isolate sequence order. A genuinely paired, rescored experiment
> is still needed. The explorer does construct an exact shuffle of each input.
> The AMP/non-AMP cohorts also share 45 exact sequences with conflicting labels.
> Training-source overlap is documented; exact checkpoint split overlap is unresolved.


Compare 2,000 known AMPs with 2,000 separately sampled shuffled-AMP sequences.
At a score threshold of 0.5, amPEPpy calls 87.5% of shuffles positive versus 66.8% of
known AMPs. AMPlify shows a similar gap. The shuffles are untested controls, not
confirmed inactive peptides, but the contrast raises a useful question about
what these scores reward.

A second check plots the fraction of known AMPs as we select more sequences from
a ranked AMP/shuffle pool. Models that look similar near the top can differ deeper
in the list.

For the OSI Hackathon we released 14,977 peptides × 16 model scores, reusable
diagnostics, and a browser notebook with a sequence explorer and control sampler.
The explorer uses a composition-only surrogate; its scores do not establish activity.

[Code](https://github.com/Rebell-Leader/oracle-audit) ·
[Data](https://huggingface.co/datasets/avaliev/oracle-audit-amp-scores) ·
[App](https://huggingface.co/spaces/avaliev/oracle-audit)
