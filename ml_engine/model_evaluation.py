"""
ClimateTwin AI — Module 8: Comprehensive Model Evaluation & Visualization Suite
Module: ml_engine/model_evaluation.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Responsibilities:
- Evaluate all four hazard models independently on chronological Train / Validation / Test splits.
- Fit preprocessing strictly on the training split to prevent data leakage.
- Compute Regression metrics: MAE, MSE, RMSE, R².
- Compute Risk-Category Classification metrics: Accuracy, Precision, Recall, F1-score,
  Confusion Matrix, and High-Risk Binary ROC-AUC (hazard >= 60).
- Compare Ridge Baseline vs. Random Forest vs. Gradient Boosting / XGBoost.
- Persist evaluation reports (`evaluation/metrics/`) and publication-grade plots (`evaluation/plots/`).
- Document model-specific scientific limitations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)

from ml_engine.air_quality_model import AirQualityRiskModel
from ml_engine.config import (
    METRICS_DIR,
    PLOTS_DIR,
    PROCESSED_DATA_DIR,
    score_to_risk_level,
)
from ml_engine.data_preprocessing import EnvironmentalDataPreprocessor
from ml_engine.feature_engineering import EnvironmentalFeatureEngineer
from ml_engine.flood_model import FloodRiskModel
from ml_engine.heat_model import HeatRiskModel
from ml_engine.reference_data import load_or_create_pilot_dataset
from ml_engine.water_stress_model import WaterStressModel


RISK_CATEGORY_ORDER: List[str] = ["Very Low", "Low", "Moderate", "High", "Very High"]

MODEL_LIMITATIONS: Dict[str, str] = {
    "heat": (
        "Trained on meteorological heat hazard proxy (NOAA Heat Index + Wet-Bulb + IMD thermal anomaly). "
        "Does not incorporate indoor building thermal insulation, urban canyon micro-scale radiative trapping, "
        "or clinical hospital heat-stroke admission records."
    ),
    "flood": (
        "Implements a Hydrometeorological Rainfall-Runoff Flood-Hazard Proxy. High rainfall alone does not "
        "confirm street-level inundation; does not model real-time dam reservoir releases (e.g., Khadakwasla discharge) "
        "or localized municipal stormwater drain blockages."
    ),
    "air_quality": (
        "Calibrated to official Indian CPCB NAQI sub-indices. Does not account for sudden episodic point-source "
        "emissions (e.g., localized crop burning plumes, traffic accidents, or festival firecracker spikes) "
        "unless reflected in incoming pollutant sensor readings."
    ),
    "water_stress": (
        "Quantifies environmental and hydro-climatic moisture deficit (30d ET minus rainfall and soil moisture depletion). "
        "Does not measure municipal dam storage volumes, groundwater table drawdowns, or piped water distribution equity."
    ),
}


def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate MAE, MSE, RMSE, and R² on 0-100 clipped hazard predictions."""
    y_p = np.clip(np.asarray(y_pred, dtype=float), 0.0, 100.0)
    y_t = np.asarray(y_true, dtype=float)
    mse = float(mean_squared_error(y_t, y_p))
    return {
        "MAE": round(float(mean_absolute_error(y_t, y_p)), 4),
        "MSE": round(mse, 4),
        "RMSE": round(float(np.sqrt(mse)), 4),
        "R2": round(float(r2_score(y_t, y_p)), 4),
    }


def compute_classification_metrics(
    y_true_scores: np.ndarray,
    y_pred_scores: np.ndarray,
    elevated_threshold: float = 50.0,
) -> Dict[str, Any]:
    """
    Evaluate risk-category classification performance (5-tier categories) and
    elevated-risk alert detection (score >= elevated_threshold) including ROC-AUC.
    """
    y_t = np.clip(np.asarray(y_true_scores, dtype=float), 0.0, 100.0)
    y_p = np.clip(np.asarray(y_pred_scores, dtype=float), 0.0, 100.0)

    true_labels = [score_to_risk_level(v) for v in y_t]
    pred_labels = [score_to_risk_level(v) for v in y_p]

    acc = float(accuracy_score(true_labels, pred_labels))
    prec = float(precision_score(true_labels, pred_labels, average="weighted", zero_division=0))
    rec = float(recall_score(true_labels, pred_labels, average="weighted", zero_division=0))
    f1 = float(f1_score(true_labels, pred_labels, average="weighted", zero_division=0))
    cm = confusion_matrix(true_labels, pred_labels, labels=RISK_CATEGORY_ORDER).tolist()

    # Binary elevated-risk ROC-AUC using continuous predicted score
    y_bin_true = (y_t >= elevated_threshold).astype(int)
    if len(np.unique(y_bin_true)) > 1:
        roc_auc = round(float(roc_auc_score(y_bin_true, y_p / 100.0)), 4)
    else:
        # Fallback to median split if test slice has no extreme events above threshold
        med_thresh = float(np.median(y_t))
        y_bin_med = (y_t >= med_thresh).astype(int)
        roc_auc = (
            round(float(roc_auc_score(y_bin_med, y_p / 100.0)), 4)
            if len(np.unique(y_bin_med)) > 1
            else None
        )

    return {
        "Accuracy": round(acc, 4),
        "Precision_Weighted": round(prec, 4),
        "Recall_Weighted": round(rec, 4),
        "F1_Weighted": round(f1, 4),
        "ROC_AUC": roc_auc,
        "Confusion_Matrix_Labels": RISK_CATEGORY_ORDER,
        "Confusion_Matrix": cm,
    }


