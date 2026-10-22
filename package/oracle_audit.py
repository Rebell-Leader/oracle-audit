"""Oracle Audit: two benchmark-validity diagnostics for any in-silico sequence scorer.

Usage:
    from oracle_audit import sign_test, depth_test
    r = sign_test(pos_scores, decoy_scores, nonneg_scores, threshold=0.5)   # sign inversion?
    d = depth_test(pos_scores, decoy_scores, precision_floor=0.75)          # how deep is it usable?
    # CLI: python oracle_audit.py --scores oracle_audit_scores_wide.csv --oracle ampeppy
    #      python oracle_audit.py --scores oracle_audit_scores_wide.csv --all

Rationale
---------
Compare positive-call rates at a chosen threshold and known-positive enrichment
as selection depth grows. These diagnostics do not establish biological activity.
Use composition-matched controls to isolate sequence order; the CLI checks their
composition multisets when sequences are supplied.
"""
from __future__ import annotations
import argparse
from collections import Counter
import numpy as np

DEFAULT_THRESHOLD = 0.5
DEFAULT_FLOOR = 0.75


def composition_overlap(pos_sequences, decoy_sequences):
    """Count matching amino-acid compositions, respecting duplicate counts."""
    pos = Counter("".join(sorted(s)) for s in pos_sequences)
    dec = Counter("".join(sorted(s)) for s in decoy_sequences)
    return sum((pos & dec).values())


def _scores(values):
    s = np.asarray(values, dtype=float)
    if s.ndim != 1 or not s.size or not np.isfinite(s).all():
        raise ValueError("scores must be a nonempty, finite, one-dimensional array")
    return s


def positive_rate(scores, threshold=DEFAULT_THRESHOLD, *, lower_is_better=False) -> float:
    s = _scores(scores)
    if not np.isfinite(threshold):
        raise ValueError("threshold must be finite")
    return float((s <= threshold if lower_is_better else s >= threshold).mean())


def sign_test(pos_scores, decoy_scores, nonneg_scores=None, threshold=DEFAULT_THRESHOLD,
              *, lower_is_better=False) -> dict:
    """Does the oracle flag composition-preserving decoys more often than real positives?

    pos_scores     : scores for curated real positives (e.g. real AMPs)
    decoy_scores   : scores for composition-preserving shuffles of those positives
    nonneg_scores  : optional curated true-negative cohort
    Returns positive rates, signed gap (decoy_rate - pos_rate) and `sign_inverted`.
    A positive gap means more decoys pass this threshold. This is a threshold
    diagnostic, not a test of the full ranking or statistical significance.
    """
    pos = positive_rate(pos_scores, threshold, lower_is_better=lower_is_better)
    dec = positive_rate(decoy_scores, threshold, lower_is_better=lower_is_better)
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
        non = positive_rate(nonneg_scores, threshold, lower_is_better=lower_is_better)
        out.update(n_nonneg=int(len(nonneg_scores)), nonneg_rate=non,
                   nonneg_gap=non - pos, sign_inverted_vs_nonneg=bool(non > pos))
    return out


def depth_test(pos_scores, neg_scores, precision_floor=DEFAULT_FLOOR, *,
               lower_is_better=False, min_k=20) -> dict:
    """Precision as a function of selection depth k in a pooled screen.

    Pools positives and negatives, ranks by score descending (ties broken by a
    fixed permutation so the result is deterministic), and reports
    precision@k for every k. `k_first_below` is the first failing depth at or
    after min_k; `k_at_floor` is its preceding depth (0 if min_k already fails).
    The curve can recover after a crossing; this is not a maximum over the curve.
    """
    pos = _scores(pos_scores)
    neg = _scores(neg_scores)
    if not 0 < precision_floor <= 1:
        raise ValueError("precision_floor must be in (0, 1]")
    if not isinstance(min_k, (int, np.integer)) or not 1 <= min_k <= len(pos) + len(neg):
        raise ValueError("min_k must be an integer within the pool")
    scores = np.concatenate([pos, neg])
    labels = np.concatenate([np.ones(len(pos), int), np.zeros(len(neg), int)])
    rng = np.random.default_rng(0)
    jitter = rng.permutation(len(scores))              # deterministic tie-break
    order = np.lexsort((jitter, scores if lower_is_better else -scores))
    hits = np.cumsum(labels[order])
    k = np.arange(1, len(scores) + 1)
    precision = hits / k
    below = np.flatnonzero((precision < precision_floor) & (k >= min_k))
    k_first_below = int(k[below[0]]) if below.size else None
    k_at_floor = (0 if k_first_below == min_k else k_first_below - 1) if below.size else len(scores)

    def at(kk):
        return float(precision[kk - 1]) if kk <= len(precision) else float("nan")

    return {
        "k": k, "precision": precision,
        "precision_floor": float(precision_floor),
        "k_at_floor": k_at_floor,
        "k_first_below": k_first_below, "min_k": min_k,
        "prec_at_100": at(100), "prec_at_500": at(500),
        "n_pool": int(len(scores)), "n_pos": int(len(pos)),
    }


