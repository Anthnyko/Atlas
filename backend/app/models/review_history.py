from sqlalchemy import Column, Integer, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class ReviewHistory(Base):
    __tablename__ = "review_history"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False) # when
    was_correct = Column(Boolean, nullable=False) # did user remember
    quality = Column(Integer, nullable=False)
    repetitions = Column(Integer, default=0, nullable=False)

    interval = Column(Integer, default=1, nullable=False) # how long till next review (in days)
    ease_factor = Column(Float, default=2.5, nullable=False)
    next_review_date = Column(DateTime, nullable=False) # when card should be shown again

    user = relationship("User")
    deck = relationship("Deck")
    card = relationship("Card")
