from website.models.logging_models import LoggedExercise, LoggedDay, LoggedSet
from collections import defaultdict
from sqlalchemy.orm import joinedload

def get_user_progression(user_id):
    """
    Get progression data for each exercise based on estimated 1RM
    """
    progression = defaultdict(list)

    logged_exercises = (
        LoggedExercise.query
        .join(LoggedDay)
        .filter(LoggedDay.user_id == user_id)
        .options(
            joinedload(LoggedExercise.sets),
            joinedload(LoggedExercise.logged_day)
        )
        .order_by(LoggedDay.date.asc())
        .all()
    )

    for ex in logged_exercises:
        best_e1rm = 0
        for s in ex.sets:
            if s.weight and s.reps:
                e1rm = s.weight * (1 + s.reps / 30)
                best_e1rm = max(best_e1rm, e1rm)
        if best_e1rm:
            progression[ex.name].append({
                'date': ex.logged_day.date.strftime('%Y-%m-%d'),
                'e1rm': round(best_e1rm, 2)
            })

    return progression
