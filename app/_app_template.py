# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "altair>=5.4",
#     "numpy>=1.26",
#     "pandas>=2.2",
#     "matplotlib>=3.8",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="Oracle Audit")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Oracle Audit

    ### Check a peptide scorer before using it to choose candidates.

    An antimicrobial peptide (AMP) is a short protein with measured antimicrobial
    activity. Design tools often use a model score to choose which new peptides
    to test. Here we check what those scores respond to.

    We compare **2,000 known AMPs**, **2,000 sequences from a separate shuffle cohort**,
    and **877 curated non-AMPs**. Shuffling preserves amino-acid composition and
    length for each source peptide, but these two cohorts are **not paired**.
    Only **87 of 2,000 compositions overlap**. Differences can reflect cohort
    composition as well as order. The shuffles have not been tested in a lab.

    At a score threshold of 0.5, amPEPpy calls **87.5% of shuffles** positive,
    compared with **66.8% of known AMPs**. AMPlify shows a similar gap.
    This raises a question about using these scores to select new sequences.

    /// tip | Try the audit
    Choose a scorer and threshold below. Then compare a peptide with its shuffle,
    inspect an idealised helix, or generate new sequences with a simple sampler.
    The explorer uses a **composition-only surrogate**, not the original amPEPpy
    model. Model scores and geometric views do not establish biological activity.
    ///
    """
    )
    return


@app.cell(hide_code=True)
def _():
    # --- Setup ------------------------------------------------------------------
    import base64
    import gzip
    import io
    import json
    import math
    import random

    import altair as alt
    import matplotlib
    import numpy as np
    import pandas as pd

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Wedge

    alt.data_transformers.enable("default", max_rows=20000)

    # Family A: OmegAMP's hard-negative-trained classifiers (broad + per-species + per-strain)
    FAMILY_A = [
        "broad-classifier",
        "species-acinetobacterbaumannii-classifier",
        "species-escherichiacoli-classifier",
        "species-klebsiellapneumoniae-classifier",
        "species-pseudomonasaeruginosa-classifier",
        "species-staphylococcusaureus-classifier",
        "strains-acinetobacterbaumanniiatcc19606-classifier",
        "strains-escherichiacoliatcc25922-classifier",
        "strains-klebsiellapneumoniaeatcc700603-classifier",
        "strains-pseudomonasaeruginosaatcc27853-classifier",
        "strains-staphylococcusaureusatcc25923-classifier",
        "strains-staphylococcusaureusatcc33591-classifier",
        "strains-staphylococcusaureusatcc43300-classifier"
    ]
    # Family B: the widely-used published classifiers
    FAMILY_B = ["ampeppy", "amplify", "ampredictor"]
    # AMPredictor returns a predicted MIC in uM -- LOWER is more antimicrobial.
    MIC_ORACLES = {"ampredictor"}

    REF_COHORTS = ["ref_MarLys_AMPs", "ref_shuffled_decoys", "ref_nonAMPs"]
    COHORT_LABEL = {
        "ref_MarLys_AMPs": "real AMPs (n=2000)",
        "ref_shuffled_decoys": "shuffled decoys (n=2000)",
        "ref_nonAMPs": "curated non-AMPs (n=877)",
        "submitted_top100": "submitted top-100 (n=100)",
    }
    PALETTE = {
        "ref_MarLys_AMPs": "#1b7837",
        "ref_shuffled_decoys": "#e7298a",
        "ref_nonAMPs": "#7570b3",
        "submitted_top100": "#d95f02",
    }
    PRETTY = {"ampeppy": "amPEPpy", "amplify": "AMPlify", "ampredictor": "AMPredictor"}
    return (
        COHORT_LABEL,
        FAMILY_A,
        FAMILY_B,
        MIC_ORACLES,
        PALETTE,
        PRETTY,
        REF_COHORTS,
        Wedge,
        alt,
        base64,
        gzip,
        io,
        json,
        math,
        np,
        pd,
        plt,
        random,
    )


@app.cell(hide_code=True)
def _(FAMILY_A, FAMILY_B, PRETTY, base64, gzip, io, pd):
    # Per-peptide oracle scores, embedded so the WASM build needs no network.
    DATA_B64 = "@@DATA_B64@@"

    scores = pd.read_csv(io.BytesIO(gzip.decompress(base64.b64decode(DATA_B64))))

    def _label(o, fam):
        return f"{fam} - " + PRETTY.get(o, o.replace("-classifier", "").replace("-", " "))

    ORACLE_OPTIONS = {_label(o, "A"): o for o in FAMILY_A}
    ORACLE_OPTIONS.update({_label(o, "B"): o for o in FAMILY_B})
    ORACLE_FAMILY = {o: "A" for o in FAMILY_A} | {o: "B" for o in FAMILY_B}
    return ORACLE_FAMILY, ORACLE_OPTIONS, scores


@app.cell(hide_code=True)
def _(base64, gzip, json):
    # Explorer assets: order-2 Markov model over the real AMPs, the exported
    # composition-only oracle weights, the mimic scatter and the headline stats.
    ASSETS_B64 = "@@ASSETS_B64@@"

    ASSETS = json.loads(gzip.decompress(base64.b64decode(ASSETS_B64)).decode("utf-8"))
    MARKOV = ASSETS["markov_order2"]
    COMP_ORACLE = ASSETS["composition_oracle"]
    MIMIC = ASSETS["mimic_scatter"]
    STATS = ASSETS["audit_stats"]
    EXAMPLES = ASSETS["explorer_sequences"]
    return COMP_ORACLE, EXAMPLES, MARKOV, MIMIC, STATS


@app.cell(hide_code=True)
def _(MIC_ORACLES, np):
    def activity(frame, oracle):
        """Higher = more AMP-like, for any oracle (MIC oracles get sign-flipped)."""
        v = frame[oracle].to_numpy(dtype=float)
        return -np.log10(np.clip(v, 1e-6, None)) if oracle in MIC_ORACLES else v

    def positive_rate(frame, oracle, prob_cut, mic_cut):
        v = frame[oracle].to_numpy(dtype=float)
        return float((v <= mic_cut).mean()) if oracle in MIC_ORACLES else float((v >= prob_cut).mean())

    def precision_curve(frame, oracle, pos_cohort, neg_cohort):
        pos = activity(frame[frame.cohort == pos_cohort], oracle)
        neg = activity(frame[frame.cohort == neg_cohort], oracle)
        a = np.concatenate([pos, neg])
        y = np.concatenate([np.ones(len(pos)), np.zeros(len(neg))])
        jitter = np.random.default_rng(0).permutation(len(a))
        order = np.lexsort((jitter, -a))
        k = np.arange(1, len(y) + 1)
        prec = np.cumsum(y[order]) / k
        return k, prec

    def first_below(k, prec, floor, min_k=20):
        bad = np.where((prec < floor) & (k >= min_k))[0]
        return int(k[bad[0]]) if len(bad) else None

    return activity, first_below, positive_rate, precision_curve


@app.cell(hide_code=True)
def _(COMP_ORACLE, Wedge, math, np, plt, random):
    # --- Peptide biophysics (pure numpy; identical to the offline pipeline) ------
    AA20 = "ACDEFGHIKLMNPQRSTVWY"

    # Eisenberg consensus hydrophobicity scale (kcal/mol-like units).
    EISENBERG = {
        "A": 0.62, "R": -2.53, "N": -0.78, "D": -0.90, "C": 0.29,
        "Q": -0.85, "E": -0.74, "G": 0.48, "H": -0.40, "I": 1.38,
        "L": 1.06, "K": -1.50, "M": 0.64, "F": 1.19, "P": 0.12,
        "S": -0.18, "T": -0.05, "W": 0.81, "Y": 0.26, "V": 1.08,
    }
    CHARGE = {"K": 1.0, "R": 1.0, "D": -1.0, "E": -1.0, "H": 0.1}
    THREE = {
        "A": "ALA", "R": "ARG", "N": "ASN", "D": "ASP", "C": "CYS",
        "Q": "GLN", "E": "GLU", "G": "GLY", "H": "HIS", "I": "ILE",
        "L": "LEU", "K": "LYS", "M": "MET", "F": "PHE", "P": "PRO",
        "S": "SER", "T": "THR", "W": "TRP", "Y": "TYR", "V": "VAL",
    }
    HELIX_DELTA = 100.0  # degrees per residue in an ideal alpha-helix
    H_MIN, H_MAX = -2.53, 1.38

    COMP_COEF = np.asarray(COMP_ORACLE["coef"], dtype=float)
    COMP_INTERCEPT = float(COMP_ORACLE["intercept"])
    COMP_AAS = COMP_ORACLE["features"][:20]

    def clean_seq(text):
        """Keep only canonical one-letter residues, upper-cased."""
        return "".join(c for c in str(text).upper() if c in AA20)

    def net_charge(seq):
        return float(sum(CHARGE.get(c, 0.0) for c in seq))

    def mean_hydrophobicity(seq):
        return float(np.mean([EISENBERG[c] for c in seq])) if seq else 0.0

    def moment_vector(seq, delta=HELIX_DELTA):
        """(x, y) components of the hydrophobic moment in wheel coordinates."""
        if not seq:
            return 0.0, 0.0
        h = np.array([EISENBERG[c] for c in seq])
        ang = np.deg2rad(delta * np.arange(len(seq)))
        return float(np.sum(h * np.sin(ang))), float(np.sum(h * np.cos(ang)))

    def hydrophobic_moment(seq, delta=HELIX_DELTA):
        """mu_H -- Eisenberg consensus scale, 100 deg/residue, normalised by length."""
        if not seq:
            return 0.0
        mx, my = moment_vector(seq, delta)
        return float(math.hypot(mx, my) / len(seq))

    def comp_features(seq):
        n = max(len(seq), 1)
        return np.array(
            [seq.count(a) / n for a in COMP_AAS] + [len(seq) / 50.0], dtype=float
        )

    def comp_oracle_score(seq):
        """21-feature logistic model trained to reproduce amPEPpy's own binary call."""
        if not seq:
            return 0.0
        z = float(comp_features(seq) @ COMP_COEF) + COMP_INTERCEPT
        return float(1.0 / (1.0 + math.exp(-max(min(z, 60.0), -60.0))))

    def shuffle_seq(seq, seed=0):
        """Composition-preserving permutation: same residues, destroyed order."""
        chars = list(seq)
        random.Random(seed).shuffle(chars)
        return "".join(chars)

    def hydro_color(aa):
        frac = (EISENBERG[aa] - H_MIN) / (H_MAX - H_MIN)
        return plt.get_cmap("coolwarm")(min(max(frac, 0.0), 1.0))

    def helical_wheel(ax, seq, title, delta=HELIX_DELTA):
        """Residues every `delta` degrees, spiralling outward; hydrophobic face shaded."""
        n = len(seq)
        ang = np.deg2rad(delta * np.arange(n))
        rad = 1.0 + 0.055 * np.arange(n)
        x, y = rad * np.sin(ang), rad * np.cos(ang)
        rmax = float(rad.max()) if n else 1.0

        mx, my = moment_vector(seq, delta)
        mu = math.hypot(mx, my) / max(n, 1)
        if mu > 1e-6:
            face = math.degrees(math.atan2(mx, my))  # clockwise from top
            phi = 90.0 - face                        # matplotlib: CCW from +x
            ax.add_patch(
                Wedge((0, 0), rmax + 0.45, phi - 60, phi + 60,
                      facecolor="#f2c14e", alpha=0.22, edgecolor="none", zorder=0)
            )
            ax.annotate(
                "", xy=(0.82 * (rmax + 0.2) * math.sin(math.radians(face)),
                        0.82 * (rmax + 0.2) * math.cos(math.radians(face))),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="#b8860b", lw=1.6),
                zorder=4,
            )

        ax.plot(x, y, "-", color="#c6c6c6", lw=1.1, zorder=1)
        for i, aa in enumerate(seq):
            ax.add_patch(
                plt.Circle((x[i], y[i]), 0.30, facecolor=hydro_color(aa),
                           edgecolor="#333333", lw=0.7, zorder=2)
            )
            ax.text(x[i], y[i], aa, ha="center", va="center", fontsize=8.5,
                    fontweight="bold", color="#111111", zorder=3)
        if n:
            ax.text(x[0], y[0] + 0.42, "N", ha="center", va="bottom",
                    fontsize=8, color="#444444", zorder=3)

        lim = rmax + 0.75
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{title}\nmu_H = {mu:.3f}", fontsize=11)
        return mu

    def helix_pdb(seq, radius=2.3, rise=1.5, delta=HELIX_DELTA):
        """Idealised alpha-helix CA trace (+ outward CB), b-factor = hydrophobicity."""
        lines, conect, serial, prev_ca = [], [], 0, None
        for i, aa in enumerate(seq):
            th = math.radians(delta * i)
            z = rise * i
            bf = 100.0 * (EISENBERG[aa] - H_MIN) / (H_MAX - H_MIN)
            serial += 1
            ca = serial
            lines.append(
                "ATOM  %5d  CA  %3s A%4d    %8.3f%8.3f%8.3f  1.00%6.2f           C"
                % (serial, THREE[aa], i + 1, radius * math.cos(th),
                   radius * math.sin(th), z, bf)
            )
            if prev_ca is not None:
                conect.append("CONECT%5d%5d" % (prev_ca, ca))
            prev_ca = ca
            if aa != "G":
                serial += 1
                lines.append(
                    "ATOM  %5d  CB  %3s A%4d    %8.3f%8.3f%8.3f  1.00%6.2f           C"
                    % (serial, THREE[aa], i + 1, 3.75 * math.cos(th),
                       3.75 * math.sin(th), z + 0.45, bf)
                )
                conect.append("CONECT%5d%5d" % (ca, serial))
        return "\n".join(lines + conect + ["END", ""])

    return (
        AA20,
        EISENBERG,
        clean_seq,
        comp_oracle_score,
        helical_wheel,
        helix_pdb,
        hydrophobic_moment,
        mean_hydrophobicity,
        net_charge,
        shuffle_seq,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 0. The audit — pick an oracle, move the threshold""")
    return


@app.cell(hide_code=True)
def _(ORACLE_OPTIONS, mo):
    oracle_pick = mo.ui.dropdown(
        options=ORACLE_OPTIONS, value="B - AMPlify", label="Oracle", searchable=True
    )
    prob_cut = mo.ui.slider(
        0.05, 0.95, 0.01, value=0.5, label="probability threshold", show_value=True
    )
    mic_cut = mo.ui.slider(
        1, 128, 1, value=16, label="MIC cutoff, uM (AMPredictor only)", show_value=True
    )
    mo.hstack([oracle_pick, prob_cut, mic_cut], justify="start", gap=1.5, wrap=True)
    return mic_cut, oracle_pick, prob_cut


@app.cell(hide_code=True)
def _(
    COHORT_LABEL,
    MIC_ORACLES,
    ORACLE_FAMILY,
    REF_COHORTS,
    mic_cut,
    mo,
    oracle_pick,
    positive_rate,
    prob_cut,
    scores,
):
    # --- Verdict panel ----------------------------------------------------------
    _o = oracle_pick.value
    _rates = {
        _c: positive_rate(scores[scores.cohort == _c], _o, prob_cut.value, mic_cut.value)
        for _c in REF_COHORTS
    }
    _rule = (
        f"MIC <= {mic_cut.value} uM" if _o in MIC_ORACLES else f"score >= {prob_cut.value:.2f}"
    )
    _real, _dec, _non = (_rates[c] for c in REF_COHORTS)
    _inverted = _dec > _real
    _verdict = (
        f"**SIGN INVERTED** - this oracle calls {_dec:.1%} of separately sampled "
        f"shuffle controls antimicrobial but only {_real:.1%} of real AMPs. "
        f"More shuffles pass this threshold. This does not establish their activity."
        if _inverted
        else f"**No threshold inversion** - known AMPs: {_real:.1%}; shuffles: "
        f"{_dec:.1%}; curated non-AMPs: {_non:.1%}. This alone does not validate the ranking."
    )

    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(
                        value=f"{_rates[_c]:.1%}",
                        label=COHORT_LABEL[_c],
                        caption=f"called AMP at {_rule}",
                        bordered=True,
                    )
                    for _c in REF_COHORTS
                ],
                widths="equal",
                gap=1,
            ),
            mo.callout(
                mo.md(
                    f"### {'Sign inversion' if _inverted else 'Ordering preserved'}\n\n"
                    f"Oracle: `{_o}` (family {ORACLE_FAMILY[_o]}) &nbsp;|&nbsp; decision rule: {_rule}\n\n"
                    f"{_verdict}"
                ),
                kind="danger" if _inverted else "success",
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### 0.1 Where the three cohorts land

    Green shows known AMPs; pink shows a separate shuffle cohort. Compare each model within
    its own score scale. A difference in positive rates at one threshold does not
    describe the full ranking. AMPredictor predicts MIC: lower values mean stronger
    predicted activity, so its ranking direction is reversed.
    """
    )
    return


