# helpers.py or directly in your views.py

from app.auction.models import Category, Type

def get_categories():
    """Fetch categories from the database and return as a list of tuples."""
    return [(c.id, c.name) for c in Category.query.all()]

def get_types():
    """Fetch types from the database and return as a list of tuples."""
    return [(t.id, t.name) for t in Type.query.all()]
