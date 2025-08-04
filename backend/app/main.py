import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any
from model import ModelService
from schemas import PredictionOutput, ModelSchema

# --- Application State ---
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load ML model
    print("INFO:     Loading ML model and preprocessor...")
    ml_models["salary_predictor"] = ModelService()
    print("INFO:     ML model and preprocessor loaded successfully.")
    yield
    # Shutdown: clear models
    print("INFO:     Clearing ML models...")
    ml_models.clear()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Stack Overflow Salary Predictor",
    description="A dynamic API to predict developer salaries using the best model from MLflow.",
    version="2.0.0",
    lifespan=lifespan
)

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Salary Predictor API"}

@app.get("/api/v1/model-schema")
def get_model_schema():
    """
    Returns the model input schema: mapping of feature names to their metadata
    (type, selection, values) for dynamic form rendering.
    """
    model_service = ml_models.get("salary_predictor")
    if model_service is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")

    # Directly return the full schema as loaded from artifacts
    return {"features": model_service.schema}

@app.post("/api/v1/predict", response_model=PredictionOutput)
def predict(payload: Dict[str, Any]):
    """
    Receives a JSON payload with feature values, constructs a DataFrame,
    and returns the salary prediction.
    """
    model_service = ml_models.get("salary_predictor")
    if model_service is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")

    try:
        input_df = pd.DataFrame([payload])
        input_df = input_df[model_service.feature_names]
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Missing feature in request: {e}. Required features: {model_service.feature_names}"
            )
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input data: {e}")

    try:
        prediction_value = model_service.predict(input_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

    return {"prediction": prediction_value}