@app.cell(hide_code=True)
def _(
    COHORT_LABEL,
    MIC_ORACLES,
    PALETTE,
    REF_COHORTS,
    alt,
    mic_cut,
    mo,
    np,
    oracle_pick,
    pd,
    prob_cut,
    scores,
):
    # --- Score distributions ----------------------------------------------------
    _o = oracle_pick.value
    _is_mic = _o in MIC_ORACLES
    _sub = scores[scores.cohort.isin(REF_COHORTS)]
    _d = pd.DataFrame(
        {
            "cohort": [COHORT_LABEL[c] for c in _sub.cohort],
            "value": np.log10(np.clip(_sub[_o].to_numpy(float), 1e-6, None))
            if _is_mic
            else _sub[_o].to_numpy(float),
        }
    )
    _domain = [COHORT_LABEL[c] for c in REF_COHORTS]
    _range = [PALETTE[c] for c in REF_COHORTS]
    _xtitle = "log10 predicted MIC (uM)" if _is_mic else f"{_o} score"

    _hist = (
        alt.Chart(_d)
        .mark_area(opacity=0.45, interpolate="step")
        .encode(
            x=alt.X("value:Q", bin=alt.Bin(maxbins=60), title=_xtitle),
            y=alt.Y("count()", stack=None, title="peptides"),
            color=alt.Color(
                "cohort:N",
                scale=alt.Scale(domain=_domain, range=_range),
                legend=alt.Legend(title=None, orient="top"),
            ),
        )
    )
    _cut = np.log10(mic_cut.value) if _is_mic else prob_cut.value
    _line = (
        alt.Chart(pd.DataFrame({"x": [_cut]}))
        .mark_rule(strokeDash=[5, 4], color="#444")
        .encode(x="x:Q")
    )
    mo.ui.altair_chart(
        (_hist + _line).properties(width=920, height=300, title=f"Score distributions - {_o}"),
        chart_selection=False,
        legend_selection=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### 0.2 How many candidates would you select?

    Rank the 2,000 known AMPs and 2,000 shuffles together. Precision@100 is the
    fraction of known AMPs among the first 100 sequences. It is 0.92 for amPEPpy,
    0.90 for AMPlify and 1.00 for OmegAMP broad on this pool.

    This pool uses separately sampled cohorts, so it does not isolate sequence order.
    The curve shows how that fraction changes as you select more sequences.
    The marker is the **first depth at or after k=20 where precision is below 0.75**.
    Ties use a fixed random permutation (seed 0), matching the CLI. This is a
    reference-cohort measure, not a prediction of experimental success. It depends
    on the pool composition; the threshold slider does not change this ranking.
    """
    )
    return


@app.cell(hide_code=True)
def _(
    ORACLE_FAMILY,
    alt,
    first_below,
    mo,
    oracle_pick,
    pd,
    precision_curve,
    scores,
):
    # --- Precision vs depth, computed live --------------------------------------
    _o = oracle_pick.value
    _k, _p = precision_curve(scores, _o, "ref_MarLys_AMPs", "ref_shuffled_decoys")
    _kstar = first_below(_k, _p, 0.75)
    _thin = slice(0, None, 4)
    _curve = pd.DataFrame({"k": _k[_thin], "precision": _p[_thin]})

    _base = (
        alt.Chart(_curve)
        .mark_line(color="#1b7837", strokeWidth=2)
        .encode(
            x=alt.X("k:Q", title="selection depth k (peptides taken from the top)"),
            y=alt.Y("precision:Q", scale=alt.Scale(domain=[0.4, 1.02]), title="precision@k"),
            tooltip=["k:Q", alt.Tooltip("precision:Q", format=".3f")],
        )
    )
    _floor = (
        alt.Chart(pd.DataFrame({"y": [0.75]}))
        .mark_rule(color="#888", strokeDash=[5, 4])
        .encode(y="y:Q")
    )
    _chance = (
        alt.Chart(pd.DataFrame({"y": [0.5]}))
        .mark_rule(color="#bbb")
        .encode(y="y:Q")
    )
    _layers = [_chance, _floor, _base]
    if _kstar is not None:
        _layers.append(
            alt.Chart(pd.DataFrame({"k": [_kstar]}))
            .mark_rule(color="#e7298a", strokeWidth=2)
            .encode(x="k:Q")
        )
        _layers.append(
            alt.Chart(pd.DataFrame({"k": [_kstar], "precision": [0.98], "t": [f"k* = {_kstar}"]}))
            .mark_text(align="left", dx=6, color="#e7298a", fontSize=13, fontWeight="bold")
            .encode(x="k:Q", y="precision:Q", text="t:N")
        )

    _p100 = float(_p[99])
    _p500 = float(_p[499])
    mo.vstack(
        [
            mo.ui.altair_chart(
                alt.layer(*_layers).properties(
                    width=920, height=320,
                    title=f"{_o} - known AMPs vs separate shuffle cohort (unpaired)",
                ),
                chart_selection=False,
                legend_selection=False,
            ),
            mo.hstack(
                [
                    mo.stat(value=f"{_p100:.2f}", label="precision@100", bordered=True),
                    mo.stat(value=f"{_p500:.2f}", label="precision@500", bordered=True),
                    mo.stat(
                        value=str(_kstar) if _kstar else ">4000",
                        label="k* (precision < 0.75)",
                        caption="first crossing below the chosen reference floor",
                        bordered=True,
                    ),
                ],
                widths="equal",
                gap=1,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### 0.3 All 16 oracles at once

    Compare threshold rates and depth statistics for all models. The OmegAMP
    heads target different species or strains and share a model family. Their
    results should not be counted as independent replications.
    """
    )
    return


