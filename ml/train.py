import pandas as pd
import mlflow
import mlflow.xgboost
import xgboost as xgb
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score,
    recall_score, confusion_matrix
)

# Load train/test splits
X_train = pd.read_csv('C:/churn-intelligence-platform/ml/X_train.csv')
X_test  = pd.read_csv('C:/churn-intelligence-platform/ml/X_test.csv')
y_train = pd.read_csv('C:/churn-intelligence-platform/ml/y_train.csv').squeeze()
y_test  = pd.read_csv('C:/churn-intelligence-platform/ml/y_test.csv').squeeze()

# Class imbalance ratio for scale_pos_weight
neg = (y_train == 0).sum()
pos = (y_train == 1).sum()
scale_pos_weight = neg / pos
print(f"scale_pos_weight: {scale_pos_weight:.2f} ({neg} non-churn / {pos} churn)")

# MLflow tracking server
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("churn-prediction")

# --- Experiment 1: Baseline ---
params_1 = {
    "max_depth": 4,
    "n_estimators": 100,
    "learning_rate": 0.1,
    "scale_pos_weight": scale_pos_weight,
    "random_state": 42,
    "eval_metric": "auc"
}

with mlflow.start_run(run_name="baseline"):
    model = xgb.XGBClassifier(**params_1)
    model.fit(X_train, y_train)
    preds      = model.predict(X_test)
    preds_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "roc_auc":   roc_auc_score(y_test, preds_prob),
        "f1":        f1_score(y_test, preds),
        "precision": precision_score(y_test, preds),
        "recall":    recall_score(y_test, preds),
    }
    mlflow.log_params(params_1)
    mlflow.log_metrics(metrics)
    mlflow.xgboost.log_model(model, "model")
    print(f"Baseline    → AUC: {metrics['roc_auc']:.4f} | F1: {metrics['f1']:.4f} | Recall: {metrics['recall']:.4f}")

# --- Experiment 2: Deeper trees ---
params_2 = {
    "max_depth": 6,
    "n_estimators": 200,
    "learning_rate": 0.05,
    "scale_pos_weight": scale_pos_weight,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "eval_metric": "auc"
}

with mlflow.start_run(run_name="deeper-trees"):
    model = xgb.XGBClassifier(**params_2)
    model.fit(X_train, y_train)
    preds      = model.predict(X_test)
    preds_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "roc_auc":   roc_auc_score(y_test, preds_prob),
        "f1":        f1_score(y_test, preds),
        "precision": precision_score(y_test, preds),
        "recall":    recall_score(y_test, preds),
    }
    mlflow.log_params(params_2)
    mlflow.log_metrics(metrics)
    mlflow.xgboost.log_model(model, "model")
    print(f"Deeper trees → AUC: {metrics['roc_auc']:.4f} | F1: {metrics['f1']:.4f} | Recall: {metrics['recall']:.4f}")

# --- Experiment 3: High recall focus ---
params_3 = {
    "max_depth": 5,
    "n_estimators": 300,
    "learning_rate": 0.03,
    "scale_pos_weight": scale_pos_weight * 1.5,  # push even harder on minority class
    "subsample": 0.7,
    "colsample_bytree": 0.7,
    "min_child_weight": 5,
    "random_state": 42,
    "eval_metric": "auc"
}

with mlflow.start_run(run_name="high-recall"):
    model = xgb.XGBClassifier(**params_3)
    model.fit(X_train, y_train)
    preds      = model.predict(X_test)
    preds_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "roc_auc":   roc_auc_score(y_test, preds_prob),
        "f1":        f1_score(y_test, preds),
        "precision": precision_score(y_test, preds),
        "recall":    recall_score(y_test, preds),
    }
    mlflow.log_params(params_3)
    mlflow.log_metrics(metrics)
    mlflow.xgboost.log_model(model, "model")
    print(f"High recall  → AUC: {metrics['roc_auc']:.4f} | F1: {metrics['f1']:.4f} | Recall: {metrics['recall']:.4f}")

print("\nAll experiments logged. Check MLflow UI at http://localhost:5000")