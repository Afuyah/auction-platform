from flask import Blueprint
item_bp = Blueprint('item', __name__, url_prefix = '/item')

def create_bid_blueprint():
    
    return item_bp