@app.cell(hide_code=True)
def _(
    FAMILY_A,
    FAMILY_B,
    MIC_ORACLES,
    first_below,
    mic_cut,
    mo,
    pd,
    positive_rate,
    precision_curve,
    prob_cut,
    scores,
):
    # --- Cross-oracle table -----------------------------------------------------
    _rows = []
    for _fam, _list in (("A", FAMILY_A), ("B", FAMILY_B)):
        for _o in _list:
            _r = {
                _c: positive_rate(
                    scores[scores.cohort == _c], _o, prob_cut.value, mic_cut.value
                )
                for _c in ("ref_MarLys_AMPs", "ref_shuffled_decoys", "ref_nonAMPs")
            }
            _k, _p = precision_curve(scores, _o, "ref_MarLys_AMPs", "ref_shuffled_decoys")
            _ks = first_below(_k, _p, 0.75)
            _rows.append(
                {
                    "oracle": _o,
                    "family": _fam,
                    "units": "MIC uM" if _o in MIC_ORACLES else "probability",
                    "real_AMP_pos": round(_r["ref_MarLys_AMPs"], 3),
                    "decoy_pos": round(_r["ref_shuffled_decoys"], 3),
                    "nonAMP_pos": round(_r["ref_nonAMPs"], 3),
                    "prec@100": round(float(_p[99]), 3),
                    "prec@500": round(float(_p[499]), 3),
                    "k_star": _ks if _ks else 4000,
                    "verdict": "SIGN INVERTED"
                    if _r["ref_shuffled_decoys"] > _r["ref_MarLys_AMPs"]
                    else "no threshold inversion",
                }
            )
    audit_table = pd.DataFrame(_rows).sort_values("k_star", ascending=False)
    mo.ui.table(audit_table, selection=None, page_size=20)
    return (audit_table,)


