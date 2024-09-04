from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Optional

class ItemDetailsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired()])
    provenance_origin = StringField('Provenance Origin', validators=[Optional()])
    provenance_previous_ownership = TextAreaField('Provenance Previous Ownership', validators=[Optional()])
    authentication_details = TextAreaField('Authentication Details', validators=[Optional()])
    certificates = TextAreaField('Certificates', validators=[Optional()])
    submit = SubmitField('Next')

class ItemSpecificationsForm(FlaskForm):
    dimensions = StringField('Dimensions', validators=[Optional()])
    material = StringField('Material', validators=[Optional()])
    rarity = StringField('Rarity', validators=[Optional()])
    edition = StringField('Edition', validators=[Optional()])
    submit = SubmitField('Next')

class ItemFinancialForm(FlaskForm):
    starting_bid = DecimalField('Starting Bid', places=2, validators=[DataRequired()])
    reserve_price = DecimalField('Reserve Price', places=2, validators=[Optional()])
    photos = MultipleFileField('Photos', validators=[Optional()])
    submit = SubmitField('Submit')
