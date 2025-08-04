import mlflow
import dagshub
import pandas as pd
import joblib
import os
import json
import sys
import prep
from typing import List, Dict, Any
from mlflow.tracking import MlflowClient
from sklearn.base import BaseEstimator, TransformerMixin


class YearsCodeConverter(BaseEstimator, TransformerMixin):
    """
    Converts experience strings like "Less than 1 year" or "More than 50 years"
    into numeric floats, and casts other values to numeric.
    """
    def __init__(self):
        self.special_map = {
            "Less than 1 year": 0.5,
            "More than 50 years": 51
        }

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        for col in X_copy.columns:
            if X_copy[col].dtype == object:
                X_copy[col] = X_copy[col].replace(self.special_map)
            X_copy[col] = pd.to_numeric(X_copy[col], errors='coerce')
        return X_copy

    def get_feature_names_out(self, input_features=None):
        return input_features


# Inject YearsCodeConverter into __main__ module for unpickling compatibility
sys.modules['__main__'].YearsCodeConverter = YearsCodeConverter

# Also register into prep namespace
prep.YearsCodeConverter = YearsCodeConverter


class ModelService:
    """
    A service to find, load, and use the best ML model from MLflow.
    Loads preprocessor, feature names, and input schema from artifacts.
    """

    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.feature_names: List[str] = []
        self.schema: Dict[str, Any] = {}
        self._initialize_service()

    def _initialize_service(self):
        try:
            dagshub.init(
                repo_owner='malhar.c.prajapati',
                repo_name='Stack-overflow-survey-2024-salary-prediction',
                mlflow=True
            )
            print("INFO: Successfully connected to DagsHub/MLflow.")
        except Exception as e:
            print(f"ERROR: Could not connect to DagsHub/MLflow: {e}")
            raise

        self.load_best_model_and_artifacts()

    def load_best_model_and_artifacts(self):
        print("INFO:     Loading ML model and artifacts...")
        try:
            # Find the best MLflow run by R2
            runs = mlflow.search_runs(order_by=["metrics.r2 DESC"], max_results=1)
            if runs.empty:
                raise RuntimeError("No MLflow runs found.")

            best_run = runs.iloc[0]
            run_id = best_run.run_id
            print(f"INFO:     Found best run ID: {run_id} (R2: {best_run['metrics.r2']:.4f})")

            # Load the sklearn model from MLflow
            model_uri = f"runs:/{run_id}/model"
            self.model = mlflow.sklearn.load_model(model_uri)
            print("INFO:     Model loaded successfully.")

            # Use MlflowClient to fetch artifacts
            client = MlflowClient()

            # Fetch and load preprocessor
            print("INFO:     Downloading preprocessor artifact...")
            preproc_file = client.download_artifacts(run_id, "preprocessor/preprocessor.pkl")
            if not os.path.exists(preproc_file):
                raise FileNotFoundError(f"Preprocessor file not found: {preproc_file}")
            with open(preproc_file, "rb") as f:
                self.preprocessor = joblib.load(f)
            print("INFO:     Preprocessor loaded successfully.")

            # Fetch and load input schema
            print("INFO:     Downloading input schema artifact...")
            schema_file = client.download_artifacts(run_id, "input_schema/cat_domains.json")
            if not os.path.exists(schema_file):
                raise FileNotFoundError(f"Schema file not found: {schema_file}")
            with open(schema_file, "r") as f:
                self.schema = json.load(f)
            print("INFO:     Schema loaded successfully.")

            # Store feature names
            self.feature_names = list(self.schema.keys())
            print(f"INFO:     Feature names: {self.feature_names}")

        except Exception as e:
            print(f"ERROR:    Failed to load model or artifacts: {e}")
            raise

    def predict(self, data: pd.DataFrame) -> float:
        if self.model is None or self.preprocessor is None:
            raise RuntimeError("Model or preprocessor not loaded.")

        # Apply preprocessing and predict
        data_converted = YearsCodeConverter().transform(data)
        processed = self.preprocessor.transform(data_converted)
        prediction = self.model.predict(processed)
        return float(prediction[0])
