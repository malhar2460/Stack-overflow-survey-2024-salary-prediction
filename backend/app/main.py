import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any
from model import ModelService
from schemas import PredictionOutput, ModelSchema
from prep import YearsCodeConverter

# --- Application State ---
# This dictionary will hold our loaded model service.
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # This code runs when the application starts.
    print("INFO:     Loading ML model and preprocessor...")
    ml_models["salary_predictor"] = ModelService()
    print("INFO:     ML model and preprocessor loaded successfully.")
    yield
    # --- Shutdown ---
    # This code runs when the application stops.
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
# This allows the frontend (running on a different port) to communicate with the backend.
# Add the origins that your frontend is running on.
origins = [
    "http://localhost",
    "http://localhost:5173",  # Default SvelteKit dev port
    "http://127.0.0.1:5173",
    # Add your deployed frontend URL here for production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Salary Predictor API"}

@app.get("/api/v1/model-schema", response_model=ModelSchema)
def get_model_schema():
    """
    Endpoint to provide the required input schema for the currently loaded model.
    The frontend will use this to dynamically generate the input form.
    """
    if "salary_predictor" not in ml_models:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")
    
    model_service = ml_models["salary_predictor"]
    return {"features": model_service.feature_names}

@app.post("/api/v1/predict", response_model=PredictionOutput)
def predict(payload: Dict[str, Any]):
    """
    Receives a dynamic payload, preprocesses it, and returns a salary prediction.
    """
    if "salary_predictor" not in ml_models:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")

    model_service = ml_models["salary_predictor"]
    
    # Convert the dynamic payload into a DataFrame
    try:
        input_df = pd.DataFrame([payload])
        # Ensure column order matches what the model was trained on
        input_df = input_df[model_service.feature_names]
    except KeyError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing feature in payload: {e}. Required features are: {model_service.feature_names}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input data: {e}")

    # Get the prediction
    prediction = model_service.predict(input_df)
    
    return {"prediction": prediction}
