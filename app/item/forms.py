from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, MultipleFileField, SubmitField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Add Category')

class TypeForm(FlaskForm):
    name = StringField('Type Name', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Add Type')


class ItemDetailsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, choices=[], validators=[DataRequired()])
    type = SelectField('Type', coerce=int, choices=[], validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired()])
    provenance_origin = StringField('Provenance Origin', validators=[Optional()])
    provenance_previous_ownership = TextAreaField('Provenance Previous Ownership', validators=[Optional()])
    authentication_details = TextAreaField('Authentication Details', validators=[Optional()])
    certificates = TextAreaField('Certificates', validators=[Optional()])
    # Hidden fields to store data across steps
    current_step = HiddenField('current_step', default='1')
    submit = SubmitField('Next')

class ItemSpecificationsForm(FlaskForm):
    dimensions = StringField('Dimensions', validators=[Optional()])
    material = StringField('Material', validators=[Optional()])
    rarity = StringField('Rarity', validators=[Optional()])
    edition = StringField('Edition', validators=[Optional()])
    # Hidden fields to store data across steps
    current_step = HiddenField('current_step', default='2')
    submit = SubmitField('Next')

class ItemFinancialForm(FlaskForm):
    starting_bid = DecimalField('Starting Bid', places=2, validators=[DataRequired()])
    reserve_price = DecimalField('Reserve Price', places=2, validators=[Optional()])
    photos = MultipleFileField('Photos', validators=[Optional()])
    # Hidden fields to store data across steps
    current_step = HiddenField('current_step', default='3')
    submit = SubmitField('Submit')
