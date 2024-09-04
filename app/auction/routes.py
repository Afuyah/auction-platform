from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Auction, Item
from app.bidding.models import Bid
from .forms import AuctionForm
from app import db

auction_bp = Blueprint('auction', __name__)

@auction_bp.route('/')
def index():
    try:
        auctions = Auction.query.all()
        return render_template('index.html', auctions=auctions)
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return render_template('index.html', auctions=[])

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
            flash('Auction created successfully and is pending approval!')
            return redirect(url_for('auction.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}')
    return render_template('auction/create_auction.html', form=form)

@auction_bp.route('/<int:auction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    if auction.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this auction.')
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
            flash('Auction updated successfully!')
            return redirect(url_for('auction.auction_detail', auction_id=auction.id))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}')
    return render_template('auction/edit_auction.html', form=form, auction=auction)

@auction_bp.route('/<int:auction_id>/delete', methods=['POST'])
@login_required
def delete_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    if auction.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this auction.')
        return redirect(url_for('auction.index'))

    try:
        db.session.delete(auction)
        db.session.commit()
        flash('Auction deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}')
    return redirect(url_for('auction.index'))

@auction_bp.route('/<int:auction_id>/activate', methods=['POST'])
@login_required
def activate_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    if not current_user.is_admin:
        flash('You do not have permission to activate this auction.')
        return redirect(url_for('auction.index'))
    
    auction.status = 'Active'
    try:
        db.session.commit()
        flash('Auction activated and open for bidding!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}')
    return redirect(url_for('auction.auction_detail', auction_id=auction.id))

@auction_bp.route('/<int:auction_id>/deactivate', methods=['POST'])
@login_required
def deactivate_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    if not current_user.is_admin:
        flash('You do not have permission to deactivate this auction.')
        return redirect(url_for('auction.index'))
    
    auction.status = 'Inactive'
    try:
        db.session.commit()
        flash('Auction deactivated!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}')
    return redirect(url_for('auction.auction_detail', auction_id=auction.id))

@auction_bp.route('/<int:auction_id>')
def auction_detail(auction_id):
    try:
        auction = Auction.query.get_or_404(auction_id)
        items = Item.query.filter_by(auction_id=auction_id).all()
        return render_template('auction/details.html', auction=auction, items=items)
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('auction.index'))

@auction_bp.route('/<int:auction_id>/finalize', methods=['POST'])
@login_required
def finalize_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    if auction.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to finalize this auction.')
        return redirect(url_for('auction.index'))

    try:
        for item in auction.items:
            highest_bid = get_highest_bid(item)  # Implement this function based on your bidding logic
            if item.reserve_price and highest_bid < item.reserve_price:
                item.status = 'Unsold'
                flash(f'Item {item.title} did not meet the reserve price and was not sold.')
            else:
                item.status = 'Sold'
                flash(f'Item {item.title} was sold for ${highest_bid}.')
        db.session.commit()
        flash('Auction finalized!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}')
    return redirect(url_for('auction.auction_detail', auction_id=auction.id))

@auction_bp.route('/dashboard')
@login_required
def dashboard():
    user_auctions = Auction.query.filter_by(user_id=current_user.id).all()
    user_bids = Bid.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', user_auctions=user_auctions, user_bids=user_bids)