@app.cell(hide_code=True)
def _(audit_table, mo):
    _inv = audit_table[audit_table.verdict == "SIGN INVERTED"]
    mo.callout(
        mo.md(
            f"""
    **At the thresholds currently set:** {len(_inv)} of {len(audit_table)} scorers call
    a larger fraction of shuffles positive than known AMPs
    ({", ".join(_inv.oracle) if len(_inv) else "none"}).
    Median k* is {int(audit_table[audit_table.family == "A"].k_star.median())} for family A versus
    {int(audit_table[audit_table.family == "B"].k_star.median())} for family B.
    These depths describe this 4,000-sequence pool. They cannot be scaled directly
    to a larger generated pool with a different proportion of active peptides.
    """
        ),
        kind="warn",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---

    ## 1. Audit any peptide

    Paste a sequence, or draw one from the audit cohorts. Everything below is computed
    in your browser from the sequence string alone.

    The wheels place residues around an ideal alpha-helix, at 100 degrees per
    residue. Colour shows hydrophobicity; the arrow shows the hydrophobic moment,
    a measure of how unevenly hydrophobic residues are distributed around the helix.
    Shuffling can change this pattern while leaving composition unchanged.

    These are geometric illustrations. They do not predict folding or activity,
    and some AMPs do not form alpha-helices.
    """
    )
    return


@app.cell(hide_code=True)
def _(EXAMPLES, mo):
    seq_source = mo.ui.dropdown(
        options={
            "random real AMP": "real",
            "random shuffled decoy": "decoy",
            "my own sequence (use the box)": "custom",
        },
        value="random real AMP",
        label="sequence source",
    )
    draw_btn = mo.ui.button(label="load a random real AMP", value=0, on_click=lambda v: v + 1,
                            kind="neutral")
    seq_input = mo.ui.text_area(
        value=EXAMPLES["real"][0],
        label="peptide sequence (one-letter code; non-residue characters are dropped)",
        rows=2,
        full_width=True,
    )
    shuffle_seed = mo.ui.slider(
        0, 50, 1, value=7, label="shuffle seed (re-permute the decoy)", show_value=True
    )
    mo.vstack(
        [
            mo.hstack([seq_source, draw_btn, shuffle_seed], justify="start", gap=1.5, wrap=True),
            seq_input,
        ]
    )
    return draw_btn, seq_input, seq_source, shuffle_seed


@app.cell(hide_code=True)
def _(EXAMPLES, clean_seq, draw_btn, random, seq_input, seq_source):
    # Resolve the sequence under audit from the source selector.
    if seq_source.value == "custom":
        query_seq = clean_seq(seq_input.value)
        query_label = "pasted sequence"
    else:
        _pool = EXAMPLES["real"] if seq_source.value == "real" else EXAMPLES["decoy"]
        _rng = random.Random(1000 * int(draw_btn.value) + (0 if seq_source.value == "real" else 1))
        query_seq = clean_seq(_pool[_rng.randrange(len(_pool))])
        query_label = (
            "curated real AMP (drawn from the audit cohort)"
            if seq_source.value == "real"
            else "shuffled decoy (drawn from the audit cohort)"
        )
    return query_label, query_seq


@app.cell(hide_code=True)
def _(
    hydrophobic_moment,
    mean_hydrophobicity,
    mo,
    net_charge,
    query_label,
    query_seq,
):
    _ok = len(query_seq) >= 4
    mo.vstack(
        [
            mo.md(f"**Under audit** ({query_label}): `{query_seq or '(empty)'}`"),
            mo.hstack(
                [
                    mo.stat(value=str(len(query_seq)), label="length", caption="residues",
                            bordered=True),
                    mo.stat(value=f"{net_charge(query_seq):+.1f}", label="net charge",
                            caption="pH 7; K,R +1 / D,E -1 / H +0.1", bordered=True),
                    mo.stat(value=f"{mean_hydrophobicity(query_seq):+.3f}",
                            label="mean hydrophobicity",
                            caption="Eisenberg consensus scale", bordered=True),
                    mo.stat(value=f"{hydrophobic_moment(query_seq):.3f}", label="mu_H",
                            caption="hydrophobic moment, 100 deg/residue", bordered=True),
                ],
                widths="equal",
                gap=1,
            ),
        ]
        + ([] if _ok else [mo.callout(mo.md("Enter at least 4 canonical residues."), kind="warn")])
    )
    return


@app.cell(hide_code=True)
def _(helical_wheel, mo, plt, query_seq, shuffle_seq, shuffle_seed):
    # --- Helical wheels: real order vs composition-preserving shuffle ------------
    _shuf = shuffle_seq(query_seq, seed=int(shuffle_seed.value))
    _fig, _axes = plt.subplots(1, 2, figsize=(10.5, 5.4), dpi=120)
    helical_wheel(_axes[0], query_seq, "sequence as given")
    helical_wheel(_axes[1], _shuf, "composition-preserving shuffle")
    _fig.suptitle(
        "Same composition; a different arrangement around an ideal helix",
        fontsize=12,
    )
    _fig.tight_layout(rect=(0, 0, 1, 0.93))
    mo.vstack([mo.as_html(_fig), mo.md(f"Shuffled sequence: `{_shuf}`")])
    return


@app.cell(hide_code=True)
def _(
    comp_oracle_score,
    hydrophobic_moment,
    mo,
    query_seq,
    shuffle_seq,
    shuffle_seed,
):
    # --- Composition-only oracle: the sequence vs its own shuffle ----------------
    _shuf2 = shuffle_seq(query_seq, seed=int(shuffle_seed.value))
    _s1 = comp_oracle_score(query_seq)
    _s2 = comp_oracle_score(_shuf2)
    _m1 = hydrophobic_moment(query_seq)
    _m2 = hydrophobic_moment(_shuf2)
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(value=f"{_s1:.4f}", label="composition surrogate — as given",
                            caption="P(amPEPpy calls it AMP)", bordered=True),
                    mo.stat(value=f"{_s2:.4f}", label="composition surrogate — shuffled",
                            caption="P(amPEPpy calls it AMP)", bordered=True),
                    mo.stat(value=f"{abs(_s1 - _s2):.4f}", label="|difference|",
                            caption="composition features are identical", bordered=True),
                    mo.stat(value=f"{_m1:.3f} / {_m2:.3f}", label="mu_H as given / shuffled",
                            caption="order-dependent, and it does change", bordered=True),
                ],
                widths="equal",
                gap=1,
            ),
            mo.callout(
                mo.md(
                    f"""
    **Composition-only surrogate:** {_s1:.4f} for the original and {_s2:.4f} for
    its shuffle. They match because the model receives the same amino-acid
    frequencies and length. Hydrophobic moment changes from **{_m1:.3f}** to
    **{_m2:.3f}** because it also depends on residue order. The surrogate was
    trained to imitate amPEPpy calls; these are not amPEPpy predictions.
    """
                ),
                kind="info",
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### 1.1 The same peptide as a 3D helix

    An idealised alpha-helix built analytically from the sequence — CA on a helix of
    radius 2.3 A, rise 1.5 A per residue, 100 deg per residue, with CB projected
    outward (glycine omitted). Residues are coloured by Eisenberg hydrophobicity (red
    = hydrophobic, blue = charged/polar), so the amphipathic stripe that the wheel
    shows as a wedge appears in 3D as a coloured face running up one side of the
    cylinder. Drag to rotate. This is a geometric idealisation, not a structure
    prediction — no folding is implied.
    """
    )
    return


