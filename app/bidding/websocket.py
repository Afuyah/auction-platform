from decimal import Decimal, InvalidOperation
from flask_socketio import emit, join_room
from flask import request
from app.auction.models import Auction
from .models import Bid, AuditLog
from flask_login import current_user
from datetime import datetime, timedelta
from app import db, socketio
import logging
import traceback


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_audit_log(user_id, action_type, description):
    try:
        audit_log = AuditLog(user_id=user_id, action_type=action_type, description=description)
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error creating audit log: {traceback.format_exc()}")

@socketio.on('join')
def on_join(data):
    auction_id = data.get('auction_id')

    if not auction_id:
        emit('error', {'message': 'Auction ID is required.'}, room=request.sid)
        logging.error(f"Missing auction_id in join request: {data}")
        create_audit_log(current_user.id if current_user.is_authenticated else None, 'JOIN_FAILED', f"Missing auction_id: {data}")
        return

    auction = Auction.query.get(auction_id)
    if not auction:
        emit('error', {'message': 'Auction not found.'}, room=request.sid)
        logging.error(f"Auction not found for auction_id={auction_id}")
        create_audit_log(current_user.id if current_user.is_authenticated else None, 'JOIN_FAILED', f"Auction not found for auction_id={auction_id}")
        return

    join_room(auction_id)
    if current_user.is_authenticated:
        logging.info(f"{current_user.id} Joined {auction_id}.")
        create_audit_log(current_user.id, 'JOIN_SUCCESS', f"Joined auction room {auction_id}.")
        emit('status', {
            'message': f'{current_user.id} Entered The Room.',
            'auction_id': auction_id,
            'current_price': str(auction.current_price),
            'end_time': auction.end_time.strftime('%Y-%m-%d %H:%M:%S')
        }, room=auction_id)
    else:
        logging.warning(f"Unauthenticated user tried to join auction room {auction_id}.")
        emit('error', {'message': 'Authentication required to join auction.'}, room=request.sid)
        create_audit_log(None, 'JOIN_FAILED', f"Unauthenticated attempt to join auction room {auction_id}.")

@socketio.on('bid')
def on_bid(data):
    auction_id = data.get('auction_id')
    bid_amount_str = data.get('bid_amount')

    if not auction_id:
        emit('error', {'message': 'Auction ID is required.'}, room=request.sid)
        logging.error(f"Missing auction_id in bid request: {data}")
        create_audit_log(current_user.id if current_user.is_authenticated else None, 'BID_FAILED', 'Missing auction_id')
        return

    if not bid_amount_str:
        emit('error', {'message': 'Bid amount is required.'}, room=request.sid)
        logging.error(f"Missing bid_amount in bid request: {data}")
        create_audit_log(current_user.id if current_user.is_authenticated else None, 'BID_FAILED', 'Missing bid_amount')
        return

    try:
        bid_amount = Decimal(bid_amount_str)
    except InvalidOperation:
        emit('error', {'message': 'Invalid bid amount format.'}, room=request.sid)
        logging.error(f"Invalid bid amount format: {bid_amount_str}")
        create_audit_log(current_user.id if current_user.is_authenticated else None, 'BID_FAILED', f"Invalid bid amount format: {bid_amount_str}")
        return

    auction = db.session.query(Auction).with_for_update().get(auction_id)
    if auction is None:
        emit('error', {'message': 'Auction not found.'}, room=request.sid)
        logging.error(f"Auction not found for auction_id={auction_id}")
        create_audit_log(current_user.id if current_user.is_authenticated else None, 'BID_FAILED', f"Auction not found for auction_id={auction_id}")
        return

    if auction.end_time < datetime.utcnow():
        emit('error', {'message': 'Auction has ended. Bid Not allowed.'}, room=request.sid)
        logging.warning(f"Bid attempt on ended auction {auction_id} by user {current_user.username}.")
        create_audit_log(current_user.id, 'BID_FAILED', f"Auction has ended. Bid attempt by {current_user.username}.")
        return

    highest_bid = db.session.query(db.func.max(Bid.amount)).filter_by(auction_id=auction_id).scalar() or auction.current_price
    highest_bid = Decimal(highest_bid)

    if bid_amount <= highest_bid:
        emit('bid_status', {
            'success': False,
            'message': 'Bid amount less than Highest Bid.',
            'current_price': str(highest_bid)
        }, room=request.sid)
        create_audit_log(current_user.id, 'BID_FAILED', f"Bid amount {bid_amount} not higher than current price {highest_bid}.")
        return

    try:
        if (auction.end_time - datetime.utcnow()) <= timedelta(seconds=30):
            auction.end_time += timedelta(minutes=2)
            emit('auction_extended', {
                'new_end_time': auction.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'message': 'Auction extended due to late bid.'
            }, room=auction_id)

        bid = Bid(amount=bid_amount, user_id=current_user.id, auction_id=auction_id)
        auction.current_price = bid_amount

        db.session.add(bid)
        db.session.commit()

        emit('bid_status', {
            'success': True,
            'message': 'Bid placed!',
            'new_bid_amount': str(bid_amount),
            'username': current_user.username,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }, room=request.sid)

        emit('bid_status', {
            'success': True,
            'message': f'{current_user.id}  Bid  {bid_amount}.',
            'new_bid_amount': str(bid_amount)
        }, room=auction_id)

        logging.info(f"{current_user.username} placed a bid of {bid_amount} on auction {auction_id}.")
        create_audit_log(current_user.id, 'BID_SUCCESS', f"Placed bid of {bid_amount} on auction {auction_id}.")

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error processing bid: {traceback.format_exc()}")
        emit('error', {'message': 'An error occurred while placing the bid.'}, room=request.sid)
        create_audit_log(current_user.id if current_user.is_authenticated else None, 'BID_FAILED', f"Error occurred while placing bid: {traceback.format_exc()}")
