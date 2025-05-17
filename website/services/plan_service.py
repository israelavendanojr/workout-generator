from website import db
from website.models.saved_models import SavedPlan
from flask_login import current_user
from website.utils.plan_utils import get_saved_plan
from website.models.generation_models import Exercise, ExerciseRole
from collections import defaultdict
import json

def save_workout_plan(split_name, plan_data):
    """
    Save a generated workout plan to the database
    """
    try:
        plan = json.loads(plan_data)
        
        # Create new saved plan
        saved_plan = SavedPlan(
            split_name=split_name,
            user_id=current_user.id
        )
        db.session.add(saved_plan)
        db.session.flush()  # Get the ID of the new plan
        
        # Create saved days with order
        from website.services.day_service import create_day_from_plan
        for index, day in enumerate(plan['days']):
            create_day_from_plan(saved_plan.id, day, index)
        
        db.session.commit()
        return saved_plan, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def rename_plan(plan_id, new_name):
    """
    Rename an existing workout plan
    """
    plan = SavedPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
    if plan:
        plan.split_name = new_name
        db.session.commit()
        return True, "Plan renamed successfully!"
    else:
        return False, "Plan not found or access denied."

def delete_plan(plan_id):
    """
    Delete a workout plan
    """
    try:
        plan = get_saved_plan(plan_id)
        if plan.user_id != current_user.id:
            return False, "You cannot delete plans you do not own."
            
        # delete plan
        db.session.delete(plan)
        db.session.commit()
        return True, "Plan deleted successfully!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def get_all_user_plans():
    """
    Get all workout plans owned by the current user
    """
    return SavedPlan.query.filter_by(user_id=current_user.id).all()

def get_exercises_by_role():
    """
    Get all exercises grouped by their role
    """
    exercises = Exercise.query.all()
    exercises_by_role = defaultdict(list)
    
    for exercise in exercises:
        role_name = exercise.role.name
        exercises_by_role[role_name].append({
            'id': exercise.id,
            'name': exercise.name,
        })
    
    return exercises_by_role

def get_all_exercise_roles():
    """
    Get all exercise roles
    """
    return ExerciseRole.query.all()