from flask_login import current_user
from website.models.saved_models import SavedPlan

def get_saved_plan(plan_id):
    """
    Get a saved plan and verify user is the owner
    """
    plan = SavedPlan.query.get_or_404(plan_id)
    if plan.user_id != current_user.id:
        raise PermissionError("Unauthorized plan access")
    return plan