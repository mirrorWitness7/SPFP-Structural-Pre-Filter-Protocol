# run_eval.py
import json, os, sys, collections, math
from typing import List, Set, Dict

# --- Import detector (supports either detect() or label()) ---
try:
    from spfp import detector as DET
except Exception as e:
    print("ERROR: cannot import spfp.detector — make sure your repo has spfp/detector.py")
    raise

def detect_codes(text: str) -> List[str]:
    if hasattr(DET, "detect"):
        out = DET.detect(text)
    elif hasattr(DET, "label"):
        out = DET.label(text)
    else:
        raise RuntimeError("spfp.detector must expose detect(text) or label(text)")
    if out is None:
        return []
    # Normalize to list of unique, sorted strings
    if isinstance(out, (set, tuple)):
        out = list(out)
    out = [str(x).strip() for x in out if str(x).strip()]
    return sorted(set(out))

def load_cases(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def f1(p, r):
    return 0.0 if (p + r) == 0 else 2*p*r/(p+r)

def main():
    cases_path = "evals/cases.jsonl"
    if len(sys.argv) > 1:
        cases_path = sys.argv[1]
    if not os.path.exists(cases_path):
        print(f"ERROR: {cases_path} not found")
        sys.exit(1)

    data = load_cases(cases_path)

    # Collect code universe from file + detector outputs
    all_codes = set()
    gold_list = []
    pred_list = []
    ids = []
    texts = []

    for row in data:
        ids.append(row.get("id",""))
        texts.append(row.get("text",""))
        gold = row.get("expect", []) or []
        gold = sorted(set([str(x).strip() for x in gold if str(x).strip()]))
        pred = detect_codes(row.get("text",""))

        gold_list.append(gold)
        pred_list.append(pred)
        all_codes.update(gold)
        all_codes.update(pred)

    # Ensure stable order; add a special NONE class for clean confusion display
    all_codes = sorted([c for c in all_codes if c])  # only non-empty
    CODE_NONE = "NONE"

    # Per-code TP/FP/FN
    tp = collections.Counter()
    fp = collections.Counter()
    fn = collections.Counter()
    tn = collections.Counter()  # not used for F1, but available

    # Micro counts
    micro_TP = 0
    micro_FP = 0
    micro_FN = 0

    # For confusion matrix (multi-label): we spread each example’s predictions across codes
    # A cell (r=gold_code, c=pred_code) increments when both appear in the same sample.
    # Also account for codes missed (gold->NONE) and spurious (NONE->pred).
    cm = collections.defaultdict(lambda: collections.Counter())

    # Error notebook: keep top FP/FN examples
    fp_examples = collections.defaultdict(list)  # code -> [(id, text)]
    fn_examples = collections.defaultdict(list)

    for i, (gold, pred) in enumerate(zip(gold_list, pred_list)):
        gold_set = set(gold)
        pred_set = set(pred)

        # Update per-code counters
        for code in all_codes:
            in_gold = code in gold_set
            in_pred = code in pred_set
            if in_gold and in_pred:
                tp[code] += 1
                micro_TP += 1
            elif (not in_gold) and in_pred:
                fp[code] += 1
                micro_FP += 1
                if len(fp_examples[code]) < 6:
                    fp_examples[code].append((ids[i], texts[i]))
            elif in_gold and (not in_pred):
                fn[code] += 1
                micro_FN += 1
                if len(fn_examples[code]) < 6:
                    fn_examples[code].append((ids[i], texts[i]))
            else:
                tn[code] += 1

        # Confusion matrix population
        # gold->pred for overlapping codes
        for g in gold_set:
            if g not in all_codes: 
                continue
            if g in pred_set:
                # split credit across matched predictions (for display; TP already counted above)
                for p in (pred_set & {g}):
                    cm[g][p] += 1
            else:
                # missed: gold code -> NONE
                cm[g][CODE_NONE] += 1

        # spurious: NONE -> each predicted code that wasn't in gold
        for p in (pred_set - gold_set):
            if p in all_codes:
                cm[CODE_NONE][p] += 1

    # Micro scores
    micro_prec = 0.0 if (micro_TP + micro_FP) == 0 else micro_TP / (micro_TP + micro_FP)
    micro_rec  = 0.0 if (micro_TP + micro_FN) == 0 else micro_TP / (micro_TP + micro_FN)
    micro_f1   = f1(micro_prec, micro_rec)

    # Macro scores
    per_code_rows = []
    prec_sum = rec_sum = f1_sum = 0.0
    for code in all_codes:
        TP, FP, FN = tp[code], fp[code], fn[code]
        P = 0.0 if (TP + FP) == 0 else TP / (TP + FP)
        R = 0.0 if (TP + FN) == 0 else TP / (TP + FN)
        F = f1(P, R)
        prec_sum += P; rec_sum += R; f1_sum += F
        per_code_rows.append((code, TP, FP, FN, P, R, F))
    nC = max(1, len(all_codes))
    macro_prec = prec_sum / nC
    macro_rec  = rec_sum / nC
    macro_f1   = f1_sum / nC

    # --- Print report ---
    print("="*72)
    print("SPFP Evaluation Report")
    print("="*72)
    print(f"Samples: {len(data)}")
    print("\nMicro-Averaged:")
    print(f"  Precision: {micro_prec:.3f}  Recall: {micro_rec:.3f}  F1: {micro_f1:.3f}")

    print("\nMacro-Averaged:")
    print(f"  Precision: {macro_prec:.3f}  Recall: {macro_rec:.3f}  F1: {macro_f1:.3f}")

    print("\nPer-Code Metrics:")
    print(f"{'Code':<10} {'TP':>4} {'FP':>4} {'FN':>4}   {'P':>6} {'R':>6} {'F1':>6}")
    for code, TP, FP, FN, P, R, F in per_code_rows:
        print(f"{code:<10} {TP:>4} {FP:>4} {FN:>4}   {P:>6.3f} {R:>6.3f} {F:>6.3f}")

    # Confusion matrix header
    labels = all_codes + [CODE_NONE]
    idx = {c:i for i,c in enumerate(labels)}
    print("\nConfusion Matrix (rows = GOLD, cols = PRED):")
    # header row
    header = [""] + labels
    print("\t".join(header))
    for r in labels:
        row = [r]
        for c in labels:
            row.append(str(cm[r][c]))
        print("\t".join(row))

    # Error notebook
    print("\nTop False NEGATIVES (missed codes):")
    for code in all_codes:
        items = fn_examples[code]
        if not items: 
            continue
        print(f"\n  {code} — {len(items)} examples")
        for _id, txt in items:
            snippet = txt.replace("\n"," ")[:140]
            print(f"    - {(_id or '')}: {snippet}")

    print("\nTop False POSITIVES (over-flags):")
    for code in all_codes:
        items = fp_examples[code]
        if not items: 
            continue
        print(f"\n  {code} — {len(items)} examples")
        for _id, txt in items:
            snippet = txt.replace("\n"," ")[:140]
            print(f"    + {(_id or '')}: {snippet}")

    print("\nDone.")

if __name__ == "__main__":
    main()
