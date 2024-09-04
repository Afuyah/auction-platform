    from wtforms import ValidationError

    class BidForm(FlaskForm):
        amount = DecimalField('Bid Amount', places=2, validators=[DataRequired(), NumberRange(min=0)])
        submit = SubmitField('Place Bid')

        def validate_amount(self, field):
            auction = Auction.query.get(self.auction_id)
            if auction and field.data <= auction.current_price:
                raise ValidationError('Bid amount must be higher than the current auction price.')

