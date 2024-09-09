from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.authentication.forms import RoleForm, PermissionForm ,FeatureForm
from app import db
from app.authentication.models import Role, Permission, User
from app.auction.models import Auction, Item
from functools import wraps
import logging

admin_bp = Blueprint('admin', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def role_required(role_name):
    """Decorator to check if the current user has the required role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_role(role_name):
                logger.warning(f"Unauthorized access attempt by {current_user.email} to {request.url}")
                abort(403)  # Forbidden access
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@admin_bp.route('/roles', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_roles():
    """Route to manage roles - create, list, and delete roles."""
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data, description=form.description.data)
        db.session.add(role)
        db.session.commit()
        logger.info(f"Role created: {role.name}")
        flash('Role created successfully.', 'success')
        return redirect(url_for('admin.manage_roles'))
    roles = Role.query.all()
    return render_template('manage_roles.html', form=form, roles=roles)

@admin_bp.route('/roles/delete/<int:role_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_role(role_id):
    """Route to delete a specific role."""
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    logger.info(f"Role deleted: {role.name}")
    flash('Role deleted successfully.', 'success')
    return redirect(url_for('admin.manage_roles'))

@admin_bp.route('/permissions', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_permissions():
    """Route to manage permissions - create, list, and delete permissions."""
    form = PermissionForm()
    if form.validate_on_submit():
        permission = Permission(name=form.name.data, description=form.description.data)
        db.session.add(permission)
        db.session.commit()
        logger.info(f"Permission created: {permission.name}")
        flash('Permission created successfully.', 'success')
        return redirect(url_for('admin.manage_permissions'))
    permissions = Permission.query.all()
    return render_template('manage_permissions.html', form=form, permissions=permissions)

@admin_bp.route('/permissions/delete/<int:permission_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_permission(permission_id):
    """Route to delete a specific permission."""
    permission = Permission.query.get_or_404(permission_id)
    db.session.delete(permission)
    db.session.commit()
    logger.info(f"Permission deleted: {permission.name}")
    flash('Permission deleted successfully.', 'success')
    return redirect(url_for('admin.manage_permissions'))

@admin_bp.route('/assign_role', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def assign_role():
    """Route to assign a role to a user."""
    form = AssignRoleForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        role = Role.query.filter_by(name=form.role.data).first()
        if user and role:
            if role not in user.roles:
                user.roles.append(role)
                db.session.commit()
                logger.info(f"Role '{role.name}' assigned to user '{user.email}'")
                flash('Role assigned successfully.', 'success')
            else:
                flash('User already has this role.', 'warning')
        else:
            flash('User or Role not found.', 'danger')
        return redirect(url_for('admin.manage_roles'))
    
    return render_template('assign_role.html', form=form)

@admin_bp.route('/admin-dashboard')
@login_required
@role_required('Admin')
def admin_dashboard():
    try:
        roles = Role.query.all()
        permissions = Permission.query.all()
        users = User.query.all()
        pending_items = Item.query.filter_by(status='Pending Verification').all()
        verified_items = Item.query.filter_by(status='Verified').all()
        rejected_items = Item.query.filter_by(status='Rejected').all()
        auctions = Auction.query.all()

        # Create an instance of FeatureForm to be used in the template
        feature_form = FeatureForm()

        logger.info(f"Admin dashboard accessed by '{current_user.email}'")

        return render_template('admin/admin_dashboard.html',
                               roles=roles,
                               permissions=permissions,
                               users=users,
                               pending_items=pending_items,
                               verified_items=verified_items,
                               rejected_items=rejected_items,
                               auctions=auctions,
                               feature_form=feature_form)
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {e}")
        flash('An error occurred while loading the dashboard. Please try again later.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))




@admin_bp.route('/items/verify/<int:item_id>', methods=['POST'])
@login_required
@role_required('Admin')
def verify_item(item_id):
    """Route to verify an item added by a user."""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        end_time = request.form.get('end_time')
        if end_time:
            try:
                item.end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                flash('Invalid date format. Use YYYY-MM-DD HH:MM:SS.', 'danger')
                return redirect(url_for('admin.admin_dashboard'))

    if item.status == 'Pending Verification':
        item.status = 'Verified'
        db.session.commit()
        logger.info(f"Item '{item.title}' verified by admin '{current_user.email}'")
        flash('Item verified successfully.', 'success')
    else:
        flash('Item is already verified or does not require verification.', 'warning')
    
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/items/reject/<int:item_id>', methods=['POST'])
@login_required
@role_required('Admin')
def reject_item(item_id):
    """Route to reject an item added by a user."""
    item = Item.query.get_or_404(item_id)
    if item.status == 'Pending Verification':
        item.status = 'Rejected'
        db.session.commit()
        logger.info(f"Item '{item.title}' rejected by admin '{current_user.email}'")
        flash('Item rejected successfully.', 'success')
    else:
        flash('Item is already verified or does not require rejection.', 'warning')
    return redirect(url_for('admin.admin_dashboard'))




@admin_bp.route('/<int:auction_id>/activate', methods=['POST'])
@login_required
@role_required('Admin')
def activate_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    try:
        auction.activate()
        db.session.commit()
        logger.info(f"Auction '{auction.title}' activated by admin '{current_user.email}'")
        flash('Auction activated and open for bidding!', 'success')
    except ValueError as e:
        logger.warning(f"Failed to activate auction '{auction.title}': {e}")
        flash(str(e), 'danger')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error activating auction '{auction.title}': {e}")
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/<int:auction_id>/deactivate', methods=['POST'])
@login_required
@role_required('Admin')
def deactivate_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    if auction.status == 'Inactive':
        flash('Auction is already inactive.', 'warning')
        return redirect(url_for('admin.admin_dashboard'))
    
    auction.deactivate()
    try:
        db.session.commit()
        logger.info(f"Auction '{auction.title}' deactivated by admin '{current_user.email}'")
        flash('Auction deactivated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deactivating auction '{auction.title}': {e}")
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('admin.admin_dashboard'))





@admin_bp.route('/feature/<int:auction_id>', methods=['POST'])
@login_required
@role_required('Admin')
def feature_auction(auction_id):
    form = FeatureForm()
    if form.validate_on_submit():
        auction = Auction.query.get_or_404(auction_id)
        if not auction.is_featured:
            auction.is_featured = True
            db.session.commit()
            flash('Auction has been featured successfully!', 'success')
        else:
            flash('Auction is already featured.', 'warning')
    return redirect(url_for('admin.admin_dashboard') )

@admin_bp.route('/unfeature/<int:auction_id>', methods=['POST'])
@login_required
@role_required('Admin')
def unfeature_auction(auction_id):
    form = FeatureForm()
    if form.validate_on_submit():
        auction = Auction.query.get_or_404(auction_id)
        if auction.is_featured:
            auction.is_featured = False
            db.session.commit()
            flash('Auction removed from featured section!', 'success')
        else:
            flash('Auction is not featured.', 'warning')
    return redirect(url_for('admin.admin_dashboard'))