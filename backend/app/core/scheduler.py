from dataclasses import dataclass
from datetime import datetime, timedelta


MIN_EASE_FACTOR = 1.3
DEFAULT_EASE_FACTOR = 2.5


@dataclass(frozen=True)
class SM2Schedule:
    quality: int
    repetitions: int
    interval: int
    ease_factor: float
    next_review_date: datetime


def schedule_next_review(
    quality: int,
    repetitions: int = 0,
    interval: int = 0,
    ease_factor: float = DEFAULT_EASE_FACTOR,
    now: datetime | None = None,
) -> SM2Schedule:
    """Calculate the next review using the SuperMemo SM-2 algorithm."""
    if quality < 0 or quality > 5:
        raise ValueError("quality must be an integer from 0 through 5")

    review_time = now or datetime.utcnow()
    previous_ease = max(float(ease_factor), MIN_EASE_FACTOR)
    difficulty = 5 - quality
    updated_ease = max(
        MIN_EASE_FACTOR,
        previous_ease + 0.1 - difficulty * (0.08 + difficulty * 0.02),
    )

    if quality < 3:
        updated_repetitions = 0
        updated_interval = 1
    else:
        updated_repetitions = max(repetitions, 0) + 1
        if updated_repetitions == 1:
            updated_interval = 1
        elif updated_repetitions == 2:
            updated_interval = 6
        else:
            updated_interval = max(1, round(max(interval, 1) * updated_ease))

    return SM2Schedule(
        quality=quality,
        repetitions=updated_repetitions,
        interval=updated_interval,
        ease_factor=updated_ease,
        next_review_date=review_time + timedelta(days=updated_interval),
    )
