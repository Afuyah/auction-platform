from app import create_app, mail
from flask_mail import Message
from app import db, celery

@celery.task(bind=True, max_retries=3, default_retry_delay=300)
def send_auction_end_notification(self, user_email, auction_title):
    try:
        msg = Message('Auction Ended', recipients=[user_email])
        msg.body = f'The auction for {auction_title} has ended.'
        with app.app_context():
            mail.send(msg)
    except Exception as e:
        raise self.retry(exc=e)
