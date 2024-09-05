from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from redis import Redis
from celery import Celery
from flask_caching import Cache
from flask_socketio import SocketIO
from flask_migrate import Migrate



# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()
mail = Mail()
login_manager = LoginManager()
csrf = CSRFProtect()
cache = Cache()  # For caching
migrate = Migrate()


def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or 'config.Config')

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)  # Initialize caching
    migrate.init_app(app, db)

    
    # Redis and Celery configuration
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.celery = make_celery(app)

    # Register Blueprints
    from app.authentication.routes import auth_bp
    from app.auction.routes import auction_bp
    from app.user.routes import user_bp
    from app.item.routes import item_bp
    from app.admin.routes import admin_bp

    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auction_bp)
    app.register_blueprint(item_bp, url_prefix='/item')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
   
    # Session handling and cookie settings
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Options: 'Lax', 'Strict', 'None'
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'

    # Set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # User loader function
    from app.authentication.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    return celery