# ---------------------------------------------------------------- CLI
def _load(path):
    import pandas as pd
    return pd.read_csv(path)


def _audit_one(df, oracle, pos_cohort, decoy_cohort, nonneg_cohort, threshold, floor, lower=False):
    g = {c: df.loc[df.cohort == c, oracle].to_numpy() for c in (pos_cohort, decoy_cohort, nonneg_cohort)}
    s = sign_test(g[pos_cohort], g[decoy_cohort], g[nonneg_cohort], threshold, lower_is_better=lower)
    d = depth_test(g[pos_cohort], g[decoy_cohort], floor, lower_is_better=lower)
    return {"oracle": oracle, **{k: v for k, v in s.items() if k != "threshold"},
            "threshold": threshold, "lower_is_better": lower,
            "k_at_floor": d["k_at_floor"], "k_first_below": d["k_first_below"],
            "prec@100": d["prec_at_100"], "prec@500": d["prec_at_500"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit an in-silico oracle for sign inversion and selection depth.")
    ap.add_argument("--scores", required=True, help="wide CSV: one row per sequence, one column per oracle")
    ap.add_argument("--oracle", help="oracle column to audit")
    ap.add_argument("--all", action="store_true", help="audit every oracle column, ranked by signed gap")
    ap.add_argument("--pos-cohort", default="ref_MarLys_AMPs")
    ap.add_argument("--decoy-cohort", default="ref_shuffled_decoys")
    ap.add_argument("--nonneg-cohort", default="ref_nonAMPs")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    ap.add_argument("--mic-cutoff", type=float, default=16.0, help="AMPredictor cutoff in uM (lower is better)")
    ap.add_argument("--lower-is-better", action="append", default=[], metavar="ORACLE",
                    help="additional lower-is-better column; uses --threshold")
    ap.add_argument("--precision-floor", type=float, default=DEFAULT_FLOOR)
    ap.add_argument("--require-paired", action="store_true",
                    help="reject controls unless composition multisets match the positives")
    a = ap.parse_args(argv)

    df = _load(a.scores)
    if "sequence" in df:
        pos_seqs = df.loc[df.cohort == a.pos_cohort, "sequence"]
        dec_seqs = df.loc[df.cohort == a.decoy_cohort, "sequence"]
        matched = composition_overlap(pos_seqs, dec_seqs)
        paired = matched == len(pos_seqs) == len(dec_seqs) and matched > 0
        if a.require_paired and not paired:
            ap.error(f"controls are not composition matched: {matched}/{len(pos_seqs)} positives")
        print(f"Composition overlap: {matched}/{len(pos_seqs)} positives; "
              + ("matched composition multisets" if paired else
                 "WARNING: unpaired cohorts; cannot isolate the effect of sequence order"))
    elif a.require_paired:
        ap.error("--require-paired needs a sequence column")
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

    rows = [_audit_one(df, o, a.pos_cohort, a.decoy_cohort, a.nonneg_cohort,
                       a.mic_cutoff if o == "ampredictor" else a.threshold, a.precision_floor,
                       o == "ampredictor" or o in a.lower_is_better)
            for o in targets]
    rows.sort(key=lambda r: -r["signed_gap"])

    hdr = f"{'oracle':<48} {'pos':>7} {'decoy':>7} {'nonAMP':>7} {'gap':>8} {'first<':>8} {'p@100':>6} {'p@500':>6}  verdict"
    print(f"Oracle audit | score >= {a.threshold} (AMPredictor MIC <= {a.mic_cutoff} uM) | precision floor {a.precision_floor}; min k=20")
    print(f"positives={a.pos_cohort}  decoys={a.decoy_cohort}  true-negatives={a.nonneg_cohort}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        verdict = "SIGN-INVERTED" if r["sign_inverted"] else ("shallow" if r["k_at_floor"] < 500 else "ok")
        print(f"{r['oracle']:<48} {r['pos_rate']:>7.3f} {r['decoy_rate']:>7.3f} {r['nonneg_rate']:>7.3f} "
              f"{r['signed_gap']:>+8.3f} {str(r['k_first_below']):>8} {r['prec@100']:>6.2f} {r['prec@500']:>6.2f}  {verdict}")
    print("\nSIGN-INVERTED = flags composition-preserving decoys more often than real positives.")
    return rows


if __name__ == "__main__":
    main()
