from decimal import Decimal
from flask_socketio import emit, join_room
from flask import request
from app.auction.models import Auction
from .models import Bid
from flask_login import current_user
from datetime import datetime
from app import db, socketio
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)

@socketio.on('join')
def on_join(data):
    auction_id = data.get('auction_id')

    if not auction_id:
        emit('error', {'message': 'Auction ID is required.'})
        logging.error(f"Missing auction_id in join request: {data}")
        return

    auction = Auction.query.get(auction_id)
    if not auction:
        emit('error', {'message': 'Auction not found.'})
        logging.error(f"Auction not found for auction_id={auction_id}")
        return

    join_room(auction_id)
    logging.info(f"{current_user.username} has joined auction room {auction_id}.")

    # Notify the room about the new participant
    emit('status', {
        'message': f'{current_user.username} has entered the auction room.',
        'auction_id': auction_id,
        'current_price': str(auction.current_price)
    }, room=auction_id)

@socketio.on('bid')
def on_bid(data):
    auction_id = data.get('auction_id')

    if not auction_id:
        emit('error', {'message': 'Auction ID is required.'})
        logging.error(f"Missing auction_id in bid request: {data}")
        return

    auction = Auction.query.get(auction_id)
    if not auction:
        emit('error', {'message': 'Auction not found.'})
        logging.error(f"Auction not found for auction_id={auction_id}")
        return

    try:
        current_price = Decimal(auction.current_price)
        highest_bid = db.session.query(db.func.max(Bid.amount)).filter_by(auction_id=auction_id).scalar() or current_price
        highest_bid = Decimal(highest_bid)

        increment = Decimal('0.10')  # 10% increment
        new_bid_amount = highest_bid + (highest_bid * increment)

        if current_price >= new_bid_amount:
            emit('bid_status', {
                'success': False,
                'message': 'Bid amount must be higher than the current price.',
                'current_price': str(current_price)
            }, room=request.sid)
            return

        # Start the transaction
        bid = Bid(amount=new_bid_amount, user_id=current_user.id, auction_id=auction_id)
        auction.current_price = new_bid_amount
        
        # Add the new bid and update the auction price
        db.session.add(bid)
        db.session.commit()  # Commit the changes

        # Emit the success response to the auction room
        emit('bid_status', {
            'success': True,
            'message': 'Bid placed successfully!',
            'new_bid_amount': str(new_bid_amount),
            'username': current_user.username,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room=auction_id)

    except Exception as e:
        db.session.rollback()  # Rollback the transaction if something goes wrong
        logging.error(f"Error processing bid: {traceback.format_exc()}")
        emit('error', {'message': 'An error occurred while placing the bid.'})