from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from website.models.saved_models import *
from website.models.logging_models import *
from website import db
from datetime import date, timedelta

log_routes = Blueprint('log_routes', __name__)

@log_routes.route('/logged_plans', methods=['GET'])
@login_required
def logged_plans():
    saved_plans = SavedPlan.query.filter_by(user_id=current_user.id).all()
    logged_weeks = LoggedWeek.query.filter_by(user_id=current_user.id) \
    .order_by(LoggedWeek.start_date.desc()) \
    .options(
        db.joinedload(LoggedWeek.logged_days)
            .joinedload(LoggedDay.saved_day),  # ensure we load this for sorting
        db.joinedload(LoggedWeek.logged_days)
            .joinedload(LoggedDay.logged_exercises)
            .joinedload(LoggedExercise.saved_exercise),
        db.joinedload(LoggedWeek.logged_days)
            .joinedload(LoggedDay.logged_exercises)
            .joinedload(LoggedExercise.sets)
    ).all()

    for week in logged_weeks:
        week.logged_days.sort(key=lambda d: d.saved_day.order if d.saved_day else 0)
        for day in week.logged_days:
            day.logged_exercises.sort(key=lambda e: e.saved_exercise.order if e.saved_exercise else 0)


    # Inside your /logged_plans view function after querying `logged_weeks`
    if len(logged_weeks) >= 2:
        prev_week = logged_weeks[1]  # because weeks are ordered DESC
        prev_sets = {}
        for day in prev_week.logged_days:
            for ex in day.logged_exercises:
                prev_sets[ex.saved_exercise_id] = ex.sets

        curr_week = logged_weeks[0]
        for day in curr_week.logged_days:
            for ex in day.logged_exercises:
                if ex.saved_exercise_id in prev_sets:
                    for i in range(len(ex.sets)):
                        # Only fill if reps/weight not logged
                        if i < len(prev_sets[ex.saved_exercise_id]):
                            if ex.sets[i].reps is None and ex.sets[i].weight is None:
                                ex.sets[i].weight = prev_sets[ex.saved_exercise_id][i].weight


    return render_template("logged_plans.html", user=current_user, saved_plans=saved_plans, logged_weeks=logged_weeks)

@log_routes.route('/logged_plans/add_week', methods=['POST'])
@login_required
def add_logged_week():
    data = request.get_json()
    print("Received POST to /add_week with:", data)

    plan_id = data.get('plan_id')

    saved_plan = SavedPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
    if not saved_plan:
        return {"error": "Plan not found"}, 404

    # Create the new LoggedWeek
    new_week = LoggedWeek(
        user_id=current_user.id,
        saved_plan_id=saved_plan.id,
        # start_date=date.today()
    )
    db.session.add(new_week)
    db.session.flush()  # So we can reference new_week.id before committing

    # Get all SavedDays for this plan
    saved_days = SavedDay.query.filter_by(saved_plan_id=saved_plan.id).order_by(SavedDay.order).all()

    for i, saved_day in enumerate(saved_days):
        log_date = date.today() + timedelta(days=i)

        new_logged_day = LoggedDay(
            logged_week_id=new_week.id,
            user_id=current_user.id,
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
            db.session.flush()  # Get new_logged_exercise.id

            for _ in range(saved_exercise.sets):
                new_set = LoggedSet(
                    logged_exercise_id=new_logged_exercise.id,
                    reps=None,
                    weight=None
                )
                db.session.add(new_set)


    db.session.commit()
    flash("Workout week successfully logged!", "success")
    return ('', 204)

@log_routes.route('/logged_plans/delete_week/<int:week_id>', methods=['POST'])
@login_required
def delete_logged_week(week_id):
    week = LoggedWeek.query.filter_by(id=week_id, user_id=current_user.id).first_or_404()

    db.session.delete(week)  # Cascades will delete related days, exercises, and sets
    db.session.commit()

    flash("Workout week deleted.", "success")
    return redirect(url_for('log_routes.logged_plans'))

@log_routes.route('/logged_plans/log_day_sets/<int:day_id>', methods=['POST'])
@login_required
def log_day_sets(day_id):
    day = LoggedDay.query.filter_by(id=day_id, user_id=current_user.id).first_or_404()

    # Remove existing sets
    for exercise in day.logged_exercises:
        LoggedSet.query.filter_by(logged_exercise_id=exercise.id).delete()

    # Process new inputs
    for exercise in day.logged_exercises:
        for i in range(exercise.saved_exercise.sets):
            reps = request.form.get(f"reps_{exercise.id}_{i}")
            weight = request.form.get(f"weight_{exercise.id}_{i}")
            if reps and weight:
                db.session.add(LoggedSet(
                    logged_exercise_id=exercise.id,
                    reps=int(reps),
                    weight=float(weight)
                ))

    db.session.commit()
    flash("Sets logged for the day!", "success")
    return redirect(url_for('log_routes.logged_plans'))
