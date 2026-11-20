from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.scheduler import DEFAULT_EASE_FACTOR, schedule_next_review
from app.core.selector import get_next_card, get_study_counts
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.card import Card
from app.models.deck import Deck
from app.models.review_history import ReviewHistory
from app.models.user import User

router = APIRouter(prefix="/study", tags=["study"])


def get_owned_deck(deck_id: int, db: Session, current_user: User) -> Deck:
    deck = db.query(Deck).filter(Deck.id == deck_id, Deck.owner_id == current_user.id).first()
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found.")
    return deck


@router.post("/start/{deck_id}")
def start_session(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_deck(deck_id, db, current_user)
    counts = get_study_counts(deck_id, current_user.id, db)
    return {"deck_id": deck_id, **counts, "message": "Study session initialized."}


@router.get("/next-card/{deck_id}")
def next_card(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_deck(deck_id, db, current_user)
    card = get_next_card(deck_id, current_user.id, db)
    if not card:
        return {"message": "No cards left to study.", "card": None}
    return {"card_id": card.id, "front": card.front, "back": card.back}


@router.post("/submit-answer")
def submit_answer(
    card_id: int,
    quality: int | None = None,
    was_correct: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record an SM-2 quality score.

    ``was_correct`` remains temporarily supported for existing clients and is
    translated to quality 5 (correct) or 2 (incorrect).
    """
    if quality is None:
        if was_correct is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A quality score is required.")
        quality = 5 if was_correct else 2
    if quality < 0 or quality > 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quality must be between 0 and 5.")

    card = (
        db.query(Card)
        .join(Deck)
        .filter(Card.id == card_id, Deck.owner_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")

    last_review = (
        db.query(ReviewHistory)
        .filter(ReviewHistory.card_id == card_id, ReviewHistory.user_id == current_user.id)
        .order_by(ReviewHistory.id.desc())
        .first()
    )
    schedule = schedule_next_review(
        quality=quality,
        repetitions=last_review.repetitions if last_review else 0,
        interval=last_review.interval if last_review else 0,
        ease_factor=last_review.ease_factor if last_review else DEFAULT_EASE_FACTOR,
    )
    new_review = ReviewHistory(
        user_id=current_user.id,
        deck_id=card.deck_id,
        card_id=card_id,
        was_correct=quality >= 3,
        quality=schedule.quality,
        repetitions=schedule.repetitions,
        interval=schedule.interval,
        ease_factor=schedule.ease_factor,
        next_review_date=schedule.next_review_date,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return {
        "message": "Answer recorded.",
        "review": {
            "card_id": card_id,
            "quality": schedule.quality,
            "was_correct": quality >= 3,
            "repetitions": schedule.repetitions,
            "interval": schedule.interval,
            "ease_factor": schedule.ease_factor,
            "next_review_date": schedule.next_review_date,
        },
    }


@router.get("/practice/{deck_id}")
def get_practice_cards(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_deck(deck_id, db, current_user)
    return db.query(Card).filter(Card.deck_id == deck_id).order_by(Card.id).all()


@router.get("/progress/{deck_id}")
def study_progress(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_deck(deck_id, db, current_user)
    return get_study_counts(deck_id, current_user.id, db)
