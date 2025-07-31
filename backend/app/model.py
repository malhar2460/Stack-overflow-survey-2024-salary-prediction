import mlflow
import dagshub
import pandas as pd
import joblib
import os
from typing import List
from prep import YearsCodeConverter
from prep import YearsCodeConverter
import joblib

class ModelService:
    """
    A service to find, load, and use the best ML model from MLflow.
    """
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.feature_names = None
        self._initialize_service()

    def _initialize_service(self):
        """
        Connects to DagsHub/MLflow and loads the best model and its artifacts.
        """
        try:
            dagshub.init(
                repo_owner='malhar.c.prajapati',
                repo_name='Stack-overflow-survey-2024-salary-prediction',
                mlflow=True
            )
            print("INFO:     Successfully connected to DagsHub/MLflow.")
        except Exception as e:
            print(f"ERROR:    Could not connect to DagsHub/MLflow: {e}")
            raise

        self.load_best_model_and_artifacts()

    def load_best_model_and_artifacts(self):
        """
        Finds the run with the best R2 score and loads its model and preprocessor.
        """
        print("INFO:     Searching for the best model in MLflow...")
        try:
            # Search all runs and order by R2 score descending
            runs = mlflow.search_runs(order_by=["metrics.r2 DESC"], max_results=1)
            if runs.empty:
                raise RuntimeError("No MLflow runs found.")

            best_run = runs.iloc[0]
            best_run_id = best_run.run_id
            print(f"INFO:     Found best model in run ID: {best_run_id} (R2 Score: {best_run['metrics.r2']:.4f})")

            # --- Load Model ---
            model_uri = f"runs:/{best_run_id}/model"
            self.model = mlflow.sklearn.load_model(model_uri)
            print("INFO:     Model loaded successfully.")

            # --- Load Preprocessor ---
            # Preprocessor is not an MLflow model, so we download it as an artifact
            local_preprocessor_path = "../../models/preprocessor1.pkl"
            with open(local_preprocessor_path, "rb") as f:
                self.preprocessor = joblib.load(f)

            print("INFO:     Preprocessor loaded successfully.")

            # --- Load Feature Names ---
            # This is crucial for the dynamic API. We expect the feature list
            # to be saved as an artifact during training.
            try:                
                features_path = os.path.join(os.path.dirname(__file__), "feature_names.txt")
                with open(features_path, "r") as f:
                    self.feature_names = [line.strip() for line in f if line.strip()]
                print(f"INFO:     Feature names loaded successfully: {self.feature_names}")
            except Exception:
                 # Fallback: try to infer from the preprocessor if the artifact is missing
                print("WARN:     'feature_names.txt' not found. Attempting to infer from preprocessor.")
                self.feature_names = self.preprocessor.feature_names_in_.tolist()
                print(f"INFO:     Inferred feature names: {self.feature_names}")


        except Exception as e:
            print(f"ERROR:    Failed to load model or artifacts from MLflow: {e}")
            raise

    def predict(self, data: pd.DataFrame) -> float:
        """
        Makes a salary prediction on new data.
        """
        if self.model is None or self.preprocessor is None:
            raise RuntimeError("Model and preprocessor are not loaded.")
        
        # Preprocess the data
        processed_data = self.preprocessor.transform(data)
        
        # Make prediction
        prediction = self.model.predict(processed_data)
        
        return float(prediction[0])

