from datetime import datetime, timedelta

import pytest

from app.core.scheduler import MIN_EASE_FACTOR, schedule_next_review


NOW = datetime(2026, 1, 1, 12, 0, 0)


def test_sm2_uses_first_second_and_subsequent_intervals():
    first = schedule_next_review(quality=5, now=NOW)
    assert first.repetitions == 1
    assert first.interval == 1
    assert first.ease_factor == pytest.approx(2.6)
    assert first.next_review_date == NOW + timedelta(days=1)

    second = schedule_next_review(
        quality=4,
        repetitions=first.repetitions,
        interval=first.interval,
        ease_factor=first.ease_factor,
        now=NOW,
    )
    assert (second.repetitions, second.interval) == (2, 6)
    assert second.ease_factor == pytest.approx(2.6)

    third = schedule_next_review(
        quality=5,
        repetitions=second.repetitions,
        interval=second.interval,
        ease_factor=second.ease_factor,
        now=NOW,
    )
    assert (third.repetitions, third.interval) == (3, 16)
    assert third.ease_factor == pytest.approx(2.7)


def test_sm2_lapse_resets_repetitions_and_interval():
    result = schedule_next_review(
        quality=2,
        repetitions=4,
        interval=40,
        ease_factor=2.7,
        now=NOW,
    )

    assert (result.repetitions, result.interval) == (0, 1)
    assert result.ease_factor == pytest.approx(2.38)
    assert result.next_review_date == NOW + timedelta(days=1)


def test_sm2_never_reduces_ease_below_minimum():
    result = schedule_next_review(quality=0, ease_factor=MIN_EASE_FACTOR, now=NOW)
    assert result.ease_factor == MIN_EASE_FACTOR


@pytest.mark.parametrize("quality", [-1, 6])
def test_sm2_rejects_invalid_quality(quality):
    with pytest.raises(ValueError, match="0 through 5"):
        schedule_next_review(quality=quality, now=NOW)
