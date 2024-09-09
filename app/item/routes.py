import os
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.auction.models import Item,Category, Type, Condition
from .forms import ItemDetailsForm, ItemSpecificationsForm, ItemFinancialForm, CategoryForm, TypeForm, ConditionForm
from app import db
from .helpers import get_categories, get_types 

item_bp = Blueprint('item', __name__)

UPLOAD_FOLDER = 'static/images/auc'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if a file is allowed based on its extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_photos(files):
    """Handle file uploads and save them to the upload folder."""
    photos = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                file.save(file_path)
                photos.append(filename)
            except Exception as e:
                logging.error(f'Error saving file {filename}: {e}', exc_info=True)
                flash(f'Failed to upload file {filename}. Please try again.')
    return photos

@item_bp.route('/add-category', methods=['GET', 'POST'])
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        # Check if category already exists
        existing_category = Category.query.filter_by(name=form.name.data).first()
        if existing_category:
            flash(f'Category "{form.name.data}" already exists.', 'warning')
        else:
            category = Category(name=form.name.data)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('item.add_category'))
    return render_template('items/add_category.html', form=form)


@item_bp.route('/add-type', methods=['GET', 'POST'])
def add_type():
    form = TypeForm()
    if form.validate_on_submit():
        type_ = Type(name=form.name.data)
        db.session.add(type_)
        db.session.commit()
        flash('Type added successfully!', 'success')
        return redirect(url_for('item.add_type'))
    return render_template('items/add_type.html', form=form)


@item_bp.route('/add-condition', methods=['GET', 'POST'])
@login_required
def add_condition():
    form = ConditionForm()
    if form.validate_on_submit():
        # Check if condition already exists
        existing_condition = Condition.query.filter_by(name=form.name.data).first()
        if existing_condition:
            flash(f'Condition "{form.name.data}" already exists.', 'warning')
        else:
            # Create new condition and add to the database
            condition = Condition(name=form.name.data)
            db.session.add(condition)
            db.session.commit()
            flash('Condition added successfully!', 'success')
            return redirect(url_for('item.add_condition'))

    return render_template('items/add_condition.html', form=form)




@item_bp.route('/add-item', methods=['GET', 'POST'])
@login_required
def add_item():
    step = int(request.args.get('step', '1'))

    if step == 1:
        form = ItemDetailsForm()
        form.category.choices = get_categories()  # Populate categories
        form.type.choices = get_types()  # Populate types
        form.condition.choices = [(c.id, c.name) for c in Condition.query.all()]
        if form.validate_on_submit():
            session['item_data'] = {
                'title': form.title.data,
                'description': form.description.data,
                'category': form.category.data,  # Storing ID
                'type': form.type.data,          # Storing ID
                'condition': form.condition.data,  # Storing ID
                'provenance_origin': form.provenance_origin.data,
                'provenance_previous_ownership': form.provenance_previous_ownership.data,
                'authentication_details': form.authentication_details.data,
                'certificates': form.certificates.data,
            }
            return redirect(url_for('item.add_item', step=2))
    
    elif step == 2:
        form = ItemSpecificationsForm()
        if form.validate_on_submit():
            session['item_data'].update({
                'dimensions': form.dimensions.data,
                'material': form.material.data,
                'rarity': form.rarity.data,
                'edition': form.edition.data,
            })
            return redirect(url_for('item.add_item', step=3))
    
    elif step == 3:
        form = ItemFinancialForm()
        if form.validate_on_submit():
            item_data = session.get('item_data', {})
            photos = handle_photos(request.files.getlist('photos'))
            
            # Fetch category, type, and condition objects based on stored IDs
            category = Category.query.get(item_data.get('category'))
            type = Type.query.get(item_data.get('type'))
            condition = Condition.query.get(item_data.get('condition'))
            
            # Create and save the item
            item = Item(
                title=item_data.get('title'),
                description=item_data.get('description'),
                category=category,  # Assigning full object
                type=type,          # Assigning full object
                condition=condition,  # Assigning full object
                provenance_origin=item_data.get('provenance_origin'),
                provenance_previous_ownership=item_data.get('provenance_previous_ownership'),
                authentication_details=item_data.get('authentication_details'),
                certificates=item_data.get('certificates'),
                dimensions=item_data.get('dimensions'),
                material=item_data.get('material'),
                rarity=item_data.get('rarity'),
                edition=item_data.get('edition'),
                starting_bid=form.starting_bid.data,
                reserve_price=form.reserve_price.data,
                photos=photos
            )
            try:
                db.session.add(item)
                db.session.commit()
                session.pop('item_data', None)
                flash('Item added successfully!')
                return redirect(url_for('auction.index'))
            except Exception as e:
                db.session.rollback()
                logging.error(f'Error adding item: {e}', exc_info=True)
                flash(f'An error occurred: {str(e)}')

    else:
        flash('Invalid step')
        return redirect(url_for('item.add_item', step=1))

    return render_template('items/add_item_wizard.html', form=form, step=step)


@item_bp.route('/items')
def display_items():
    items = Item.query.all()
    return render_template('items/display_items.html', items=items)


@item_bp.route('/place-bid/<int:item_id>', methods=['GET', 'POST'])
@login_required
def place_bid(item_id):
    item = Item.query.get_or_404(item_id)

    # Check if item is in an active independent auction
    if item.end_time and item.end_time < datetime.utcnow():
        flash('This auction has ended.', 'danger')
        return redirect(url_for('item.display_items'))

    if request.method == 'POST':
        bid_amount = request.form.get('bid_amount', type=float)
        if bid_amount and bid_amount > item.starting_bid:
            # Check if the bid is higher than the current highest bid
            highest_bid = Bid.query.filter_by(auction_id=item.auction_id).order_by(Bid.amount.desc()).first()
            if highest_bid and bid_amount <= highest_bid.amount:
                flash('Bid amount must be higher than the current highest bid.', 'danger')
            else:
                # Process the bid
                bid = Bid(amount=bid_amount, auction_id=item.auction_id, user_id=current_user.id)
                db.session.add(bid)
                db.session.commit()
                flash('Bid placed successfully!', 'success')
                return redirect(url_for('item.display_items'))
        else:
            flash('Bid amount must be higher than the starting bid.', 'danger')

    return render_template('items/place_bid.html', item=item)


@item_bp.route('/recent-items')
def recent_items():
    items = Item.query.order_by(Item.id.desc()).limit(6).all()
    return render_template('items/recent_items.html', items=items)