@app.cell(hide_code=True)
def _(helix_pdb, json, mo, query_seq, shuffle_seq, shuffle_seed):
    # --- 3Dmol.js viewer (CDN) with an in-iframe fallback message ---------------
    _pdb_real = helix_pdb(query_seq)
    _pdb_shuf = helix_pdb(shuffle_seq(query_seq, seed=int(shuffle_seed.value)))

    def _viewer_html(pdb_a, pdb_b):
        _js = """
    function draw(id, pdb) {
      var v = $3Dmol.createViewer(document.getElementById(id),
                                  {backgroundColor: "white"});
      v.addModel(pdb, "pdb");
      v.setStyle({}, {stick: {radius: 0.22, colorscheme:
                       {prop: "b", gradient: "rwb", min: 100, max: 0}},
                      sphere: {scale: 0.30, colorscheme:
                       {prop: "b", gradient: "rwb", min: 100, max: 0}}});
      v.zoomTo();
      v.render();
      v.spin("y", 0.4);
    }
    function boot() {
      if (typeof $3Dmol === "undefined") {
        document.getElementById("fallback").style.display = "block";
        return;
      }
      draw("v1", PDB_A);
      draw("v2", PDB_B);
    }
    """
        return (
            "<html><head>"
            '<script src="https://cdn.jsdelivr.net/npm/3dmol@2.4.2/build/3Dmol-min.js"></script>'
            "<style>body{margin:0;font-family:system-ui,sans-serif}"
            ".row{display:flex;gap:16px}.row>div{flex:1;min-width:0}"
            ".cell{width:100%;position:relative;height:330px;"
            "border:1px solid #ddd;border-radius:6px}"
            ".cap{font-size:12px;text-align:center;color:#444;padding:3px}"
            "#fallback{display:none;padding:14px;font-size:13px;color:#8a4b00;"
            "background:#fff5e6;border:1px solid #f0c080;border-radius:6px}</style>"
            "</head><body>"
            '<div id="fallback">3Dmol.js could not be loaded from the CDN '
            "(offline, or the CDN is blocked). The helical wheels above carry the same "
            "information without any network dependency.</div>"
            '<div class="row">'
            '<div><div class="cell" id="v1"></div><div class="cap">sequence as given</div></div>'
            '<div><div class="cell" id="v2"></div><div class="cap">composition-preserving shuffle</div></div>'
            "</div>"
            "<script>var PDB_A = " + json.dumps(pdb_a)
            + "; var PDB_B = " + json.dumps(pdb_b)
            + ";" + _js + "window.addEventListener('load', boot);</script>"
            "</body></html>"
        )

    mo.iframe(_viewer_html(_pdb_real, _pdb_shuf), height="400px")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---

    ## 2. Generate control sequences

    This order-2 Markov sampler chooses each residue from the preceding two,
    using transition counts fitted to the 2,000 known AMPs. Score the samples
    with the **composition-only surrogate** and compare them with known AMPs.
    A high surrogate score does not show that a sample is active or inactive.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    n_gen = mo.ui.slider(10, 500, 10, value=200, label="peptides to generate", show_value=True)
    gen_len = mo.ui.slider(8, 50, 1, value=18, label="target length", show_value=True)
    gen_seed = mo.ui.slider(0, 999, 1, value=0, label="random seed", show_value=True)
    gen_thresh = mo.ui.slider(0.05, 0.95, 0.05, value=0.5, label="call threshold p >=",
                              show_value=True)
    use_real_lengths = mo.ui.checkbox(
        value=False, label="draw lengths from the real AMP length distribution instead"
    )
    mo.vstack(
        [
            mo.hstack([n_gen, gen_len, gen_seed], justify="start", gap=1.5, wrap=True),
            mo.hstack([gen_thresh, use_real_lengths], justify="start", gap=1.5, wrap=True),
        ]
    )
    return gen_len, gen_seed, gen_thresh, n_gen, use_real_lengths


