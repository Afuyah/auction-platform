from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class BidForm(FlaskForm):
    amount = DecimalField('Bid Amount', places=2, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Place Bid')
