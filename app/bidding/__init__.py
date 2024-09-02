from flask import Blueprint
bid_bp = Blueprint('bid', __name__, url_prefix = '/bid')

def create_bid_blueprint():
    
    return bid_bp