@app.cell(hide_code=True)
def _(MARKOV, comp_oracle_score, gen_len, gen_seed, n_gen, random, use_real_lengths):
    # --- Order-2 Markov sampler, pure Python, seeded ----------------------------
    MARKOV_COUNTS = MARKOV["counts"]
    MARKOV_CACHE = {}

    def markov_dist(ctx):
        d = MARKOV_CACHE.get(ctx)
        if d is None:
            row = (
                MARKOV_COUNTS.get(ctx)
                or MARKOV_COUNTS.get("^" + ctx[-1])
                or MARKOV_COUNTS["^^"]
            )
            keys = list(row.keys())
            tot = float(sum(row.values()))
            d = (keys, [row[k] / tot for k in keys])
            MARKOV_CACHE[ctx] = d
        return d

    def sample_peptide(rng, length):
        out = []
        ctx = "^^"
        for _ in range(length):
            keys, probs = markov_dist(ctx)
            aa = rng.choices(keys, weights=probs, k=1)[0]
            out.append(aa)
            ctx = (ctx + aa)[-2:]
        return "".join(out)

    _rng = random.Random(int(gen_seed.value))
    _lens = MARKOV["lengths"]
    generated = []
    for _i in range(int(n_gen.value)):
        _L = _rng.choice(_lens) if use_real_lengths.value else int(gen_len.value)
        generated.append(sample_peptide(_rng, _L))
    gen_scores = [comp_oracle_score(s) for s in generated]
    return gen_scores, generated


