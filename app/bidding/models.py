from app import db
from datetime import datetime

class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    auction = db.relationship('Auction', back_populates='bids')
    user = db.relationship('User', back_populates='bids')

    __table_args__ = (
        db.Index('idx_auction_id', 'auction_id'),
        db.Index('idx_user_id', 'user_id'),
        db.CheckConstraint('amount > 0', name='check_bid_amount_positive'),
    )

    def __repr__(self):
        return f'<Bid {self.id} for Auction {self.auction_id}>'
    
    def is_highest_bid(self):
        highest_bid = db.session.query(db.func.max(Bid.amount)).filter_by(auction_id=self.auction_id).scalar()
        return self.amount == highest_bid
