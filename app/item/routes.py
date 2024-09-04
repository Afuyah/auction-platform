import os
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.auction.models import Item
from .forms import ItemDetailsForm, ItemSpecificationsForm, ItemFinancialForm
from app import db

# Define Blueprint for item routes
item_bp = Blueprint('item', __name__)

# Define the path for file uploads
UPLOAD_FOLDER = 'static/images/auc'  # Ensure this path exists and is writable
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for step 1 of adding an item
@item_bp.route('/add-item/step1', methods=['GET', 'POST'])
@login_required
def add_item_step1():
    form = ItemDetailsForm()  # Create form instance
    if form.validate_on_submit():  # Check if form is submitted and valid
        # Save form data to session
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
        return redirect(url_for('item.add_item_step2'))  # Redirect to next step
    return render_template('add_item_step1.html', form=form)  # Render template with form

# Route for step 2 of adding an item
@item_bp.route('/add-item/step2', methods=['GET', 'POST'])
@login_required
def add_item_step2():
    form = ItemSpecificationsForm()  # Create form instance
    if form.validate_on_submit():  # Check if form is submitted and valid
        # Update session data with specifications
        session['item_data'].update({
            'dimensions': form.dimensions.data,
            'material': form.material.data,
            'rarity': form.rarity.data,
            'edition': form.edition.data,
        })
        return redirect(url_for('item.add_item_step3'))  # Redirect to next step
    return render_template('add_item_step2.html', form=form)  # Render template with form

# Route for step 3 of adding an item
@item_bp.route('/add-item/step3', methods=['GET', 'POST'])
@login_required
def add_item_step3():
    form = ItemFinancialForm()  # Create form instance
    if form.validate_on_submit():  # Check if form is submitted and valid
        item_data = session.get('item_data', {})  # Retrieve item data from session
        photos = []
        
        # Process uploaded files
        if 'photos' in request.files:
            files = request.files.getlist('photos')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    try:
                        file.save(file_path)  # Save file to the specified path
                        photos.append(filename)  # Store only filenames
                    except Exception as e:
                        logging.error(f'Error saving file {filename}: {e}', exc_info=True)
                        flash(f'Failed to upload file {filename}. Please try again.')
                        return render_template('add_item_step3.html', form=form)  # Return to form on error

        # Create Item instance with form and session data
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
            photos=photos  # Store filenames of uploaded photos
        )
        
        try:
            db.session.add(item)  # Add item to the database
            db.session.commit()  # Commit transaction
            session.pop('item_data', None)  # Clear session data
            flash('Item added successfully!')
        except Exception as e:
            db.session.rollback()  # Rollback transaction on error
            logging.error(f'Error adding item: {e}', exc_info=True)
            flash(f'An error occurred: {str(e)}')
        
        return redirect(url_for('item.index'))  # Redirect to item listing page
    return render_template('add_item_step3.html', form=form)  # Render template with form
