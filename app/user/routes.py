from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_mail import Message
from app.authentication.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Bid, Auction

from app import mail 

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    user_auctions = current_user.auctions  # Assuming you have a relationship defined in your User model
    user_bids = Bid.query.filter_by(user_id=current_user.id).all()  # Assuming Bid is a model that stores bids

    return render_template('dashboard.html', user_auctions=user_auctions, user_bids=user_bids)


# In your user/routes.py or equivalent file

@user_bp.route('/notifications')
@login_required
def notifications():
    # Your logic here
    return render_template('notification/notifications.html')