@app.cell(hide_code=True)
def _(MIMIC, alt, gen_scores, gen_thresh, generated, mo, np, pd):
    # --- Generated-vs-real score distributions + live counter --------------------
    _n_called = int(np.sum(np.asarray(gen_scores) >= gen_thresh.value))
    _n_total = len(gen_scores)
    _real_called = float(np.mean(np.asarray(MIMIC["real"]["comp"]) >= gen_thresh.value))

    _d = pd.concat(
        [
            pd.DataFrame({"score": gen_scores, "set": "Markov-generated (this run)"}),
            pd.DataFrame({"score": MIMIC["real"]["comp"], "set": "real AMPs (n=2000)"}),
        ]
    )
    _hist = (
        alt.Chart(_d)
        .mark_area(opacity=0.45, interpolate="step")
        .encode(
            x=alt.X("score:Q", bin=alt.Bin(extent=[0, 1], maxbins=40),
                    title="composition-only surrogate score"),
            y=alt.Y("count()", stack=None, title="peptides"),
            color=alt.Color(
                "set:N",
                scale=alt.Scale(
                    domain=["Markov-generated (this run)", "real AMPs (n=2000)"],
                    range=["#d95f02", "#1b7837"],
                ),
                legend=alt.Legend(title=None, orient="top"),
            ),
        )
    )
    _rule = (
        alt.Chart(pd.DataFrame({"x": [gen_thresh.value]}))
        .mark_rule(color="#444", strokeDash=[5, 4])
        .encode(x="x:Q")
    )

    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(
                        value=f"{_n_called} of {_n_total}",
                        label=f"pass surrogate threshold >= {gen_thresh.value:.2f}",
                        caption=f"{_n_called / max(_n_total, 1):.1%} of this Markov sample",
                        bordered=True,
                    ),
                    mo.stat(
                        value=f"{_real_called:.1%}",
                        label="same rate on the 2,000 real AMPs",
                        caption="same surrogate, same threshold",
                        bordered=True,
                    ),
                    mo.stat(
                        value=f"{float(np.median(gen_scores)):.3f}",
                        label="median generated score",
                        caption=f"real-AMP median {float(np.median(MIMIC['real']['comp'])):.3f}",
                        bordered=True,
                    ),
                ],
                widths="equal",
                gap=1,
            ),
            mo.ui.altair_chart(
                (_hist + _rule).properties(
                    width=920, height=280,
                    title="Surrogate scores: generated sequences and known AMPs",
                ),
                chart_selection=False,
                legend_selection=False,
            ),
            mo.md(
                f"""
    **{_n_called} of {_n_total} samples** pass the composition-only surrogate's
    threshold, compared with **{_real_called:.1%}** of known AMPs. This shows how
    a simple sampler can obtain high surrogate scores. Neither these samples nor
    their activity have been tested here, and the original amPEPpy model is not
    running in this panel.
    """
            ),
            mo.download(
                data="".join(
                    f">markov_decoy_{_i + 1} len={len(_s)} comp_score={_v:.4f}\n{_s}\n"
                    for _i, (_s, _v) in enumerate(zip(generated, gen_scores))
                ).encode("utf-8"),
                filename="markov_decoys.fasta",
                mimetype="text/plain",
                label="download this generated set as FASTA",
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(generated, gen_scores, mo, pd):
    _t = pd.DataFrame(
        {
            "sequence": generated,
            "length": [len(s) for s in generated],
            "comp_oracle_score": [round(v, 4) for v in gen_scores],
        }
    ).sort_values("comp_oracle_score", ascending=False)
    mo.vstack(
        [
            mo.md("**Generated sequences, ranked by the composition-only surrogate** "
                  "(paste any row into section 1 to see its wheel):"),
            mo.ui.table(_t, selection=None, page_size=10),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---

    ## 3. How much can composition explain?

    Fit a 21-feature logistic regression — the 20 amino-acid frequencies plus
    length/50, no order information whatsoever — to predict **amPEPpy's own binary
    call**. The stored results measure agreement with model calls, not activity.
    Composition may carry biological signal; high agreement does not prove a
    causal explanation of amPEPpy behaviour.
    """
    )
    return


@app.cell(hide_code=True)
def _(MIMIC, STATS, alt, mo, pd):
    # --- Mimic scatter: composition-only score vs amPEPpy ------------------------
    _d = pd.concat(
        [
            pd.DataFrame(
                {
                    "comp": MIMIC["real"]["comp"],
                    "ampeppy": MIMIC["real"]["ampeppy"],
                    "mu_H": MIMIC["real"]["mu_h"],
                    "cohort": "real AMPs",
                }
            ),
            pd.DataFrame(
                {
                    "comp": MIMIC["decoy"]["comp"],
                    "ampeppy": MIMIC["decoy"]["ampeppy"],
                    "mu_H": MIMIC["decoy"]["mu_h"],
                    "cohort": "shuffled decoys",
                }
            ),
        ]
    )
    _sc = (
        alt.Chart(_d)
        .mark_circle(size=18, opacity=0.35)
        .encode(
            x=alt.X("comp:Q", title="composition-only surrogate score (21 features, in-browser)",
                    scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("ampeppy:Q", title="amPEPpy score", scale=alt.Scale(domain=[0, 1])),
            color=alt.Color(
                "cohort:N",
                scale=alt.Scale(domain=["real AMPs", "shuffled decoys"],
                                range=["#1b7837", "#e7298a"]),
                legend=alt.Legend(title=None, orient="top"),
            ),
            tooltip=[alt.Tooltip("comp:Q", format=".3f"),
                     alt.Tooltip("ampeppy:Q", format=".3f"),
                     alt.Tooltip("mu_H:Q", format=".3f"), "cohort:N"],
        )
        .properties(
            height=380,
            title="A bag-of-residues model reproduces amPEPpy — and both cohorts sit in the same cloud",
        )
    )
    mo.vstack(
        [
            mo.ui.altair_chart(_sc, chart_selection=False, legend_selection=False),
            mo.hstack(
                [
                    mo.stat(
                        value=f"{STATS['composition_mimic']['auroc_logistic']:.3f}",
                        label="AUROC, logistic mimic",
                        caption="21 composition features -> amPEPpy's call; this is the model running in-browser",
                        bordered=True,
                    ),
                    mo.stat(
                        value=f"{STATS['composition_mimic']['auroc_gb']:.3f}",
                        label="AUROC, gradient boosting",
                        caption="same features, fitted offline (not shipped in this app)",
                        bordered=True,
                    ),
                    mo.stat(
                        value=f"{STATS['composition_mimic']['n_train']:,} / {STATS['composition_mimic']['n_test']:,}",
                        label="train / test peptides",
                        caption="held-out split",
                        bordered=True,
                    ),
                ],
                widths="equal",
                gap=1,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(STATS, mo):
    _a = STATS["auroc_real_vs_decoy"]
    _m = STATS["mu_h_median"]
    _p = STATS["omegamp_broad_p95"]
    mo.callout(
        mo.md(
            f"""
    ### What the comparison can tell us

    Hydrophobic moment separates known AMPs from the separate shuffle cohort at AUROC
    **{_a['hydrophobic_moment']:.3f}** in the stored analysis. amPEPpy and AMPlify
    score **{_a['ampeppy']:.3f}** and **{_a['amplify']:.3f}** on that same contrast.
    An AUROC of 0.5 is chance ordering.

    OmegAMP broad is also near chance overall (**{_a['omegamp_broad']:.3f}**),
    despite enriching known AMPs near the top of its ranking. Inspect both the
    overall ranking and precision at the depth you plan to use.

    These results concern this reference set. Related OmegAMP heads are not
    independent replications, and their low positive rates do not prove that
    they are better activity predictors. Training-set overlap was not audited.
    """
        ),
        kind="warn",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---

    ### Data provenance

    Rates, curves and sequence features recompute in-browser; surrogate training
    statistics and AUROCs are stored offline results. The audit panels use per-peptide
    oracle scores embedded in this notebook (gzip + base64, ~260 kB); the explorer
    panels run from a second embedded blob (~0.2 MB of JSON) holding the Markov
    transition counts, the composition-oracle weights, the mimic scatter and the
    headline statistics. The published build therefore fetches no data at runtime and
    needs no server and no login. The one external resource is the 3Dmol.js bundle in
    section 1.1, loaded from a CDN; if it is unavailable the viewer says so and the
    helical wheels carry the same information.

    * **Peptides** — 4,977 sequences: 2,000 curated real AMPs, 2,000
      a separate shuffled-AMP cohort (only 87 compositions overlap with the known
      AMP cohort; this is not a paired control), 877 curated non-AMPs, and the
      100 sequences of a real competition submission.
    * **Family A oracles (13)** — OmegAMP's hard-negative-trained classifiers: the
      broad classifier, 5 per-species and 7 per-strain heads. Scored probabilities.
    * **Family B oracles (3)** — amPEPpy, AMPlify (probabilities) and AMPredictor
      (predicted MIC in uM, lower = more active; thresholded at the MIC cutoff
      slider, default 16 uM).
    * **Derived live** — positive rates at the chosen decision rule, precision@k on
      the 50/50 real-AMP vs shuffled-decoy pool, k* (the depth at which precision@k
      first drops below 0.75, k >= 20), peptide net charge / mean hydrophobicity /
      hydrophobic moment, helical wheels, the idealised helix coordinates, the
      composition-oracle score, and the order-2 Markov samples.
    * **Scales** — Eisenberg consensus hydrophobicity; mu_H computed at 100 deg per
      residue and normalised by length; net charge at pH 7 with K,R = +1, D,E = -1,
      H = +0.1.

    Part of **Oracle Audit**, an OSI Hackathon 2026 submission: a benchmark-validity
    audit of the in-silico oracles used to evaluate generative AMP design.
    """
    )
    return


if __name__ == "__main__":
    app.run()
