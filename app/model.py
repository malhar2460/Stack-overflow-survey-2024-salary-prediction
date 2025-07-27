# backend/app/model.py

import mlflow
import dagshub
import os
from sklearn.pipeline import Pipeline

# --- DagsHub & MLflow Configuration ---
# These should be set as environment variables in production
DAGSHUB_REPO_OWNER = os.getenv("DAGSHUB_REPO_OWNER", "malhar.c.prajapati")
DAGSHUB_REPO_NAME = os.getenv("DAGSHUB_REPO_NAME", "Stack-overflow-survey-2024-salary-prediction")
MODEL_NAME = "stackoverflow-salary-predictor"
MODEL_STAGE = "Production"

# Initialize DagsHub integration to configure MLflow
print("Initializing DagsHub for model loading...")
dagshub.init(repo_owner=DAGSHUB_REPO_OWNER, repo_name=DAGSHUB_REPO_NAME, mlflow=True)
print("DagsHub initialized.")

# --- Global Model Variable ---
# This will hold the loaded model pipeline to avoid reloading on every request
model_pipeline: Pipeline = None

def load_model():
    """
    Loads the model from the MLflow Model Registry.
    This function is called once at application startup.
    """
    global model_pipeline
    if model_pipeline is None:
        try:
            model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"
            print(f"Loading model from URI: {model_uri}")
            model_pipeline = mlflow.sklearn.load_model(model_uri)
            print(f"✅ Successfully loaded model '{MODEL_NAME}' version/stage '{MODEL_STAGE}'")
        except Exception as e:
            print(f"🚨 Error loading model: {e}")
            # In a real application, you might want to handle this more gracefully
            # For now, we'll let it fail loudly if the model can't be loaded.
            raise

def get_model() -> Pipeline:
    """
    Returns the loaded model pipeline.
    Raises an exception if the model is not loaded.
    """
    if model_pipeline is None:
        # This case should ideally not be hit if startup event is configured correctly
        print("Model not loaded. Attempting to load now...")
        load_model()
    if model_pipeline is None:
        raise RuntimeError("Model could not be loaded.")
    return model_pipeline
