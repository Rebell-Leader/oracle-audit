"""Check embedded notebook data and all 16 curves against the released table."""
import importlib.util
import json
from collections import Counter
from pathlib import Path
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "package"))
from oracle_audit import depth_test, composition_overlap

spec = importlib.util.spec_from_file_location("notebook", "app/oracle_audit_app.py")
notebook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notebook)
outputs, defs = notebook.app.run()
raw = pd.read_csv("package/oracle_audit_scores_wide.csv")
assert raw.shape == (14977, 20)
assert not raw.isna().any().any()
pos = raw[raw.cohort == "ref_MarLys_AMPs"]
neg = raw[raw.cohort == "ref_shuffled_decoys"]
matched = composition_overlap(pos.sequence, neg.sequence)
assert matched == 87, "Recheck and update the documented cohort provenance"
results = []
for oracle in raw.columns[4:]:
    cli = depth_test(pos[oracle], neg[oracle], lower_is_better=oracle == "ampredictor")
    k, curve = defs["precision_curve"](defs["scores"], oracle,
                                      "ref_MarLys_AMPs", "ref_shuffled_decoys")
    np.testing.assert_array_equal(cli["precision"], curve, err_msg=oracle)
    first = defs["first_below"](k, curve, .75)
    assert first == cli["k_first_below"], (oracle, first, cli["k_first_below"])
    results.append({"oracle": oracle, "first_below": first, "precision_at_100": curve[99]})
report = {"cells": len(outputs), "curves_matching_cli": len(results),
          "composition_overlap": matched, "reference_cohorts_paired": False, "rows": len(raw)}
print(report)
(Path(__file__).resolve().parent / "analysis_verification.json").write_text(json.dumps(report, indent=2))
pd.DataFrame(results).to_csv(Path(__file__).resolve().parent / "verified_curves.csv", index=False)
