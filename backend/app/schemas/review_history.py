from pydantic import BaseModel
from datetime import datetime

class ReviewHistoryBase(BaseModel):
    was_correct: bool
    quality: int

class ReviewHistoryCreate(ReviewHistoryBase):
    pass

class ReviewHistoryOut(ReviewHistoryBase):
    id: int
    card_id: int
    deck_id: int
    user_id: int
    timestamp: datetime
    interval: int
    repetitions: int
    ease_factor: float
    next_review_date: datetime

    class Config:
        from_attributes = True
