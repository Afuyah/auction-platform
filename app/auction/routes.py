from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_required, current_user
from .models import Auction, Item
from app.bidding.models import Bid
from .forms import AuctionForm
from app import db
from sqlalchemy.sql import and_
from datetime import datetime
import os
import logging
auction_bp = Blueprint('auction', __name__)

@auction_bp.route('/auction-room/<int:auction_id>')
def auction_room(auction_id):
    try:
        # Fetch the auction object
        auction = Auction.query.get_or_404(auction_id)
        # Pass the auction ID to the template
        return render_template('auction/auction_room.html', auction_id=auction_id, auction=auction)
    except Exception as e:
        # Log the error and flash a message to the user
        logging.error(f'Error fetching auction {auction_id}: {str(e)}')
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('auction.index'))



@auction_bp.route('/', defaults={'view': 'all'})
@auction_bp.route('/<view>')
def index(view):
    try:
        if view == 'featured':
            # Fetch only featured auctions
            featured_auctions = Auction.query.filter_by(is_featured=True).all()
            return render_template('featured_auctions.html', featured_auctions=featured_auctions)
        else:
            # Fetch all auctions
            auctions = Auction.query.all()
            return render_template('home.html', auctions=auctions)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('home.html', auctions=[])


@auction_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_auction():
    form = AuctionForm()
    if form.validate_on_submit():
        auction = Auction(
            title=form.title.data,
            description=form.description.data,
            starting_price=form.starting_price.data,
            current_price=form.starting_price.data,
            end_time=form.end_time.data,
            status='Pending',
            user_id=current_user.id
        )
        try:
            db.session.add(auction)
            db.session.commit()
            flash('Auction created successfully and is pending approval!', 'success')
            return redirect(url_for('auction.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    return render_template('auction/create_auction.html', form=form)

@auction_bp.route('/<int:auction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    if auction.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this auction.', 'warning')
        return redirect(url_for('auction.index'))
    
    form = AuctionForm(obj=auction)
    if form.validate_on_submit():
        auction.title = form.title.data
        auction.description = form.description.data
        auction.starting_price = form.starting_price.data
        auction.current_price = form.starting_price.data
        auction.end_time = form.end_time.data
        try:
            db.session.commit()
            flash('Auction updated successfully!', 'success')
            return redirect(url_for('auction.auction_detail', auction_id=auction.id))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    return render_template('auction/edit_auction.html', form=form, auction=auction)

@auction_bp.route('/<int:auction_id>/delete', methods=['POST'])
@login_required
def delete_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    if auction.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this auction.', 'warning')
        return redirect(url_for('auction.index'))

    try:
        db.session.delete(auction)
        db.session.commit()
        flash('Auction deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('auction.index'))

@auction_bp.route('/<int:auction_id>')
def auction_detail(auction_id):
    try:
        auction = Auction.query.get_or_404(auction_id)
        items = Item.query.filter_by(auction_id=auction_id).all()
        return render_template('auction/details.html', auction=auction, items=items)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('auction.index'))

@auction_bp.route('/<int:auction_id>/finalize', methods=['POST'])
@login_required
def finalize_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    if auction.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to finalize this auction.', 'warning')
        return redirect(url_for('auction.index'))

    try:
        for item in auction.items:
            highest_bid = get_highest_bid(item)  # Ensure this function is defined
            if item.reserve_price and highest_bid < item.reserve_price:
                item.status = 'Unsold'
                flash(f'Item {item.title} did not meet the reserve price and was not sold.', 'warning')
            else:
                item.status = 'Sold'
                flash(f'Item {item.title} was sold for ${highest_bid}.', 'success')
        db.session.commit()
        flash('Auction finalized!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('auction.auction_detail', auction_id=auction.id))

@auction_bp.route('/dashboard')
@login_required
def dashboard():
    user_auctions = Auction.query.filter_by(user_id=current_user.id).all()
    user_bids = Bid.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', user_auctions=user_auctions, user_bids=user_bids)

@auction_bp.route('/ongoing-auctions')
def ongoing_auctions():
    # Fetch ongoing auctions directly
    auctions = Auction.query.filter(
        and_(
            Auction.status == 'Active',
            Auction.end_time > datetime.utcnow()
        )
    ).all()
    return render_template('auction/ongoing_auctions.html', auctions=auctions)

@auction_bp.route('/featured')
def featured_auctions():
    try:
        # Fetch all featured auctions
        featured_auctions = Auction.query.filter_by(is_featured=True).all()
        return render_template('index.html', featured_auctions=featured_auctions)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('index.html', featured_auctions=[])

