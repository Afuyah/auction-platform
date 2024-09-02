from app import create_app, db, socketio  
from flask_migrate import Migrate

# Create Flask app
app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Run the application with WebSocket support
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)  # Use socketio.run instead of app.run
