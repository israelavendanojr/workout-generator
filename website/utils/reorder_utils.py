from website import db

def get_max_order(model, filter_field, filter_value):
    """
    Get the maximum order value for a given model and filter condition
    """
    return db.session.query(db.func.max(model.order)).filter_by(**{filter_field: filter_value}).scalar() or -1

def update_order_after_delete(model, filter_field, filter_value, deleted_order):
    """
    Update the order of remaining items after a deletion
    """
    remaining_items = model.query.filter(
        getattr(model, filter_field) == filter_value,
        model.order > deleted_order
    ).all()

    for item in remaining_items:
        item.order -= 1
        
def reorder_items(items, moved_item, new_position):
    """
    Reorder a list of items by removing an item and inserting it at a new position
    """
    # Remove the item from its current position
    items.remove(moved_item)
    
    # Insert it at the new position
    items.insert(new_position, moved_item)
    
    # Update all orders
    for i, item in enumerate(items):
        item.order = i
    
    return items