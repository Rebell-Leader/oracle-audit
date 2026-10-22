"""Score the AutoScientist checkpoint on the never-uploaded 400-row holdout.

Reports accuracy, real-recall and decoy-recall separately: a model that answers one
label for everything scores well on one and badly on the other, which is exactly the
failure mode the audit is about.
"""
import json, sys
from pathlib import Path
import pandas as pd, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

HERE = Path(__file__).resolve().parent
BASE = "google/gemma-3-4b-it"          # adapter declares togethercomputer/gemma-3-4b-it (not public)
ADAPTER = HERE / "checkpoint/extracted_mm"
LABELS = ["real", "shuffled"]


def load(with_adapter: bool):
    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.bfloat16, device_map="cuda:0")
    if with_adapter:
        model = PeftModel.from_pretrained(model, str(ADAPTER))
    return tok, model.eval()


def render(tok, prompt, template):
    if template == "chat":
        return tok.apply_chat_template([{"role": "user", "content": prompt}],
                                       tokenize=False, add_generation_prompt=True)
    return prompt + "\n"


@torch.no_grad()
def label_logprobs(tok, model, text, label):
    ctx = tok(text, return_tensors="pt", add_special_tokens=True).input_ids
    full = tok(text + label, return_tensors="pt", add_special_tokens=True).input_ids.to(model.device)
    logits = model(full).logits.float().log_softmax(-1)
    tgt = full[0, ctx.shape[1]:]
    lp = logits[0, ctx.shape[1] - 1: -1].gather(-1, tgt[:, None]).sum().item()
    return lp / max(len(tgt), 1)


def evaluate(tok, model, df, template):
    preds = []
    for prompt in df.instruction:
        text = render(tok, prompt, template)
        preds.append(max(LABELS, key=lambda l: label_logprobs(tok, model, text, l)))
    preds = pd.Series(preds, index=df.index)
    real = df.response.eq("real")
    return {"template": template, "n": int(len(df)),
            "accuracy": round(float((preds == df.response).mean()), 4),
            "real_recall": round(float((preds[real] == "real").mean()), 4),
            "decoy_recall": round(float((preds[~real] == "shuffled").mean()), 4),
            "predicted_real_fraction": round(float(preds.eq("real").mean()), 4)}


if __name__ == "__main__":
    df = pd.read_csv(HERE / "hardneg_holdout.csv")
    report = {"base_model_used": BASE, "adapter": str(ADAPTER.relative_to(HERE.parent)),
              "holdout_rows": int(len(df)), "runs": []}
    for with_adapter in (True, False):
        tok, model = load(with_adapter)
        for template in ("chat", "plain"):
            res = evaluate(tok, model, df, template)
            res["model"] = "autoscientist_lora" if with_adapter else "base"
            print(res, flush=True)
            report["runs"].append(res)
        del model; torch.cuda.empty_cache()
    (HERE / "holdout_evaluation.json").write_text(json.dumps(report, indent=2))
    print("wrote", HERE / "holdout_evaluation.json")
