from website.models.saved_models import SavedPlan, SavedDay
from website.models.logging_models import *
from website import db
from datetime import date, timedelta

def get_logged_data_for_display(user_id):
    saved_plans = SavedPlan.query.filter_by(user_id=user_id).all()
    logged_weeks = LoggedWeek.query.filter_by(user_id=user_id) \
        .order_by(LoggedWeek.start_date.desc()) \
        .options(
            db.joinedload(LoggedWeek.logged_days).joinedload(LoggedDay.saved_day),
            db.joinedload(LoggedWeek.logged_days).joinedload(LoggedDay.logged_exercises).joinedload(LoggedExercise.saved_exercise),
            db.joinedload(LoggedWeek.logged_days).joinedload(LoggedDay.logged_exercises).joinedload(LoggedExercise.sets)
        ).all()

    for week in logged_weeks:
        week.logged_days.sort(key=lambda d: d.saved_day.order if d.saved_day else 0)
        for day in week.logged_days:
            day.logged_exercises.sort(key=lambda e: e.saved_exercise.order if e.saved_exercise else 0)

    if len(logged_weeks) >= 2:
        prev_week = logged_weeks[1]
        prev_sets = {
            ex.saved_exercise_id: ex.sets
            for day in prev_week.logged_days
            for ex in day.logged_exercises
        }

        curr_week = logged_weeks[0]
        for day in curr_week.logged_days:
            for ex in day.logged_exercises:
                if ex.saved_exercise_id in prev_sets:
                    for i, current_set in enumerate(ex.sets):
                        if i < len(prev_sets[ex.saved_exercise_id]):
                            prev_set = prev_sets[ex.saved_exercise_id][i]
                            if current_set.reps is None and current_set.weight is None:
                                current_set.weight = prev_set.weight

    return saved_plans, logged_weeks

def create_logged_week_from_saved_plan(user_id, plan_id):
    saved_plan = SavedPlan.query.filter_by(id=plan_id, user_id=user_id).first()
    if not saved_plan:
        return False, "Plan not found", 404

    new_week = LoggedWeek(user_id=user_id, saved_plan_id=saved_plan.id)
    db.session.add(new_week)
    db.session.flush()

    saved_days = SavedDay.query.filter_by(saved_plan_id=saved_plan.id).order_by(SavedDay.order).all()

    for i, saved_day in enumerate(saved_days):
        log_date = date.today() + timedelta(days=i)
        new_logged_day = LoggedDay(
            logged_week_id=new_week.id,
            user_id=user_id,
            saved_day_id=saved_day.id,
            date=log_date
        )
        db.session.add(new_logged_day)
        db.session.flush()

        for saved_exercise in saved_day.exercises:
            new_logged_exercise = LoggedExercise(
                logged_day_id=new_logged_day.id,
                saved_exercise_id=saved_exercise.id,
                name=saved_exercise.name,
                notes=""
            )
            db.session.add(new_logged_exercise)
            db.session.flush()

            for _ in range(saved_exercise.sets):
                new_set = LoggedSet(
                    logged_exercise_id=new_logged_exercise.id,
                    reps=None,
                    weight=None
                )
                db.session.add(new_set)

    db.session.commit()
    return True, "Workout week successfully logged!", 200

def delete_logged_week_by_id(user_id, week_id):
    week = LoggedWeek.query.filter_by(id=week_id, user_id=user_id).first_or_404()
    db.session.delete(week)
    db.session.commit()

def update_logged_sets_for_day(user_id, day_id, form_data):
    day = LoggedDay.query.filter_by(id=day_id, user_id=user_id).first_or_404()

    for exercise in day.logged_exercises:
        LoggedSet.query.filter_by(logged_exercise_id=exercise.id).delete()

    for exercise in day.logged_exercises:
        for i in range(exercise.saved_exercise.sets):
            reps = form_data.get(f"reps_{exercise.id}_{i}")
            weight = form_data.get(f"weight_{exercise.id}_{i}")
            if reps and weight:
                db.session.add(LoggedSet(
                    logged_exercise_id=exercise.id,
                    reps=int(reps),
                    weight=float(weight)
                ))

    db.session.commit()
