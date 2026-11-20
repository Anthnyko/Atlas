from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.card import Card
from app.models.review_history import ReviewHistory


def _latest_reviews(user_id: int, db: Session):
    return (
        db.query(
            ReviewHistory.card_id,
            func.max(ReviewHistory.id).label("review_id"),
        )
        .filter(ReviewHistory.user_id == user_id)
        .group_by(ReviewHistory.card_id)
        .subquery()
    )


def get_next_card(deck_id: int, user_id: int, db: Session):
    now = datetime.utcnow()
    latest_reviews = _latest_reviews(user_id, db)

    due_card = (
        db.query(Card)
        .join(latest_reviews, latest_reviews.c.card_id == Card.id)
        .join(ReviewHistory, ReviewHistory.id == latest_reviews.c.review_id)
        .filter(Card.deck_id == deck_id, ReviewHistory.next_review_date <= now)
        .order_by(ReviewHistory.next_review_date, Card.id)
        .first()
    )
    if due_card:
        return due_card

    return (
        db.query(Card)
        .outerjoin(latest_reviews, latest_reviews.c.card_id == Card.id)
        .filter(Card.deck_id == deck_id, latest_reviews.c.review_id.is_(None))
        .order_by(Card.id)
        .first()
    )


def get_study_counts(deck_id: int, user_id: int, db: Session) -> dict[str, int]:
    now = datetime.utcnow()
    latest_reviews = _latest_reviews(user_id, db)
    total_cards = db.query(func.count(Card.id)).filter(Card.deck_id == deck_id).scalar() or 0
    due_cards = (
        db.query(func.count(Card.id))
        .join(latest_reviews, latest_reviews.c.card_id == Card.id)
        .join(ReviewHistory, ReviewHistory.id == latest_reviews.c.review_id)
        .filter(Card.deck_id == deck_id, ReviewHistory.next_review_date <= now)
        .scalar()
        or 0
    )
    new_cards = (
        db.query(func.count(Card.id))
        .outerjoin(latest_reviews, latest_reviews.c.card_id == Card.id)
        .filter(Card.deck_id == deck_id, latest_reviews.c.review_id.is_(None))
        .scalar()
        or 0
    )
    return {
        "total_cards": total_cards,
        "due_cards": due_cards,
        "new_cards": new_cards,
        "completed_cards": total_cards - due_cards - new_cards,
    }