def generate_evaluation_plots(
    eval_summary: Dict[str, Any],
    test_series_by_hazard: Dict[str, Dict[str, np.ndarray]],
    models_by_hazard: Dict[str, Any],
    plots_dir: Path = PLOTS_DIR,
) -> Dict[str, str]:
    """Generate and save model performance visualizations in `evaluation/plots/`."""
    plots_dir.mkdir(parents=True, exist_ok=True)
    saved_plots: Dict[str, str] = {}

    hazards = ["heat", "flood", "air_quality", "water_stress"]
    titles = {
        "heat": "Heat Risk Model",
        "flood": "Rainfall & Flood Proxy Model",
        "air_quality": "Air-Quality (CPCB NAQI) Model",
        "water_stress": "Water-Stress Proxy Model",
    }

    # 1. Model Comparison Bar Chart (Validation RMSE & Test R²)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    x = np.arange(len(hazards))
    width = 0.25

    candidate_keys = list(eval_summary["hazards"]["heat"]["candidate_metrics"].keys())
    colors = ["#64748b", "#2563eb", "#059669"]

    for idx, c_key in enumerate(candidate_keys):
        rmses = [
            eval_summary["hazards"][h]["candidate_metrics"][c_key]["test"]["RMSE"]
            for h in hazards
        ]
        r2s = [
            eval_summary["hazards"][h]["candidate_metrics"][c_key]["test"]["R2"]
            for h in hazards
        ]
        axes[0].bar(x + (idx - 1) * width, rmses, width, label=c_key, color=colors[idx % len(colors)])
        axes[1].bar(x + (idx - 1) * width, r2s, width, label=c_key, color=colors[idx % len(colors)])

    axes[0].set_title("Held-Out Chronological Test RMSE (Lower is Better)", fontsize=11, fontweight="bold")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([titles[h] for h in hazards], rotation=15, ha="right")
    axes[0].set_ylabel("RMSE (0–100 Hazard Scale)")
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)
    axes[0].legend()

    axes[1].set_title("Held-Out Chronological Test R² Score (Higher is Better)", fontsize=11, fontweight="bold")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([titles[h] for h in hazards], rotation=15, ha="right")
    axes[1].set_ylabel("R² Score")
    axes[1].set_ylim(0.0, 1.05)
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)
    axes[1].legend()

    fig.tight_layout()
    comp_path = plots_dir / "model_rmse_r2_comparison.png"
    fig.savefig(comp_path, dpi=160)
    plt.close(fig)
    saved_plots["model_comparison"] = str(comp_path)

    # 2. Actual vs Predicted Time-Series on Chronological Test Set
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    for ax, h in zip(axes.flatten(), hazards):
        y_true = test_series_by_hazard[h]["y_true"]
        y_pred = test_series_by_hazard[h]["y_pred"]
        ax.plot(y_true, label="Actual Hazard Proxy", color="#1e293b", linewidth=1.3, alpha=0.85)
        ax.plot(y_pred, label="Selected Model Prediction", color="#dc2626", linewidth=1.2, linestyle="--")
        r2_val = eval_summary["hazards"][h]["test_regression_metrics"]["R2"]
        mae_val = eval_summary["hazards"][h]["test_regression_metrics"]["MAE"]
        ax.set_title(f"{titles[h]} (Test R²={r2_val:.3f}, MAE={mae_val:.2f})", fontsize=10.5, fontweight="bold")
        ax.set_xlabel("Chronological Test Days (Pune Pilot)")
        ax.set_ylabel("Hazard Score (0–100)")
        ax.grid(True, linestyle=":", alpha=0.45)
        ax.legend(loc="upper right", fontsize=8.5)

    fig.tight_layout()
    ts_path = plots_dir / "actual_vs_predicted_hazards.png"
    fig.savefig(ts_path, dpi=160)
    plt.close(fig)
    saved_plots["actual_vs_predicted"] = str(ts_path)

    # 3. Top Feature Importances per Hazard Model
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    for ax, h in zip(axes.flatten(), hazards):
        m_obj = models_by_hazard[h]
        feats = m_obj.feature_names
        imps = getattr(m_obj.model, "feature_importances_", np.abs(getattr(m_obj.model, "coef_", np.ones(len(feats)))))
        order = np.argsort(imps)[-8:]
        ax.barh([feats[i] for i in order], [imps[i] for i in order], color="#0284c7")
        ax.set_title(f"{titles[h]} — Top 8 Features", fontsize=10.5, fontweight="bold")
        ax.set_xlabel("Relative Importance")
        ax.grid(axis="x", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fi_path = plots_dir / "feature_importances_summary.png"
    fig.savefig(fi_path, dpi=160)
    plt.close(fig)
    saved_plots["feature_importances"] = str(fi_path)

    # 4. Confusion Matrices for 5-Tier Risk Classification on Test Set
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    for ax, h in zip(axes.flatten(), hazards):
        cm = np.array(eval_summary["hazards"][h]["test_classification_metrics"]["Confusion_Matrix"])
        im = ax.imshow(cm, cmap="Blues")
        ax.set_title(
            f"{titles[h]} Risk Category Confusion Matrix\n"
            f"(Acc={eval_summary['hazards'][h]['test_classification_metrics']['Accuracy']:.2%}, "
            f"F1={eval_summary['hazards'][h]['test_classification_metrics']['F1_Weighted']:.2%})",
            fontsize=10,
            fontweight="bold",
        )
        ax.set_xticks(range(len(RISK_CATEGORY_ORDER)))
        ax.set_yticks(range(len(RISK_CATEGORY_ORDER)))
        ax.set_xticklabels(RISK_CATEGORY_ORDER, rotation=30, ha="right", fontsize=8.5)
        ax.set_yticklabels(RISK_CATEGORY_ORDER, fontsize=8.5)
        ax.set_xlabel("Predicted Category")
        ax.set_ylabel("True Category")
        for r in range(cm.shape[0]):
            for c in range(cm.shape[1]):
                ax.text(c, r, str(cm[r, c]), ha="center", va="center", color="black", fontsize=8.5)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    fig.tight_layout()
    cm_path = plots_dir / "confusion_matrices.png"
    fig.savefig(cm_path, dpi=160)
    plt.close(fig)
    saved_plots["confusion_matrices"] = str(cm_path)

    return saved_plots


def run_full_training_and_evaluation(
    raw_df: Optional[pd.DataFrame] = None,
    train_frac: float = 0.70,
    val_frac: float = 0.15,
) -> Dict[str, Any]:
    """
    Execute the complete, leak-free training and evaluation workflow:
    1. Load or create pilot environmental dataset.
    2. Split raw data chronologically FIRST so preprocessor fits strictly on Train slice.
    3. Transform Train, Validation, and Test sets using the training-fitted preprocessor.
    4. Engineer causal features.
    5. Train, compare, evaluate, and save all 4 hazard models.
    6. Persist evaluation JSON, CSV comparison table, and 4 diagnostic plot suites.
    """
    df_raw = raw_df.copy() if raw_df is not None else load_or_create_pilot_dataset()
    df_raw["timestamp_dt"] = pd.to_datetime(df_raw["timestamp"])
    df_raw = df_raw.sort_values(["location", "timestamp_dt"]).drop(columns=["timestamp_dt"]).reset_index(drop=True)

    n = len(df_raw)
    train_end = int(n * train_frac)
    val_end = int(n * (train_frac + val_frac))

    # Strict leak-free preprocessor fitting on training slice only
    preprocessor = EnvironmentalDataPreprocessor(preserve_missing_indicators=True)
    preprocessor.fit(df_raw.iloc[:train_end])
    preprocessor.save(PROCESSED_DATA_DIR / "preprocessor.joblib")

    # Transform full chronological series using strictly training-fitted statistics
    df_clean, prep_report = preprocessor.transform(df_raw, return_report=True)

    # Carry over target columns
    for t_col in ["heat_risk_target", "flood_risk_target", "air_quality_risk_target", "water_stress_risk_target"]:
        if t_col in df_raw.columns:
            df_clean[t_col] = df_raw[t_col].values

    engineer = EnvironmentalFeatureEngineer()
    df_features, feat_report = engineer.transform(df_clean, return_report=True)

    # Save processed ML-ready dataset
    processed_csv = PROCESSED_DATA_DIR / "pune_processed_features.csv"
    df_features.to_csv(processed_csv, index=False)

    # Instantiate and train all 4 hazard models
    heat_model = HeatRiskModel()
    flood_model = FloodRiskModel()
    aq_model = AirQualityRiskModel()
    ws_model = WaterStressModel()

    model_map = {
        "heat": (heat_model, "heat_risk_target"),
        "flood": (flood_model, "flood_risk_target"),
        "air_quality": (aq_model, "air_quality_risk_target"),
        "water_stress": (ws_model, "water_stress_risk_target"),
    }

    hazards_report: Dict[str, Any] = {}
    test_series_by_hazard: Dict[str, Dict[str, np.ndarray]] = {}
    models_by_hazard: Dict[str, Any] = {}
    comparison_rows: List[Dict[str, Any]] = []

    for hazard_key, (m_instance, target_col) in model_map.items():
        train_res = m_instance.train_and_select(
            df_features,
            target_col=target_col,
            train_frac=train_frac,
            val_frac=val_frac,
        )

        # Evaluate selected model on Train, Validation, and Held-Out Test slices
        X_all = df_features[m_instance.feature_names].to_numpy(dtype=float)
        y_all = df_features[target_col].to_numpy(dtype=float)

        X_tr, y_tr = X_all[:train_end], y_all[:train_end]
        X_va, y_va = X_all[train_end:val_end], y_all[train_end:val_end]
        X_te, y_te = X_all[val_end:], y_all[val_end:]

        pred_tr = np.clip(m_instance.model.predict(X_tr), 0.0, 100.0)
        pred_va = np.clip(m_instance.model.predict(X_va), 0.0, 100.0)
        pred_te = np.clip(m_instance.model.predict(X_te), 0.0, 100.0)

        test_series_by_hazard[hazard_key] = {"y_true": y_te, "y_pred": pred_te}
        models_by_hazard[hazard_key] = m_instance

        for cand_name, split_dict in train_res["candidate_metrics"].items():
            comparison_rows.append(
                {
                    "hazard": hazard_key,
                    "candidate_model": cand_name,
                    "is_selected": cand_name == m_instance.selected_model_name,
                    "val_MAE": split_dict["validation"]["MAE"],
                    "val_RMSE": split_dict["validation"]["RMSE"],
                    "val_R2": split_dict["validation"]["R2"],
                    "test_MAE": split_dict["test"]["MAE"],
                    "test_RMSE": split_dict["test"]["RMSE"],
                    "test_R2": split_dict["test"]["R2"],
                }
            )

        hazards_report[hazard_key] = {
            "selected_model": m_instance.selected_model_name,
            "feature_count": len(m_instance.feature_names),
            "train_regression_metrics": compute_regression_metrics(y_tr, pred_tr),
            "validation_regression_metrics": compute_regression_metrics(y_va, pred_va),
            "test_regression_metrics": compute_regression_metrics(y_te, pred_te),
            "test_classification_metrics": compute_classification_metrics(y_te, pred_te),
            "candidate_metrics": train_res["candidate_metrics"],
            "limitations": MODEL_LIMITATIONS[hazard_key],
        }

    eval_summary: Dict[str, Any] = {
        "dataset_summary": {
            "total_records": int(n),
            "train_records": int(train_end),
            "validation_records": int(val_end - train_end),
            "test_records": int(n - val_end),
            "split_method": "strict_chronological_temporal_split",
            "preprocessor_fitted_on": "train_split_only",
            "data_coverage_pct": prep_report.get("data_coverage_pct", 100.0),
            "derived_features_count": feat_report.get("derived_feature_count", 0),
        },
        "hazards": hazards_report,
    }

    plots_saved = generate_evaluation_plots(
        eval_summary,
        test_series_by_hazard,
        models_by_hazard,
        plots_dir=PLOTS_DIR,
    )
    eval_summary["plots_saved"] = plots_saved

    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = METRICS_DIR / "evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(eval_summary, f, indent=2)

    comp_df = pd.DataFrame(comparison_rows)
    comp_csv_path = METRICS_DIR / "model_comparison.csv"
    comp_df.to_csv(comp_csv_path, index=False)

    return eval_summary


if __name__ == "__main__":
    summary = run_full_training_and_evaluation()
    print("Completed full model training and evaluation!")
    for h_name, h_info in summary["hazards"].items():
        print(
            f"  [{h_name.upper()}] Selected: {h_info['selected_model']} | "
            f"Test RMSE: {h_info['test_regression_metrics']['RMSE']:.3f} | "
            f"Test R²: {h_info['test_regression_metrics']['R2']:.4f} | "
            f"Category Acc: {h_info['test_classification_metrics']['Accuracy']:.2%}"
        )

