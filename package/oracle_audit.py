"""Oracle Audit: two benchmark-validity diagnostics for any in-silico sequence scorer.

Usage:
    from oracle_audit import sign_test, depth_test
    r = sign_test(pos_scores, decoy_scores, nonneg_scores, threshold=0.5)   # sign inversion?
    d = depth_test(pos_scores, decoy_scores, precision_floor=0.75)          # how deep is it usable?
    # CLI: python oracle_audit.py --scores oracle_audit_scores_wide.csv --oracle ampeppy
    #      python oracle_audit.py --scores oracle_audit_scores_wide.csv --all

Rationale
---------
An oracle used to *rank* generated sequences is valid only if (a) it scores real
positives above composition-matched decoys (sign test) and (b) it keeps doing so
at the selection depth the pipeline actually uses (depth test). Published
precision@100 can be 1.00 for an oracle that is at chance by k=300.
"""
from __future__ import annotations
import argparse
import numpy as np

DEFAULT_THRESHOLD = 0.5
DEFAULT_FLOOR = 0.75


def positive_rate(scores, threshold=DEFAULT_THRESHOLD) -> float:
    s = np.asarray(scores, dtype=float)
    return float((s >= threshold).mean())


def sign_test(pos_scores, decoy_scores, nonneg_scores=None, threshold=DEFAULT_THRESHOLD) -> dict:
    """Does the oracle flag composition-preserving decoys more often than real positives?

    pos_scores     : scores for curated real positives (e.g. real AMPs)
    decoy_scores   : scores for composition-preserving shuffles of those positives
    nonneg_scores  : optional curated true-negative cohort
    Returns positive rates, signed gap (decoy_rate - pos_rate) and `sign_inverted`.
    A positive signed gap means the oracle ranks decoys ABOVE real positives:
    the benchmark contrast it is used for is inverted in sign.
    """
    pos = positive_rate(pos_scores, threshold)
    dec = positive_rate(decoy_scores, threshold)
    out = {
        "threshold": float(threshold),
        "n_pos": int(len(pos_scores)),
        "n_decoy": int(len(decoy_scores)),
        "pos_rate": pos,
        "decoy_rate": dec,
        "signed_gap": dec - pos,
        "sign_inverted": bool(dec > pos),
    }
    if nonneg_scores is not None:
        non = positive_rate(nonneg_scores, threshold)
        out.update(n_nonneg=int(len(nonneg_scores)), nonneg_rate=non,
                   nonneg_gap=non - pos, sign_inverted_vs_nonneg=bool(non > pos))
    return out


def depth_test(pos_scores, neg_scores, precision_floor=DEFAULT_FLOOR) -> dict:
    """Precision as a function of selection depth k in a pooled screen.

    Pools positives and negatives, ranks by score descending (ties broken by a
    fixed permutation so the result is deterministic), and reports
    precision@k for every k. `k_at_floor` is the deepest k that can be selected
    before precision first falls below `precision_floor` — the usable depth.
    """
    pos = np.asarray(pos_scores, dtype=float)
    neg = np.asarray(neg_scores, dtype=float)
    scores = np.concatenate([pos, neg])
    labels = np.concatenate([np.ones(len(pos), int), np.zeros(len(neg), int)])
    rng = np.random.default_rng(0)
    jitter = rng.permutation(len(scores))              # deterministic tie-break
    order = np.lexsort((jitter, -scores))
    hits = np.cumsum(labels[order])
    k = np.arange(1, len(scores) + 1)
    precision = hits / k
    below = np.flatnonzero(precision < precision_floor)
    k_at_floor = int(below[0] - 1) if below.size else int(len(scores))

    def at(kk):
        return float(precision[kk - 1]) if kk <= len(precision) else float("nan")

    return {
        "k": k, "precision": precision,
        "precision_floor": float(precision_floor),
        "k_at_floor": k_at_floor,
        "prec_at_100": at(100), "prec_at_500": at(500),
        "n_pool": int(len(scores)), "n_pos": int(len(pos)),
    }


# ---------------------------------------------------------------- CLI
def _load(path):
    import pandas as pd
    return pd.read_csv(path)


def _audit_one(df, oracle, pos_cohort, decoy_cohort, nonneg_cohort, threshold, floor):
    g = {c: df.loc[df.cohort == c, oracle].to_numpy() for c in (pos_cohort, decoy_cohort, nonneg_cohort)}
    s = sign_test(g[pos_cohort], g[decoy_cohort], g[nonneg_cohort], threshold)
    d = depth_test(g[pos_cohort], g[decoy_cohort], floor)
    return {"oracle": oracle, **{k: v for k, v in s.items() if k != "threshold"},
            "k_at_floor": d["k_at_floor"], "prec@100": d["prec_at_100"], "prec@500": d["prec_at_500"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit an in-silico oracle for sign inversion and selection depth.")
    ap.add_argument("--scores", required=True, help="wide CSV: one row per sequence, one column per oracle")
    ap.add_argument("--oracle", help="oracle column to audit")
    ap.add_argument("--all", action="store_true", help="audit every oracle column, ranked by signed gap")
    ap.add_argument("--pos-cohort", default="ref_MarLys_AMPs")
    ap.add_argument("--decoy-cohort", default="ref_shuffled_decoys")
    ap.add_argument("--nonneg-cohort", default="ref_nonAMPs")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    ap.add_argument("--precision-floor", type=float, default=DEFAULT_FLOOR)
    a = ap.parse_args(argv)

    df = _load(a.scores)
    meta = {"sequence_id", "cohort", "sequence", "length"}
    oracles = [c for c in df.columns if c not in meta]
    if a.all:
        targets = oracles
    elif a.oracle:
        if a.oracle not in oracles:
            ap.error(f"unknown oracle {a.oracle!r}; available: {', '.join(oracles)}")
        targets = [a.oracle]
    else:
        ap.error("pass --oracle NAME or --all")

    rows = [_audit_one(df, o, a.pos_cohort, a.decoy_cohort, a.nonneg_cohort, a.threshold, a.precision_floor)
            for o in targets]
    rows.sort(key=lambda r: -r["signed_gap"])

    hdr = f"{'oracle':<48} {'pos':>7} {'decoy':>7} {'nonAMP':>7} {'gap':>8} {'k@floor':>8} {'p@100':>6} {'p@500':>6}  verdict"
    print(f"Oracle audit  |  threshold p>={a.threshold}  |  precision floor {a.precision_floor}")
    print(f"positives={a.pos_cohort}  decoys={a.decoy_cohort}  true-negatives={a.nonneg_cohort}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        verdict = "SIGN-INVERTED" if r["sign_inverted"] else ("shallow" if r["k_at_floor"] < 500 else "ok")
        print(f"{r['oracle']:<48} {r['pos_rate']:>7.3f} {r['decoy_rate']:>7.3f} {r['nonneg_rate']:>7.3f} "
              f"{r['signed_gap']:>+8.3f} {r['k_at_floor']:>8d} {r['prec@100']:>6.2f} {r['prec@500']:>6.2f}  {verdict}")
    print("\nSIGN-INVERTED = flags composition-preserving decoys more often than real positives.")
    return rows


if __name__ == "__main__":
    main()
