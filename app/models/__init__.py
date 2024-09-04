# app/models/__init__.py
from app import db

# Import models
from app.authentication.models import User
from app.bidding.models import Bid
from app.auction.models import Auction
