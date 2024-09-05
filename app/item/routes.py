import os
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.auction.models import Item,Category, Type
from .forms import ItemDetailsForm, ItemSpecificationsForm, ItemFinancialForm, CategoryForm, TypeForm
from app import db
from .helpers import get_categories, get_types  # Ensure this import matches your actual helper module

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
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('add_category'))
    return render_template('add_category.html', form=form)

@item_bp.route('/add-type', methods=['GET', 'POST'])
def add_type():
    form = TypeForm()
    if form.validate_on_submit():
        type_ = Type(name=form.name.data)
        db.session.add(type_)
        db.session.commit()
        flash('Type added successfully!', 'success')
        return redirect(url_for('add_type'))
    return render_template('add_type.html', form=form)


@item_bp.route('/add-item', methods=['GET', 'POST'])
@login_required
def add_item():
    step = int(request.args.get('step', '1'))

    if step == 1:
        form = ItemDetailsForm()
        form.category.choices = get_categories()  # Populate categories
        form.type.choices = get_types()  # Populate types

        if form.validate_on_submit():
            session['item_data'] = {
                'title': form.title.data,
                'description': form.description.data,
                'category': form.category.data,
                'type': form.type.data,
                'condition': form.condition.data,
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
            
            # Create and save the item
            item = Item(
                title=item_data.get('title'),
                description=item_data.get('description'),
                category=item_data.get('category'),
                type=item_data.get('type'),
                condition=item_data.get('condition'),
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
                return redirect(url_for('item.index'))
            except Exception as e:
                db.session.rollback()
                logging.error(f'Error adding item: {e}', exc_info=True)
                flash(f'An error occurred: {str(e)}')

    else:
        flash('Invalid step')
        return redirect(url_for('item.add_item', step=1))

    return render_template('items/add_item_wizard.html', form=form, step=step)
