from pydantic import BaseModel
from typing import List

class PredictionOutput(BaseModel):
    """
    Schema for the prediction response.
    """
    prediction: float

class ModelSchema(BaseModel):
    """
    Schema for providing the model's required features to the frontend.
    """
    features: List[str]
