"""Compare released reference cohorts with the original source FASTA files.

Usage: python package/check_source_provenance.py /path/to/AMP_challenge
This checks source-pool membership, not exact checkpoint training membership.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path


def read_fasta(path):
    sequences, current = [], []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if current:
                sequences.append("".join(current))
                current = []
        else:
            current.append(line.strip())
    if current:
        sequences.append("".join(current))
    return sequences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_project", type=Path)
    parser.add_argument("--scores", type=Path,
                        default=Path(__file__).with_name("oracle_audit_scores_wide.csv"),
                        help="released audit score table (wide CSV)")
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("source_provenance.json"))
    args = parser.parse_args()
    base = args.source_project.resolve()
    table = args.scores
    with table.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    names = ["ref_MarLys_AMPs", "ref_shuffled_decoys", "ref_nonAMPs"]
    cohorts = {name: [r["sequence"] for r in rows if r["cohort"] == name] for name in names}
    files = {
        "amp_reference": "amp-challenge-2027/data/antibacterial.fasta",
        "omegamp_curated_positive": "OmegAMP/data/activity-data/curated-AMPs.fasta",
        "omegamp_shuffle_source": "OmegAMP/data/activity-data/synthetic-data/shuffled-AMP-sequences.fasta",
        "omegamp_curated_negative": "OmegAMP/data/activity-data/curated-Non-AMPs.fasta",
    }
    report = {"source_project": str(base), "source_files": {}, "cohorts": {}}
    source_sets = {}
    for name, relative in files.items():
        path = base / relative
        seqs = read_fasta(path)
        source_sets[name] = set(seqs)
        report["source_files"][name] = {
            "path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "records": len(seqs), "unique_sequences": len(set(seqs)),
        }
    for name, seqs in cohorts.items():
        report["cohorts"][name] = {
            "n": len(seqs), "exact_membership_in_source_pools": {
                key: sum(s in pool for s in seqs) for key, pool in source_sets.items()
            },
        }
    positives = cohorts["ref_MarLys_AMPs"]
    shuffles = cohorts["ref_shuffled_decoys"]
    counts = lambda seqs: Counter("".join(sorted(s)) for s in seqs)
    report["composition_multiset_overlap"] = sum((counts(positives) & counts(shuffles)).values())
    conflicts = sorted(set(positives) & set(cohorts["ref_nonAMPs"]))
    report["exact_overlap_between_reference_amp_and_nonamp_cohorts"] = len(conflicts)
    report["overlap_examples"] = conflicts[:5]
    report["limits"] = (
        "Source-pool membership does not prove membership in the exact checkpoint training split. "
        "Conflicting cohort labels require assay/strain/threshold reconciliation; file labels alone "
        "do not resolve biological activity."
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
