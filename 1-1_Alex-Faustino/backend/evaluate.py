#!/usr/bin/env python3
"""
Evaluate churn model on a test set, save metrics and plots.

Usage:
  python evaluate.py --model backend/models/churn_model.pkl --data backend/data/Telco-Customer-Churn.csv --out backend/models

If --test is provided, it must be a CSV with same schema including 'Churn' column.
If --test is not provided, the script will split `--data` into train/test (80/20) using random_state.

Outputs saved to --out directory:
  - metrics.txt (human readable)
  - metrics.json (machine readable)
  - roc.png, pr.png, confusion.png

The script also computes a recommended threshold that maximizes F1 on the test set.
"""

import argparse
import json
import os
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    precision_recall_fscore_support,
    roc_curve,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean common issues in the Telco dataset before evaluation.

    - Convert `TotalCharges` which may contain blank strings to numeric and impute median.
    - Strip whitespace in string columns.
    """
    df = df.copy()

    # strip whitespace-only strings across object columns
    for c in df.select_dtypes(include=['object']).columns:
        df[c] = df[c].apply(lambda x: x.strip() if isinstance(x, str) else x)

    if 'TotalCharges' in df.columns:
        # replace empty strings with NaN, then convert
        df['TotalCharges'] = df['TotalCharges'].replace(r'^\s*$', np.nan, regex=True)
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        med = df['TotalCharges'].median()
        if np.isnan(med):
            med = 0.0
        df['TotalCharges'] = df['TotalCharges'].fillna(med)

    return df


def get_features_labels(df: pd.DataFrame):
    # Expect column 'Churn' as target with values 'Yes'/'No'
    if 'Churn' not in df.columns:
        raise ValueError("Input data must contain 'Churn' column with values 'Yes'/'No'.")

    y = df['Churn'].map({'Yes': 1, 'No': 0})

    # drop obvious non-feature columns
    X = df.drop(columns=[c for c in ['customerID', 'Churn'] if c in df.columns])
    return X, y


def choose_threshold_by_f1(y_true, y_prob):
    best_t = 0.5
    best_f1 = -1.0
    thresholds = np.linspace(0.0, 1.0, 101)
    for t in thresholds:
        preds = (y_prob >= t).astype(int)
        _, _, f1, _ = precision_recall_fscore_support(y_true, preds, average='binary', zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_t = t
    return best_t, best_f1


def save_metrics_txt(path: Path, summary: str):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(summary)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', required=True)
    p.add_argument('--data', required=True, help='CSV with full dataset (contains Churn)')
    p.add_argument('--test', help='Optional CSV for test set (contains Churn)')
    p.add_argument('--out', default='backend/models')
    p.add_argument('--random-state', type=int, default=42)
    args = p.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print('Loading model...', args.model)
    model = joblib.load(args.model)

    if args.test:
        print('Loading test data...', args.test)
        test_df = load_data(args.test)
        test_df = clean_dataframe(test_df)
    else:
        print('Loading full data and splitting...', args.data)
        full = load_data(args.data)
        full = clean_dataframe(full)
        _, test_df = train_test_split(full, test_size=0.2, random_state=args.random_state, stratify=full['Churn'])

    X_test, y_test = get_features_labels(test_df)

    # attempt prediction
    try:
        probs = model.predict_proba(X_test)[:, 1]
    except Exception as e:
        # try passing DataFrame as-is; if fails, inform user
        raise RuntimeError(f'Could not call predict_proba on model: {e}')

    roc_auc = roc_auc_score(y_test, probs)
    pr_auc = average_precision_score(y_test, probs)

    # choose threshold by F1
    best_t, best_f1 = choose_threshold_by_f1(y_test, probs)
    preds_best = (probs >= best_t).astype(int)

    precision, recall, f1, support = precision_recall_fscore_support(y_test, preds_best, average=None, labels=[0,1], zero_division=0)
    # per-class: order [0,1]

    cm = confusion_matrix(y_test, preds_best)

    # save metrics.json
    metrics_json = {
        'roc_auc': float(roc_auc),
        'pr_auc': float(pr_auc),
        'best_threshold': float(best_t),
        'best_f1': float(best_f1),
        'precision_by_class': [float(precision[0]), float(precision[1])],
        'recall_by_class': [float(recall[0]), float(recall[1])],
        'f1_by_class': [float(f1[0]), float(f1[1])],
        'support_by_class': [int(support[0]), int(support[1])],
        'confusion_matrix': cm.tolist(),
        'n_test': int(len(y_test)),
    }

    with open(out_dir / 'metrics.json', 'w', encoding='utf-8') as f:
        json.dump(metrics_json, f, indent=2)

    # human readable summary
    summary = []
    summary.append('Evaluation results')
    summary.append('==================')
    summary.append(f"n_test: {len(y_test)}")
    summary.append(f"ROC AUC: {roc_auc:.4f}")
    summary.append(f"PR AUC: {pr_auc:.4f}")
    summary.append('')
    summary.append('Per-class metrics (class 0 = No churn, class 1 = Churn):')
    summary.append(f"Precision: class0={precision[0]:.4f}, class1={precision[1]:.4f}")
    summary.append(f"Recall:    class0={recall[0]:.4f}, class1={recall[1]:.4f}")
    summary.append(f"F1:        class0={f1[0]:.4f}, class1={f1[1]:.4f}")
    summary.append(f"Support:   class0={support[0]}, class1={support[1]}")
    summary.append('')
    summary.append('Confusion matrix (rows=true, cols=pred):')
    summary.append(str(cm.tolist()))
    summary.append('')
    summary.append(f"Best threshold (max F1): {best_t:.3f} with F1={best_f1:.4f}")
    summary.append('')
    summary_text = '\n'.join(summary)

    save_metrics_txt(out_dir / 'metrics.txt', summary_text)

    print('Saved metrics to', out_dir)

    # plots
    fpr, tpr, _ = roc_curve(y_test, probs)
    plt.figure()
    plt.plot(fpr, tpr, label=f'ROC AUC = {roc_auc:.4f}')
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.4)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_dir / 'roc.png')
    plt.close()

    precision_vals, recall_vals, _ = precision_recall_curve(y_test, probs)
    plt.figure()
    plt.plot(recall_vals, precision_vals, label=f'PR AUC = {pr_auc:.4f}')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend(loc='lower left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_dir / 'pr.png')
    plt.close()

    # confusion matrix plot
    plt.figure()
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion matrix')
    plt.colorbar()
    tick_marks = np.arange(2)
    plt.xticks(tick_marks, ['No', 'Yes'])
    plt.yticks(tick_marks, ['No', 'Yes'])
    fmt = 'd'
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], fmt), horizontalalignment='center', color='white' if cm[i, j] > thresh else 'black')
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.savefig(out_dir / 'confusion.png')
    plt.close()

    print('Saved plots to', out_dir)


if __name__ == '__main__':
    main()
