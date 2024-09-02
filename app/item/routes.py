from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.auction.models import Item
from .forms import ItemDetailsForm, ItemSpecificationsForm, ItemFinancialForm
from app import db
from werkzeug.utils import secure_filename
import os

item_bp = Blueprint('item', __name__)

UPLOAD_FOLDER = 'static/images/uploads'  # Ensure this path exists and is writable
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@item_bp.route('/add-item/step1', methods=['GET', 'POST'])
@login_required
def add_item_step1():
    form = ItemDetailsForm()
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
        return redirect(url_for('item.add_item_step2'))
    return render_template('add_item_step1.html', form=form)

@item_bp.route('/add-item/step2', methods=['GET', 'POST'])
@login_required
def add_item_step2():
    form = ItemSpecificationsForm()
    if form.validate_on_submit():
        session['item_data'].update({
            'dimensions': form.dimensions.data,
            'material': form.material.data,
            'rarity': form.rarity.data,
            'edition': form.edition.data,
        })
        return redirect(url_for('item.add_item_step3'))
    return render_template('add_item_step2.html', form=form)

@item_bp.route('/add-item/step3', methods=['GET', 'POST'])
@login_required
def add_item_step3():
    form = ItemFinancialForm()
    if form.validate_on_submit():
        item_data = session.get('item_data', {})
        photos = []
        if 'photos' in request.files:
            files = request.files.getlist('photos')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    photos.append(filename)  # Store only filenames

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
            photos=photos  # Store filenames
        )
        try:
            db.session.add(item)
            db.session.commit()
            session.pop('item_data', None)
            flash('Item added successfully!')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}')
        return redirect(url_for('item.index'))
    return render_template('add_item_step3.html', form=form)
