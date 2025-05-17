from website import db
from website.models.saved_models import SavedDay
from website.utils.plan_utils import get_saved_plan
from website.utils.reorder_utils import update_order_after_delete, get_max_order

def create_day_from_plan(saved_plan_id, day_data, order_index):
    """
    Create a saved day from plan data during plan save process
    """
    saved_day = SavedDay(
        saved_plan_id=saved_plan_id,
        day_name=day_data['name'],
        order=order_index
    )
    db.session.add(saved_day)
    db.session.flush()  # Get the ID of the new day
    
    # Create saved exercises
    from website.services.exercise_service import create_exercise_from_plan
    for exercise_index, exercise in enumerate(day_data['exercises']):
        create_exercise_from_plan(saved_day.id, exercise, exercise_index)
    
    return saved_day

def add_day(plan_id, day_name):
    """
    Add a new day to an existing workout plan
    """
    try:
        # Get the plan and verify ownership
        saved_plan = get_saved_plan(plan_id)
        
        # Get the current highest order for this plan
        max_order = get_max_order(SavedDay, "saved_plan_id", plan_id)
        
        # Create new saved day
        new_day = SavedDay(
            saved_plan_id=plan_id,
            day_name=day_name,
            order=max_order + 1  # Add to the end of the list
        )

        db.session.add(new_day)
        db.session.commit()
        return True, "Day added successfully!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def rename_day(day_id, new_name):
    """
    Rename an existing workout day
    """
    try:
        # Get the day
        saved_day = SavedDay.query.get_or_404(day_id)
        
        # Update the day name
        saved_day.day_name = new_name
        db.session.commit()
        return True, "Day renamed successfully!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def delete_day(day_id):
    """
    Delete a workout day
    """
    try:
        # Get the saved day
        saved_day = SavedDay.query.get_or_404(day_id)
        saved_plan = saved_day.saved_plan
        plan_id = saved_plan.id
        deleted_order = saved_day.order

        # Delete the day (this will cascade delete all exercises in the day)
        db.session.delete(saved_day)

        # Update the order of remaining days
        update_order_after_delete(SavedDay, "saved_plan_id", plan_id, deleted_order)
        
        db.session.commit()
        return True, "Day deleted successfully!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def reorder_day(day_id, new_order):
    """
    Reorder a day within a workout plan
    """
    try:
        # Get the day
        saved_day = SavedDay.query.get_or_404(day_id)
        saved_plan = saved_day.saved_plan
        plan_id = saved_plan.id
        
        # Get all days in the plan
        plan_days = SavedDay.query.filter_by(saved_plan_id=plan_id).order_by(SavedDay.order).all()
        
        # Remove the day from its current position
        plan_days.remove(saved_day)
        
        # Insert it at the new position
        plan_days.insert(new_order, saved_day)
        
        # Update all orders
        for i, day in enumerate(plan_days):
            day.order = i

        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)