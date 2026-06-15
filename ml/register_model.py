import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://localhost:5000")
client = MlflowClient()

# Get the deeper-trees run
runs = client.search_runs(
    experiment_ids=["1"],
    filter_string="tags.mlflow.runName = 'deeper-trees'",
    order_by=["metrics.roc_auc DESC"],
    max_results=1
)

best_run = runs[0]
run_id = best_run.info.run_id
auc = best_run.data.metrics["roc_auc"]
print(f"Best run: {run_id} | AUC: {auc:.4f}")

# Register model
model_uri = f"runs:/{run_id}/model"
mv = mlflow.register_model(model_uri, "churn_model")
print(f"Registered model version: {mv.version}")