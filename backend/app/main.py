import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Stack Overflow Salary Predictor API",
    description="An API to predict developer salaries based on the 2024 Stack Overflow survey data.",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",     
    "http://127.0.0.1:5173",     
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,
    allow_methods=["GET", "POST"],    
    allow_headers=["*"],              
)
try:
    pipeline = joblib.load('full_pipeline.joblib')
    print("✅ Prediction pipeline loaded successfully.")
except FileNotFoundError:
    print("🚨 Error: 'full_pipeline.joblib' not found. Make sure the model file is in the same directory.")
    pipeline = None
except Exception as e:
    print(f"🚨 An unexpected error occurred while loading the pipeline: {e}")
    pipeline = None

class DeveloperProfile(BaseModel):
    Country: str = Field(..., example="United States of America")
    EdLevel: str = Field(..., example="Bachelor’s degree (B.A., B.S., B.Eng., etc.)")
    YearsCodePro: float = Field(..., example=10.0, description="Years of professional coding experience.")
    MainBranch: str = Field(..., example="Developer, full-stack")
    LanguageHaveWorkedWith: str = Field(..., example="HTML/CSS;JavaScript;Python;SQL")
    WebframeHaveWorkedWith: str = Field(..., example="Node.js;React")
    DatabaseHaveWorkedWith: str = Field(..., example="PostgreSQL;SQLite")
    # PlatformHaveWorkedWith: str = Field(..., example="AWS;Docker;Heroku")
    OpSysPersonalUse: str = Field(..., example="macOS")

    
    class Config:
        schema_extra = {
            "example": {
                "Country": "Germany",
                "EdLevel": "Master’s degree (M.A., M.S., M.Eng., MBA, etc.)",
                "YearsCodePro": 5,
                "DevType": "Developer, back-end",
                "LanguageHaveWorkedWith": "C",
                "WebframeHaveWorkedWith": "ASP.NET Core;React",
                "DatabaseHaveWorkedWith": "Microsoft SQL Server",
                "PlatformHaveWorkedWith": "Microsoft Azure",
                "OpSys": "Windows"
            }
        }

# Load once at startup
SURVEY_DF = pd.read_csv("../../data/processed/features_labels.csv").dropna(subset=["ConvertedCompYearly"])

@app.get("/eda", tags=["EDA"])
def get_eda():
    """
    Returns:
      {
        top_countries: [str…],
        country_salaries: [float…],
        top_tech: [str…],
        tech_salaries: [float…]
      }
    """
    df = SURVEY_DF

    # Top 10 countries by median salary
    country_med = (
        df.groupby("Country")["ConvertedCompYearly"]
          .median()
          .sort_values(ascending=False)
          .head(10)
    )
    top_countries      = country_med.index.tolist()
    country_salaries   = country_med.values.tolist()

    # Top 10 technologies by median salary
    # Assumes there's one column listing multi-select techs,
    # so we need to explode it first:
    tech_series = (
        df.LanguageHaveWorkedWith
          .dropna()
          .str.split(";")
          .explode()
          .to_frame("tech")
          .join(df["ConvertedCompYearly"], how="left")
    )
    tech_med = (
        tech_series.groupby("tech")["ConvertedCompYearly"]
                  .median()
                  .sort_values(ascending=False)
                  .head(10)
    )
    top_tech       = tech_med.index.tolist()
    tech_salaries  = tech_med.values.tolist()

    return {
        "top_countries":      top_countries,
        "country_salaries":   country_salaries,
        "top_tech":           top_tech,
        "tech_salaries":      tech_salaries
    }


@app.get("/", tags=["General"])
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"status": "ok", "message": "Welcome to the Salary Predictor API!"}

@app.post("/predict", tags=["Prediction"])
def predict_salary(profile: DeveloperProfile):
    """
    Predicts the annual salary in USD based on a developer's profile.

    - **profile**: A JSON object containing the developer's details.

    Returns:
    - A JSON object with the predicted salary.
    """
    if not pipeline:
        raise HTTPException(status_code=500, detail="Prediction model is not available.")
    try:
        data = profile.dict()
        input_df = pd.DataFrame(data, index=[0])
        prediction = pipeline.predict(input_df)[0]
        predicted_salary = round(float(prediction), 2)
        return {"predicted_yearly_salary_usd": predicted_salary}

    except Exception as e:
        print(f"🚨 Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during the prediction process: {str(e)}")






