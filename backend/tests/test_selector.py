from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.selector import get_next_card, get_study_counts
from app.db.base import Base
from app.models.card import Card
from app.models.deck import Deck
from app.models.review_history import ReviewHistory
from app.models.tag import Tag  # noqa: F401 - registers card_tags
from app.models.user import User


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def review(user_id: int, deck_id: int, card_id: int, due_at: datetime) -> ReviewHistory:
    return ReviewHistory(
        user_id=user_id,
        deck_id=deck_id,
        card_id=card_id,
        was_correct=True,
        quality=5,
        repetitions=1,
        interval=1,
        ease_factor=2.5,
        next_review_date=due_at,
    )


def test_selector_uses_only_the_users_latest_review_and_keeps_other_users_cards_new(db):
    user = User(email="owner@example.com", hashed_password="hash")
    other_user = User(email="other@example.com", hashed_password="hash")
    deck = Deck(name="Deck", owner=user)
    first_card = Card(front="first", back="one", deck=deck)
    second_card = Card(front="second", back="two", deck=deck)
    db.add_all([user, other_user, deck, first_card, second_card])
    db.commit()

    now = datetime.utcnow()
    # An earlier due review must be ignored because the latest review is future.
    db.add_all([
        review(user.id, deck.id, first_card.id, now - timedelta(days=2)),
        review(user.id, deck.id, first_card.id, now + timedelta(days=2)),
        # A review by another user must not stop this card being new for the owner.
        review(other_user.id, deck.id, second_card.id, now + timedelta(days=1)),
    ])
    db.commit()

    assert get_next_card(deck.id, user.id, db).id == second_card.id
    assert get_study_counts(deck.id, user.id, db) == {
        "total_cards": 2,
        "due_cards": 0,
        "new_cards": 1,
        "completed_cards": 1,
    }

    db.add(review(user.id, deck.id, first_card.id, now - timedelta(minutes=1)))
    db.commit()

    assert get_next_card(deck.id, user.id, db).id == first_card.id
    assert get_study_counts(deck.id, user.id, db)["due_cards"] == 1
