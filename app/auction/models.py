from app import db
from datetime import datetime

class Auction(db.Model):
    __tablename__ = 'auctions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    starting_price = db.Column(db.Numeric(10, 2), nullable=False)
    current_price = db.Column(db.Numeric(10, 2), nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='auctions')
    items = db.relationship('Item', back_populates='auction', cascade='all, delete-orphan')
    bids = db.relationship('Bid', back_populates='auction')  # Added relationship to Bid

    def __repr__(self):
        return f'<Auction {self.title}>'

    @property
    def is_active(self):
        return self.status == 'Active' and self.end_time > datetime.utcnow()


class Item(db.Model):
    __tablename__ = 'items'  # Ensure the table name is defined

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    provenance_origin = db.Column(db.String(100))
    provenance_previous_ownership = db.Column(db.Text)
    authentication_details = db.Column(db.Text)
    certificates = db.Column(db.Text)
    dimensions = db.Column(db.String(100))
    material = db.Column(db.String(100))
    rarity = db.Column(db.String(100))
    edition = db.Column(db.String(100))
    starting_bid = db.Column(db.Numeric(10, 2), nullable=False)
    reserve_price = db.Column(db.Numeric(10, 2))
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)  # Corrected foreign key reference
    photos = db.Column(db.JSON)
    status = db.Column(db.String(20), default='Pending Verification')
    auction = db.relationship('Auction', back_populates='items')

    def __repr__(self):
        return f'<Item {self.title}>'
