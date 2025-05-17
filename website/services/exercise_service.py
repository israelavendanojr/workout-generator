from website import db
from website.models.saved_models import SavedExercise, Note
from website.models.generation_models import Exercise
from website.utils.reorder_utils import update_order_after_delete, get_max_order

def create_exercise_from_plan(saved_day_id, exercise_data, order_index):
    """
    Create a saved exercise from plan data during plan save process
    """
    saved_exercise = SavedExercise(
        saved_day_id=saved_day_id,
        exercise_id=exercise_data['exercise_id'],
        name=exercise_data['name'],
        sets=exercise_data['sets'],
        start_reps=exercise_data['start_reps'],
        end_reps=exercise_data['end_reps'],
        to_failure=exercise_data.get('to_failure', False),
        order=order_index
    )
    db.session.add(saved_exercise)
    return saved_exercise

def swap_exercise(exercise_id, new_exercise_id, sets, start_reps, end_reps, notes_data):
    """
    Swap an existing exercise with a new one
    """
    try:
        # Find the saved exercise to update
        saved_exercise = SavedExercise.query.get_or_404(exercise_id)
        
        # Get the new exercise
        new_exercise = Exercise.query.get(new_exercise_id)
        if not new_exercise:
            return False, "New exercise not found"

        # Update the saved exercise
        saved_exercise.exercise_id = new_exercise.id
        saved_exercise.name = new_exercise.name
        saved_exercise.sets = sets
        saved_exercise.start_reps = start_reps
        saved_exercise.end_reps = end_reps

        # Update notes
        # First, delete all existing notes
        for note in saved_exercise.notes:
            db.session.delete(note)
        
        # Then add new notes
        for index, note_content in enumerate(notes_data):
            if note_content.strip():  # Only add non-empty notes
                note = Note(
                    content=note_content.strip(),
                    saved_exercise_id=saved_exercise.id,
                    order=index
                )
                db.session.add(note)

        db.session.commit()
        return True, "Exercise updated successfully!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def add_exercise(day_id, exercise_id, sets, start_reps, end_reps):
    """
    Add a new exercise to a workout day
    """
    try:
        # Get the exercise
        exercise = Exercise.query.get_or_404(exercise_id)
        
        # Get the current highest order for this day
        max_order = get_max_order(SavedExercise, "saved_day_id", day_id)

        # Create new saved exercise
        new_exercise = SavedExercise(
            saved_day_id=day_id,
            exercise_id=exercise.id,
            name=exercise.name,
            sets=sets,
            start_reps=start_reps,
            end_reps=end_reps,
            to_failure=False,  
            order=max_order + 1  # Add to the end of the list
        )

        db.session.add(new_exercise)
        db.session.commit()
        return True, "Exercise added successfully!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def delete_exercise(exercise_id):
    """
    Delete an exercise from a workout day
    """
    try:
        # Get the saved exercise
        saved_exercise = SavedExercise.query.get_or_404(exercise_id)
        
        # Get the day_id and order for reordering
        day_id = saved_exercise.workout_day.id
        deleted_order = saved_exercise.order

        # Delete the exercise
        db.session.delete(saved_exercise)

        # Update the order of remaining exercises
        update_order_after_delete(SavedExercise, "saved_day_id", day_id, deleted_order)
        
        db.session.commit()
        return True, "Exercise deleted successfully!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def reorder_exercise(exercise_id, new_order, new_day_id):
    """
    Reorder an exercise within a workout day or move it to another day
    """
    try:
        # Get the exercise
        saved_exercise = SavedExercise.query.get_or_404(exercise_id)
        old_day_id = saved_exercise.saved_day_id
        
        # Get all exercises in the new day
        day_exercises = SavedExercise.query.filter_by(saved_day_id=new_day_id).order_by(SavedExercise.order).all()
        
        # Remove the exercise from its current position if it's in the same day
        if old_day_id == new_day_id:
            day_exercises.remove(saved_exercise)
        
        # Insert it at the new position
        day_exercises.insert(new_order, saved_exercise)
        
        # Update all orders and the day_id
        for i, exercise in enumerate(day_exercises):
            exercise.order = i
            if exercise.id == saved_exercise.id:
                exercise.saved_day_id = new_day_id

        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)