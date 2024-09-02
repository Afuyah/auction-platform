
from app import db

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=False)

    user = db.relationship('User', back_populates='bids')
    auction = db.relationship('Auction', back_populates='bids')

    def __repr__(self):
        return f'<Bid {self.amount} by User {self.user_id}>'
