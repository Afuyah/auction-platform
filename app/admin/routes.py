from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.authentication.forms import RoleForm, PermissionForm
from app import db
from app.authentication.models import Role, Permission
from functools import wraps
from flask import abort
from flask_login import current_user


admin_bp = Blueprint('admin', __name__)




def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_role(role_name):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator



@admin_bp.route('/roles', methods=['GET', 'POST'])
@login_required
def manage_roles():
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data, description=form.description.data)
        db.session.add(role)
        db.session.commit()
        flash('Role created successfully.', 'success')
        return redirect(url_for('admin.manage_roles'))
    roles = Role.query.all()
    return render_template('manage_roles.html', form=form, roles=roles)

@admin_bp.route('/roles/delete/<int:role_id>', methods=['POST'])
@login_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    flash('Role deleted successfully.', 'success')
    return redirect(url_for('admin.manage_roles'))

@admin_bp.route('/permissions', methods=['GET', 'POST'])
@login_required
def manage_permissions():
    form = PermissionForm()
    if form.validate_on_submit():
        permission = Permission(name=form.name.data, description=form.description.data)
        db.session.add(permission)
        db.session.commit()
        flash('Permission created successfully.', 'success')
        return redirect(url_for('admin.manage_permissions'))
    permissions = Permission.query.all()
    return render_template('manage_permissions.html', form=form, permissions=permissions)

@admin_bp.route('/permissions/delete/<int:permission_id>', methods=['POST'])
@login_required
def delete_permission(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    db.session.delete(permission)
    db.session.commit()
    flash('Permission deleted successfully.', 'success')
    return redirect(url_for('admin.manage_permissions'))


@admin_bp.route('/assign_role', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def assign_role():
    form = AssignRoleForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        role = Role.query.filter_by(name=form.role.data).first()
        if user and role:
            user.roles.append(role)
            db.session.commit()
            flash('Role assigned successfully.', 'success')
        else:
            flash('User or Role not found.', 'danger')
        return redirect(url_for('admin.manage_roles'))
    
    return render_template('assign_role.html', form=form)
   


@admin_bp.route('/admin-only')
@role_required('Admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')
