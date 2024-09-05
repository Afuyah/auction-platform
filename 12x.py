import logging
from app import create_app, db
from app.authentication.models import User, Role, UserRoles

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the application
app = create_app()

def create_admin():
    with app.app_context():
        try:
            # Check if an admin user already exists
            admin_user = User.query.filter_by(username='jhsync').first()
            if admin_user:
                logger.info('Admin user already exists.')
                return

            # Create the admin user
            admin_user = User(username='jhsync', email='afuya.b@gmail.com')
            admin_user.set_password('12x')  # Set a strong password
            admin_user.active = True  # Set account as active
            db.session.add(admin_user)
            db.session.flush()  # Ensure the user ID is available for the next operations

            # Create the admin role
            admin_role = Role.query.filter_by(name='Admin').first()
            if not admin_role:
                admin_role = Role(name='Admin', description='Administrator role with all permissions')
                db.session.add(admin_role)
                db.session.commit()  # Commit to ensure the role ID is available

            # Assign the admin role to the admin user
            user_role = UserRoles(user_id=admin_user.id, role_id=admin_role.id)
            db.session.add(user_role)
            
            # Commit changes to the database
            db.session.commit()
            logger.info('Admin user created successfully.')

        except Exception as e:
            logger.error(f'An error occurred: {e}')
            db.session.rollback()  # Rollback the session in case of an error

if __name__ == '__main__':
    create_admin()
