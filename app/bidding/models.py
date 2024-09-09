from app import db
from datetime import datetime

class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # Use Decimal for monetary values
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    auction = db.relationship('Auction', back_populates='bids')
    user = db.relationship('User', back_populates='bids')

    # Indexes and constraints
    __table_args__ = (
        db.Index('idx_auction_id', 'auction_id'),
        db.Index('idx_user_id', 'user_id'),
        db.CheckConstraint('amount > 0', name='check_bid_amount_positive'),
    )

    def __repr__(self):
        return f'<Bid {self.id} for Auction {self.auction_id}>'
    
    def is_highest_bid(self):
        # Get the highest bid for this auction
        highest_bid = db.session.query(db.func.max(Bid.amount)).filter_by(auction_id=self.auction_id).scalar()
        return self.amount == highest_bid


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action_type = db.Column(db.String(50))
    description = db.Column(db.Text)

    user = db.relationship('User', backref='audit_logs')

    def __init__(self, user_id, action_type, description):
        self.user_id = user_id
        self.action_type = action_type
        self.description = description
