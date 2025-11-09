from pydantic import BaseModel
from typing import List, Dict, Optional

class Perspective(BaseModel):
    actor: str
    stance: str
    key_claims: List[str]

class PerspectivesJSON(BaseModel):
    user_A_perspectives: List[Perspective]
    user_B_perspectives: List[Perspective]

class SentimentIntent(BaseModel):
    valence: float  # Range: [-1, 1]
    emotion_scores: Dict[str, float]  # e.g., {"anger": 0.8, "joy": 0.1}
    intent: str     # e.g., "seek_reassurance"

class SentimentsJSON(BaseModel):
    user_A_sentiment: SentimentIntent
    user_B_sentiment: SentimentIntent

class CandidateReply(BaseModel):
    reply_text: str

class SafetyReport(BaseModel):
    approved: bool
    reason: Optional[str]
