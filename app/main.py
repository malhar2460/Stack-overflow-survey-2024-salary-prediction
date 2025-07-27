# backend/app/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pandas as pd
import numpy as np
import os
from typing import Dict

# Import from our application modules
from .schemas import DeveloperProfile, PredictionResponse
from .model import get_model, load_model
from sklearn.pipeline import Pipeline

# Initialize the FastAPI app
app = FastAPI(
    title="Stack Overflow Salary Predictor",
    description="An API to predict developer salaries based on the 2024 Stack Overflow survey.",
    version="1.0.0"
)

# --- CORS Configuration ---
# Allows the frontend (running on a different domain) to communicate with the backend.
origins = [
    "http://localhost:5173",  # SvelteKit default dev server
    "http://localhost:3000",  # Common alternative
    # Add your Vercel deployment URL here once you have it
    # e.g., "https://your-project-name.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Application Startup Event ---
@app.on_event("startup")
async def startup_event():
    """
    Load the machine learning model when the application starts.
    """
    print("Application startup: Loading ML model...")
    load_model()
    print("Application startup complete.")

# --- API Routes ---
@app.get("/api/health", tags=["General"])
def read_root() -> Dict[str, str]:
    """
    Health check endpoint.
    """
    return {"status": "ok", "message": "Welcome to the Salary Prediction API"}

@app.post("/api/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_salary(
    profile: DeveloperProfile,
    model: Pipeline = Depends(get_model)
) -> PredictionResponse:
    """
    Predicts the annual salary based on a developer's profile.

    - **profile**: Input data containing developer attributes.
    - **Returns**: A JSON object with the predicted salary.
    """
    try:
        # Convert the Pydantic model to a pandas DataFrame
        # The model pipeline expects a DataFrame with specific column names
        profile_df = pd.DataFrame([profile.dict()])

        # Make the prediction
        # The pipeline handles all preprocessing internally
        log_prediction = model.predict(profile_df)

        # The model predicts the log of the salary, so we need to convert it back
        # using np.expm1 which calculates exp(x) - 1
        # The result is a numpy array, so we get the first element.
        prediction = np.expm1(log_prediction[0])

        return PredictionResponse(predicted_salary_usd=prediction)

    except Exception as e:
        # This will catch errors during prediction
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {str(e)}")

# --- Mount Static Files (For Docker deployment) ---
# This serves the built SvelteKit frontend from the backend.
# It must come AFTER all other API routes.
# The path for the static directory is relative to the root where uvicorn is run.
static_files_path = "frontend/build"
if os.path.exists(static_files_path):
    print(f"Serving static files from: {static_files_path}")
    app.mount("/", StaticFiles(directory=static_files_path, html=True), name="static")
else:
    print(f"Static files directory not found at '{static_files_path}'. Frontend will not be served by FastAPI.")
