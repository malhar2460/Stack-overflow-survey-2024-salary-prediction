# backend/app/schemas.py

from pydantic import BaseModel, Field

class DeveloperProfile(BaseModel):
    """
    Pydantic schema for validating incoming developer profile data.
    The field names must match the column names used during model training.
    """
    Country: str
    EdLevel: str
    YearsCodePro: int = Field(..., ge=0) # Add validation for non-negative years
    MainBranch: str
    RemoteWork: str
    Age: str
    LanguageHaveWorkedWith: str  # Semicolon-delimited string, e.g., "Python;JavaScript"
    DatabaseHaveWorkedWith: str
    WebframeHaveWorkedWith: str
    OpSysPersonalUse: str

    class Config:
        # Provides an example for the auto-generated API documentation
        schema_extra = {
            "example": {
                "Country": "United States of America",
                "EdLevel": "Master’s degree (M.A., M.S., M.Eng., MBA, etc.)",
                "YearsCodePro": 10,
                "MainBranch": "I am a developer by profession",
                "RemoteWork": "Remote",
                "Age": "25-34 years old",
                "LanguageHaveWorkedWith": "Python;JavaScript;HTML/CSS;SQL",
                "DatabaseHaveWorkedWith": "PostgreSQL;SQLite",
                "WebframeHaveWorkedWith": "FastAPI;Svelte",
                "OpSysPersonalUse": "Linux-based"
            }
        }

class PredictionResponse(BaseModel):
    """
    Pydantic schema for the prediction response.
    """
    predicted_salary_usd: float
