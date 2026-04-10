from flask import Flask
from flask_cors import CORS
from .extensions import db, jwt
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)
with app.app_context():
    try:
        from .models import User, Godown, Booking
        db.create_all()
    except Exception as e:
        print(f"Database initialization skipped: {e}")
jwt.init_app(app)
# Register blueprints
from .routes.auth_routes import auth_bp
from .routes.farmer_routes import farmer_bp
from .routes.buyer_routes import buyer_bp
from .routes.godown_routes import godown_bp
from .routes.booking_routes import booking_bp
from .routes.ai_routes import ai_bp
from .jobs.scheduler import init_scheduler

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(farmer_bp, url_prefix='/api/farmer')
app.register_blueprint(buyer_bp, url_prefix='/api')
app.register_blueprint(godown_bp, url_prefix='/api')
app.register_blueprint(booking_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api/ai')

# Initialize the scheduler (Safe start)
try:
    init_scheduler(app)
except Exception as e:
    print(f"AI Scheduler could not start: {e}")

if __name__ == '__main__':
    app.run(debug=True)
