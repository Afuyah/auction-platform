from decimal import Decimal, InvalidOperation
from flask_socketio import emit, join_room
from flask import request
from app.auction.models import Auction
from .models import Bid
from flask_login import current_user
from datetime import datetime, timedelta
from app import db, socketio
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@socketio.on('join')
def on_join(data):
    auction_id = data.get('auction_id')

    if not auction_id:
        emit('error', {'message': 'Auction ID is required.'}, room=request.sid)
        logging.error(f"Missing auction_id in join request: {data}")
        return

    auction = Auction.query.get(auction_id)
    if not auction:
        emit('error', {'message': 'Auction not found.'}, room=request.sid)
        logging.error(f"Auction not found for auction_id={auction_id}")
        return

    join_room(auction_id)
    if current_user.is_authenticated:
        logging.info(f"{current_user.username} has joined auction room {auction_id}.")
        emit('status', {
            'message': f'{current_user.username} has entered the auction room.',
            'auction_id': auction_id,
            'current_price': str(auction.current_price),
            'end_time': auction.end_time.strftime('%Y-%m-%d %H:%M:%S')
        }, room=auction_id)
    else:
        logging.warning(f"Unauthenticated user tried to join auction room {auction_id}.")
        emit('error', {'message': 'Authentication required to join auction.'}, room=request.sid)

@socketio.on('bid')
def on_bid(data):
    auction_id = data.get('auction_id')
    bid_amount_str = data.get('bid_amount')

    if not auction_id:
        emit('error', {'message': 'Auction ID is required.'}, room=request.sid)
        logging.error(f"Missing auction_id in bid request: {data}")
        return

    if not bid_amount_str:
        emit('error', {'message': 'Bid amount is required.'}, room=request.sid)
        logging.error(f"Missing bid_amount in bid request: {data}")
        return

    try:
        bid_amount = Decimal(bid_amount_str)
    except InvalidOperation:
        emit('error', {'message': 'Invalid bid amount format.'}, room=request.sid)
        logging.error(f"Invalid bid amount format: {bid_amount_str}")
        return

    auction = db.session.query(Auction).with_for_update().get(auction_id)
    if auction is None:
        emit('error', {'message': 'Auction not found.'}, room=request.sid)
        logging.error(f"Auction not found for auction_id={auction_id}")
        return

    # Check if the auction has ended
    if auction.end_time < datetime.utcnow():
        emit('error', {'message': 'Auction has ended. Bidding is no longer allowed.'}, room=request.sid)
        logging.warning(f"Bid attempt on ended auction {auction_id} by user {current_user.username}.")
        return

    highest_bid = db.session.query(db.func.max(Bid.amount)).filter_by(auction_id=auction_id).scalar() or auction.current_price
    highest_bid = Decimal(highest_bid)

    if bid_amount <= highest_bid:
        emit('bid_status', {
            'success': False,
            'message': 'Bid amount must be higher than the current price.',
            'current_price': str(highest_bid)
        }, room=request.sid)
        return

    try:
        # Extend auction if bid is placed in the last 30 seconds
        if (auction.end_time - datetime.utcnow()) <= timedelta(seconds=30):
            auction.end_time += timedelta(minutes=2)
            emit('auction_extended', {
                'new_end_time': auction.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'message': 'Auction extended due to late bid.'
            }, room=auction_id)

        # Start the transaction
        bid = Bid(amount=bid_amount, user_id=current_user.id, auction_id=auction_id)
        auction.current_price = bid_amount

        db.session.add(bid)
        db.session.commit()

        # Notify the user who placed the bid
        emit('bid_status', {
            'success': True,
            'message': 'Bid placed successfully!',
            'new_bid_amount': str(bid_amount),
            'username': current_user.username,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room=request.sid)

        # Notify the entire room about the new bid
        emit('bid_status', {
            'success': True,
            'message': f'{current_user.username} placed a bid of {bid_amount}.',
            'new_bid_amount': str(bid_amount)
        }, room=auction_id)

        logging.info(f"{current_user.username} placed a bid of {bid_amount} on auction {auction_id}.")

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error processing bid: {traceback.format_exc()}")
        emit('error', {'message': 'An error occurred while placing the bid.'}, room=request.sid)
