from flask import Blueprint, render_template, redirect, url_for, flash, request
from .forms import RegistrationForm, LoginForm
from .models import User, db
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Please check your email to activate your account.', 'success')
        # Send activation email here with user.activation_token
        return redirect(url_for('auth.login'))
    return render_template('authentication/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.active:
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
            else:
                flash('Account not activated. Please check your email.', 'warning')
        else:
            flash('Login unsuccessful. Please check your username and password', 'danger')
    return render_template('authentication/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth_bp.route('/activate/<token>')
def activate_account(token):
    user = User.query.filter_by(activation_token=token).first_or_404()
    if user.active:
        flash('Account already activated.', 'info')
    else:
        user.activate_account()
        db.session.commit()
        flash('Account activated! You can now log in.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            user.generate_reset_token()
            db.session.commit()
            # Send email with user.reset_token
            flash('A password reset email has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(reset_token=token).first_or_404()
    if not user.verify_reset_token(token):
        flash('The reset token is invalid or has expired.', 'warning')
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None  # Invalidate the token
        user.reset_token_expiry = None
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)
