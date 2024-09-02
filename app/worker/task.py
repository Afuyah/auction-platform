from app import  db, mail, celery
from flask_mail import Message
from app.models import Auction, User


@celery.task(bind=True, max_retries=3, default_retry_delay=300)
def close_auction(self, auction_id):
    try:
        with app.app_context():
            # Fetch the auction and perform the closing logic
            auction = Auction.query.get(auction_id)
            if not auction:
                raise ValueError("Auction not found")
            
            # Example logic to close the auction
            auction.is_closed = True
            db.session.commit()

            # Notify users about the auction closure
            users = User.query.filter_by(subscribed_to_notifications=True).all()
            for user in users:
                msg = Message('Auction Closed', recipients=[user.email])
                msg.body = f'The auction for {auction.title} has been closed.'
                mail.send(msg)
    except Exception as e:
        # Retry the task in case of failure
        raise self.retry(exc=e)
