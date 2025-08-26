# app/schemas.py
from typing import List, Optional
from pydantic import BaseModel, Field

class TextIn(BaseModel):
    text: str = Field(..., min_length=1, description="Zu detektierender Text")

class BatchIn(BaseModel):
    items: List[str] = Field(..., description="Liste von Texten in gleicher Reihenfolge")

class AltCandidate(BaseModel):
    language: str
    language_name: str         # <-- NEU
    confidence: float

class DetectOut(BaseModel):
    language: str
    language_name: str         # <-- NEU
    iso639_3: Optional[str] = None
    confidence: float
    alternatives: List[AltCandidate]
    engine: str
