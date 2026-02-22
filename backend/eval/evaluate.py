import json
import sys
import time
from pathlib import Path

import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score, auc, confusion_matrix,
    f1_score, precision_score, recall_score, roc_curve
)
from transformers import AutoModelForCausalLM, AutoTokenizer

CORPUS_PATH  = Path("corpus_full.csv")
OUTPUT_CSV   = Path("evaluation_results.csv")
OUTPUT_JSON  = Path("evaluation_summary.json")
OUTPUT_PLOT  = Path("roc_curve.png")
MODEL_NAME   = "sdadas/polish-gpt2-small"
MAX_LENGTH   = 512   


def load_model():
    print(f"Ładowanie modelu: {MODEL_NAME}")
    print("Pierwsze uruchomienie pobierze ~500MB...\n")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()
    print("Model załadowany!\n")
    return model, tokenizer


def compute_perplexity(text: str, model, tokenizer) -> float | None:
    try:
        inputs = tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=MAX_LENGTH
        )
        if inputs["input_ids"].shape[1] < 5:
            return None
        with torch.no_grad():
            outputs = model(inputs["input_ids"], labels=inputs["input_ids"])
        return round(min(torch.exp(outputs.loss).item(), 2000.0), 4)
    except Exception as e:
        print(f"  Błąd perplexity: {e}")
        return None


