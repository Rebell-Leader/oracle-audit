"""Oracle Audit x Adaption Labs — train a hard-negative-aware AMP oracle.

The audit (see repo README) shows the published AMP oracles rank composition-preserving
shuffled decoys ABOVE real curated AMPs. This script tests the constructive converse: can a
general-purpose LLM, fine-tuned on exactly that contrast, learn the discrimination the
published oracles lack?

Task: real curated AMP vs composition-preserving shuffle of a real AMP (same amino-acid
composition, order destroyed) — 4,000 balanced examples, 3,600 train / 400 held out.

Run:
    export ADAPTION_API_KEY=...        # https://adaptionlabs.ai/app/settings?tab=api_keys
    python build_and_run.py
"""
import json, random, time
import pandas as pd
from adaption import Adaption

INSTR = ("You are an antimicrobial-peptide oracle. Decide whether the peptide below is a REAL curated "
         "antimicrobial peptide or a COMPOSITION-PRESERVING SHUFFLE of one (same amino-acid composition, "
         "order destroyed). Answer with one word: real or shuffled.\n\nPeptide: {}")


def build(cohorts_path="../../cohorts.json", seed=0):
    coh = json.load(open(cohorts_path))
    rows = [{"instruction": INSTR.format(s), "response": "real"} for s in coh["ref_MarLys_AMPs"]]
    rows += [{"instruction": INSTR.format(s), "response": "shuffled"} for s in coh["ref_shuffled_decoys"]]
    random.Random(seed).shuffle(rows)
    pd.DataFrame(rows[400:]).to_csv("hardneg_train.csv", index=False)
    pd.DataFrame(rows[:400]).to_csv("hardneg_holdout.csv", index=False)
    return len(rows) - 400, 400


def main():
    client = Adaption()                       # reads ADAPTION_API_KEY
    ds = client.datasets.upload_file(
        "hardneg_train.csv",
        processing_mode="raw",
        column_mapping={"prompt": "instruction", "completion": "response"},
    )
    while True:                               # ingestion is asynchronous
        st = client.datasets.get_status(ds.dataset_id)
        if st.status == "failed":
            raise RuntimeError(st.error_data)
        if st.row_count is not None:
            print("ingested rows:", st.row_count)
            break
        time.sleep(5)

    run = client.autoscientist.create(dataset_id=ds.dataset_id, model="google/gemma-3-4b-it")
    print("run:", run.id, run.status, run.model, "max_iterations:", run.max_iterations)

    run = client.autoscientist.wait_for_completion(run.id)
    print("status:", run.status, "best win rate:", run.best_win_rate, "hyperparams:", run.best_hyperparams)
    return run


def score_holdout(predict):
    """Evaluate any callable(prompt) -> 'real'/'shuffled' with the audit's own sign test."""
    df = pd.read_csv("hardneg_holdout.csv")
    pred = df.instruction.map(predict)
    acc = (pred == df.response).mean()
    real = df.response.eq("real")
    print(f"holdout accuracy {acc:.3f} | real recall {(pred[real] == 'real').mean():.3f} "
          f"| decoy recall {(pred[~real] == 'shuffled').mean():.3f}")
    return acc


if __name__ == "__main__":
    build()
    main()
