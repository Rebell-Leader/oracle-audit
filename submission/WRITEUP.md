# Oracle Audit: checking peptide selection scores

> **Control-cohort correction:** The released known-AMP and shuffle cohorts were
> sampled from different source files. Only 87 of 2,000 amino-acid compositions
> overlap. The rates and depth curves below describe those separate cohorts;
> they do not isolate sequence order. A genuinely paired, rescored experiment
> is still needed. The explorer does construct an exact shuffle of each input.
> The AMP/non-AMP cohorts also share 45 exact sequences with conflicting labels.
> Training-source overlap is documented; exact checkpoint split overlap is unresolved.


Peptide generators can produce many sequences. Prediction models help choose
which ones to test, but a high prediction score is not evidence of activity.
We built a small audit to check what those selection scores respond to.

## Method

The released table contains 14,977 peptides from nine cohorts scored by 16 models.
Our main comparison uses 2,000 curated antimicrobial peptides (AMPs), 2,000
separately sampled shuffled-AMP sequences, and 877 curated non-AMPs.
Shuffling changes residue order while preserving composition and length. The
shuffled sequences have not been assayed and may retain activity.

Two diagnostics answer different questions. The threshold comparison, called the
“sign test” in the code, asks whether a larger fraction of shuffles than known
AMPs pass a chosen cutoff. It is descriptive, not a significance test. The depth
curve ranks the 4,000 AMP/shuffle sequences and reports the fraction of known AMPs
among the first k entries. We record the first depth at or after k=20 where this
fraction falls below 0.75, using seed-0 random tie breaking.

## Results

At score ≥0.5, amPEPpy calls 87.5% of shuffles and 66.8% of known AMPs positive;
AMPlify calls 87.6% and 65.8%. Their rates on curated non-AMPs are 77.8% and 79.8%.
OmegAMP broad gives 0.0%, 14.4% and 0.3% on those cohorts respectively. Its low
known-AMP rate limits what this threshold comparison alone establishes.

Precision@100 on the balanced AMP/shuffle pool is 0.92 for amPEPpy, 0.90 for
AMPlify and 1.00 for OmegAMP broad. Their first crossings below 0.75 occur at
k=267, 242 and 693. This shows why a shallow summary can miss differences deeper
in a ranked list. It does not translate directly to hit rates in a generated pool.

AMPredictor outputs predicted MIC, where lower is better. Using the correct
direction, its precision@100 is 0.79 and its first crossing is k=123. At MIC ≤16 µM,
48.8% of known AMPs and 50.5% of shuffles pass. Earlier probability-based
AMPredictor results and the claim that it never clears the floor were incorrect.

## Interactive demonstration

The marimo notebook recomputes rates and curves from stored model scores.
Its sequence explorer runs a separate composition-only logistic surrogate, trained
to imitate amPEPpy's calls. The stored held-out AUROC is 0.868; an offline gradient
boosting fit reports 0.945. Neither value measures biological accuracy, and the
full fitting procedure and split indices are not included for independent refitting.

A peptide and its shuffle receive the same surrogate score because the input
features are identical. Helical wheels and idealised 3D helices show how residue
order can change the hydrophobic pattern. These are illustrations, not folding
predictions. The Markov sampler generates new control sequences and scores them
with the surrogate, not the original amPEPpy model.

## Evidence limits

The 13 OmegAMP models are related broad, species and strain heads. They are not
13 independent replications. A threshold contrast does not prove a causal benefit
from hard-negative training. We have not audited training overlap or assayed the
shuffles, and the choice of cohort mixture and tie rule affects depth results.

The Valency-assisted literature survey screened 30 relevant abstracts and inspected
five full texts. No shuffled control was mentioned in those abstracts or found in
those five texts. That finding is limited to the checked records and text coverage.
It does not show that the entire field omitted the control, or that untested
third-party models share the failures observed here.

## Use and follow-up

Release the controls and selection-depth curve alongside a generator's results.
Check independent activity labels before recommending a model for screening.
The score table, CLI and notebook make those comparisons inspectable. The Adaption
fine-tuning run has since completed and did not produce a working oracle: best win
rate 0.528 against a 0.70 target, and on 400 never-uploaded held-out rows it sits at
chance (accuracy 0.488-0.500), collapsing to a single label, as does the base model.
It inherits the unpaired-cohort limitation, so it is not evidence that sequence order
is unlearnable. We do not present it as a demonstrated fix.
