from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from app.models import Auction

class BidForm(FlaskForm):
    amount = DecimalField('Bid Amount', places=2, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Place Bid')
    
    
   c          auction_id = None  # Placeholder; adjust based on how you manage auction_id

    def __init__(self, *args, **kwargs):
        self.auction_id = kwargs.pop('auction_id', None)
        super().__init__(*args, **kwargs)
    
    def validate_amount(self, field):
        if self.auction_id is None:
            raise ValidationError('Auction ID is required for validation.')
        
        auction = Auction.query.get(self.auction_id)
        if not auction:
            raise ValidationError('Auction not found.')
        
        if field.data <= auction.current_price:
            raise ValidationError('Bid amount must be higher than the current auction price.')
