from flask_socketio import SocketIO, emit, join_room
from .models import Auction, Bid
from flask_login import current_user
from datetime import datetime
from app import db

socketio = SocketIO()

@socketio.on('join')
def on_join(data):
    auction_id = data.get('auction_id')
    
    if not auction_id:
        emit('error', {'message': 'Auction ID is required.'})
        return
    
    auction = Auction.query.get(auction_id)
    if not auction:
        emit('error', {'message': 'Auction not found.'})
        return

    join_room(auction_id)
    emit('status', {
        'message': f'{current_user.username} has entered the auction room.',
        'auction_id': auction_id,
        'current_price': auction.current_price
    }, room=auction_id)

    # Notify existing users in the room that a new user has joined
    emit('status', {
        'message': f'{current_user.username} has joined the auction.',
        'username': current_user.username
    }, room=auction_id)

@socketio.on('bid')
def on_bid(data):
    auction_id = data.get('auction_id')
    amount = data.get('amount')

    if not auction_id or not isinstance(amount, (int, float)) or amount <= 0:
        emit('error', {'message': 'Invalid bid data.'})
        return

    auction = Auction.query.get(auction_id)
    if not auction:
        emit('error', {'message': 'Auction not found.'})
        return

    # Ensure the bid amount is higher than the current price
    if amount <= auction.current_price:
        emit('bid_failed', {'message': 'Bid amount must be higher than the current price.'}, room=request.sid)
        return

    try:
        # Record the bid
        bid = Bid(amount=amount, user_id=current_user.id, auction_id=auction_id)
        auction.current_price = amount
        db.session.add(bid)
        db.session.commit()

        # Notify all users in the auction room of the new bid
        emit('new_bid', {
            'amount': amount,
            'username': current_user.username,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'current_price': auction.current_price
        }, room=auction_id)

        # Optionally, notify the current user of their successful bid
        emit('status', {
            'message': f'Your bid of {amount} was successful!',
            'username': current_user.username,
            'current_price': auction.current_price
        }, room=request.sid)

    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        emit('error', {'message': 'An error occurred while processing your bid.'})

