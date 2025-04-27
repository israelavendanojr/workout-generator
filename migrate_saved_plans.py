from website import create_app, db
from website.models import SavedPlan, SavedDay, SavedExercise, Exercise

def migrate_saved_plans():
    plans = SavedPlan.query.all()

    # Buffer to hold SavedDay and SavedExercise objects before committing
    new_days = []
    new_exercises = []

    for plan in plans:
        plan_data = plan.get_plan_data()

        # Iterate through each day in the plan
        for day_name, exercises in plan_data.items():
            # Create and save the SavedDay object for each day
            saved_day = SavedDay(
                saved_plan_id=plan.id,
                day_name=day_name
            )
            new_days.append(saved_day)
            db.session.add(saved_day)  # Immediately add to session to get the saved_day.id

            # Now iterate over the exercises for this day and create SavedExercise objects
            for exercise_data in exercises:
                saved_exercise = SavedExercise(
                    saved_day_id=saved_day.id,  # This is now correctly linked to the current saved_day
                    # exercise_id=exercise_data.get("id"),  # Use .get() to avoid potential KeyError
                    sets=exercise_data.get("sets", 0),
                    start_reps=exercise_data.get("start_reps", 0),
                    end_reps=exercise_data.get("end_reps", 0),
                    to_failure=exercise_data.get("toFailure", False),  # Adjust key to match casing if necessary
                    order=exercise_data.get("order", 0)
                )
                new_exercises.append(saved_exercise)

        # Commit exercises in bulk after processing all days for this plan
        db.session.add_all(new_exercises)
        db.session.commit()  # Commit after adding all exercises

        # Optionally clear out old 'plan' data if you don't need it anymore
        plan.plan = None  # Remove the plan data
        db.session.commit()

    print("✅ Migration complete!")

# Ensure that the app context is created
if __name__ == "__main__":
    app = create_app()  # This initializes the Flask app (make sure it's defined in your app)
    with app.app_context():
        migrate_saved_plans()  # Run the migration function within the app context
