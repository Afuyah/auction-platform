from app import db
from datetime import datetime
from sqlalchemy.sql import and_
from app import db

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
    is_featured = db.Column(db.Boolean, default=False)  # Add this line

    # Relationships
    user = db.relationship('User', back_populates='auctions')
    bids = db.relationship('Bid', back_populates='auction', cascade='all, delete-orphan')
    items = db.relationship('Item', back_populates='auction', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Auction {self.title}>'


    @property
    def is_active(self):
        return self.status == 'Active' and self.end_time > datetime.utcnow()
    @classmethod
    def get_active_auctions(cls):
        return cls.query.filter(
            and_(
                cls.status == 'Active',
                cls.end_time > datetime.utcnow()
            )
        ).all()
    

    def activate(self):
        if self.end_time > datetime.utcnow():
            self.status = 'Active'
        else:
            raise ValueError("Cannot activate an auction that has already ended.")

    def deactivate(self):
        self.status = 'Inactive'
        self.end_time = datetime.utcnow()

    @property
    def is_completed(self):
        return datetime.utcnow() >= self.end_time


    

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Foreign keys to Type and Category tables
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    condition_id = db.Column(db.Integer, db.ForeignKey('conditions.id'), nullable=True)
    
    # Additional optional fields
    condition = db.Column(db.String(50), nullable=True)  
    provenance_origin = db.Column(db.String(100), nullable=True)  
    provenance_previous_ownership = db.Column(db.Text, nullable=True)  
    authentication_details = db.Column(db.Text, nullable=True)  
    certificates = db.Column(db.Text, nullable=True)  
    dimensions = db.Column(db.String(100), nullable=True)  
    material = db.Column(db.String(100), nullable=True)  
    rarity = db.Column(db.String(100), nullable=True)  
    edition = db.Column(db.String(100), nullable=True)  
    
    # Financial fields
    starting_bid = db.Column(db.Numeric(10, 2), nullable=False)
    reserve_price = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Foreign key to Auction
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=True)
    
    # JSON field for storing multiple photo links
    photos = db.Column(db.JSON, nullable=True)  
    
    # Item status (Pending Verification by default)
    status = db.Column(db.String(20), default='Pending Verification')

    # Relationships
    auction = db.relationship('Auction', back_populates='items')
    type = db.relationship('Type', back_populates='items')
    category = db.relationship('Category', back_populates='items')
    condition = db.relationship('Condition', back_populates='items')
    
    def __repr__(self):
        return f'<Item {self.title}>'


class Type(db.Model):
    __tablename__ = 'types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationship to Item
    items = db.relationship('Item', back_populates='type')

    def __repr__(self):
        return f'<Type {self.name}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationship to Item
    items = db.relationship('Item', back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'


class Condition(db.Model):
    __tablename__ = 'conditions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Relationship to Item
    items = db.relationship('Item', back_populates='condition')

    def __repr__(self):
        return f'<Condition {self.name}>'
