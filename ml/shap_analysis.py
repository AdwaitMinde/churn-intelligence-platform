import pandas as pd
import mlflow
import mlflow.xgboost
import shap
import matplotlib.pyplot as plt

mlflow.set_tracking_uri("http://localhost:5000")

# Load the registered model
model = mlflow.xgboost.load_model("models:/churn_model/1")

# Load test data
X_test = pd.read_csv('C:/churn-intelligence-platform/ml/X_test.csv')

# Compute SHAP values
print("Computing SHAP values...")
explainer   = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Print mean absolute SHAP value per feature (feature importance)
shap_importance = pd.DataFrame({
    'feature':    X_test.columns,
    'importance': abs(shap_values).mean(axis=0)
}).sort_values('importance', ascending=False)

print("\nFeature Importance (mean |SHAP value|):")
print(shap_importance.to_string(index=False))

# Save summary plot
shap.summary_plot(shap_values, X_test, show=False)
plt.tight_layout()
plt.savefig('C:/churn-intelligence-platform/ml/shap_summary.png', dpi=150, bbox_inches='tight')
print("\nSHAP summary plot saved to ml/shap_summary.png")