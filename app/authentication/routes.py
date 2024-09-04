from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_mail import Message
from app import mail,db  
from .forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from .models import User
from flask_login import login_user, logout_user, login_required, current_user


auth_bp = Blueprint('auth', __name__)

def send_email(subject, recipient, template, **kwargs):
    msg = Message(subject, recipients=[recipient], sender=current_app.config['MAIL_DEFAULT_SENDER'])
    msg.body = render_template(template, **kwargs)
    mail.send(msg)

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

        # Send activation email
        token = user.activation_token  # Corrected: Accessing the attribute directly
        send_email(
            'Activate Your Account',
            user.email,
            'email/activate_account.txt',
            user=user,
            token=token
        )
        
        flash('Your account has been created! Please check your email to activate your account.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('authentication/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auction.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.active:
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('auction.index'))
            else:
                flash('Account not activated. Please check your email.', 'warning')
        else:
            flash('Login unsuccessful. Please check your username and password', 'danger')
    return render_template('authentication/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auction.index'))

@auth_bp.route('/activate/<token>')
def activate_account(token):
    user = User.verify_activation_token(token)
    if user is None:
        flash('Invalid or expired token', 'warning')
    elif user.active:
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
            token = user.get_reset_token()
            send_email(
                'Reset Your Password',
                user.email,
                'email/reset_password_request.txt',
                user=user,
                token=token
            )
            flash('A password reset email has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('The reset token is invalid or has expired.', 'warning')
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)
