from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class AuctionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    starting_price = DecimalField('Starting Price', validators=[DataRequired(), NumberRange(min=0)])
    end_time = DateTimeField('End Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Submit')