def main():
    if not CORPUS_PATH.exists():
        print(f"BŁĄD: Nie znaleziono pliku {CORPUS_PATH}")
        sys.exit(1)

    df = pd.read_csv(CORPUS_PATH)
    required = {"label", "text"}
    if not required.issubset(df.columns):
        print(f"BŁĄD: Plik CSV musi zawierać kolumny: {required}")
        sys.exit(1)

    has_source = "source" in df.columns
    df["label"] = df["label"].str.strip().str.lower()
    valid = df["label"].isin(["human", "ai"])
    if not valid.all():
        print(f"OSTRZEŻENIE: Usunięto {(~valid).sum()} wierszy z nieprawidłowymi etykietami.")
        df = df[valid].reset_index(drop=True)

    n_human = (df["label"] == "human").sum()
    n_ai    = (df["label"] == "ai").sum()
    print(f"Korpus: {len(df)} tekstów  (human: {n_human}, AI: {n_ai})\n")

    model, tokenizer = load_model()
    perplexities = []
    for i, row in df.iterrows():
        t0 = time.time()
        ppx = compute_perplexity(str(row["text"]), model, tokenizer)
        elapsed = time.time() - t0
        src = f" [{row['source']}]" if has_source else ""
        status = f"  [{i+1:02d}/{len(df)}]{src} | label={row['label']} | ppx={ppx:.2f} | {elapsed:.1f}s"
        print(status)
        perplexities.append(ppx)

    df["perplexity"] = perplexities

    df_valid = df.dropna(subset=["perplexity"]).copy()
    if len(df_valid) < len(df):
        print(f"\nOSTRZEŻENIE: Pominięto {len(df)-len(df_valid)} tekstów (błąd modelu).")

    y_true  = (df_valid["label"] == "ai").astype(int)
    y_score = -df_valid["perplexity"]

    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)

    youdens_j  = tpr - fpr
    best_idx   = youdens_j.argmax()
    best_thresh_neg = thresholds[best_idx]   
    optimal_ppx = round(-best_thresh_neg, 4)

    df_valid["ai_predicted"] = df_valid["perplexity"] < optimal_ppx
    y_pred = df_valid["ai_predicted"].astype(int)

    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec  = recall_score(y_true, y_pred, zero_division=0)
    f1   = f1_score(y_true, y_pred, zero_division=0)
    cm   = confusion_matrix(y_true, y_pred).tolist()

    df_valid["label_predicted"] = df_valid["ai_predicted"].map({True: "ai", False: "human"})
    df_valid["correct"] = df_valid["label"] == df_valid["label_predicted"]

    print("\n" + "="*60)
    print("WYNIKI EWALUACJI")
    print("="*60)
    print(f"  Optymalny próg perplexity:  {optimal_ppx:.4f}")
    print(f"  AUC-ROC:                    {roc_auc:.4f}")
    print(f"  Accuracy:                   {acc:.4f}  ({acc*100:.1f}%)")
    print(f"  Precision:                  {prec:.4f}")
    print(f"  Recall:                     {rec:.4f}")
    print(f"  F1:                         {f1:.4f}")
    print(f"\n  Macierz pomyłek:")
    print(f"                 Pred: Human   Pred: AI")
    print(f"    True: Human      {cm[0][0]:5d}      {cm[0][1]:5d}")
    print(f"    True: AI         {cm[1][0]:5d}      {cm[1][1]:5d}")

    errors = df_valid[~df_valid["correct"]]
    if len(errors) > 0:
        print(f"\n  Błędne klasyfikacje ({len(errors)}):")
        for _, r in errors.iterrows():
            src = f" | {r['source']}" if has_source else ""
            print(f"    label={r['label']} → pred={r['label_predicted']} | ppx={r['perplexity']:.2f}{src}")

    out_cols = ["label", "label_predicted", "correct", "perplexity"]
    if has_source:
        out_cols = ["label", "source", "label_predicted", "correct", "perplexity"]
    out_cols.append("text")
    df_valid["text"] = df_valid["text"].str[:80]   # skrócony podgląd
    df_valid[out_cols].to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    summary = {
        "optimal_perplexity_threshold": optimal_ppx,
        "auc":       round(roc_auc, 4),
        "accuracy":  round(acc, 4),
        "precision": round(prec, 4),
        "recall":    round(rec, 4),
        "f1":        round(f1, 4),
        "confusion_matrix": cm,
        "n_human":   int(n_human),
        "n_ai":      int(n_ai),
        "n_total":   len(df_valid),
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2, ensure_ascii=False)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

        ax1.plot(fpr, tpr, "b-", lw=2, label=f"AUC = {roc_auc:.3f}")
        ax1.plot([0, 1], [0, 1], "k--", lw=1)
        ax1.scatter(fpr[best_idx], tpr[best_idx], s=120,
                    color="red", zorder=5,
                    label=f"Youden threshold\n(ppx = {optimal_ppx:.2f})")
        ax1.set_xlabel("False Positive Rate")
        ax1.set_ylabel("True Positive Rate")
        ax1.set_title("Krzywa ROC – detekcja AI")
        ax1.legend(loc="lower right")
        ax1.grid(True, alpha=0.3)

        human_ppx = df_valid[df_valid["label"] == "human"]["perplexity"]
        ai_ppx    = df_valid[df_valid["label"] == "ai"]["perplexity"]
        bins = 20
        ax2.hist(human_ppx, bins=bins, alpha=0.6, color="steelblue",
                 label=f"Human (n={len(human_ppx)})", density=True)
        ax2.hist(ai_ppx, bins=bins, alpha=0.6, color="tomato",
                 label=f"AI (n={len(ai_ppx)})", density=True)
        ax2.axvline(optimal_ppx, color="black", linestyle="--", lw=2,
                    label=f"Próg = {optimal_ppx:.2f}")
        ax2.set_xlabel("Perplexity (Polish GPT-2)")
        ax2.set_ylabel("Gęstość")
        ax2.set_title("Rozkład perplexity – Human vs AI")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(OUTPUT_PLOT, dpi=150, bbox_inches="tight")
        print(f"\n  Wykres: {OUTPUT_PLOT}")

    except ImportError:
        print("\n  (matplotlib niedostępny – pomijam wykres)")

    print(f"  CSV:    {OUTPUT_CSV}")
    print(f"  JSON:   {OUTPUT_JSON}")
    print("\nGotowe!")
    print(f"\nAktualizuj progi w ai_detector.py:")
    print(f"  PERPLEXITY_AI_THRESHOLD    = {round(optimal_ppx * 0.78, 2)}")
    print(f"  PERPLEXITY_HUMAN_THRESHOLD = {optimal_ppx}")


if __name__ == "__main__":
    main()