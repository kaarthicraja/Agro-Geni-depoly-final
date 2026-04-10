import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from .extensions import db, jwt
from .config import Config

basedir = os.path.abspath(os.path.dirname(__file__))
dist_dir = os.path.join(basedir, '..', 'dist')

app = Flask(__name__, static_folder=dist_dir, static_url_path='/')
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

# Health check route
@app.route('/api/health')
def health():
    return {"status": "Agro Geni backend is running", "version": "1.0"}


# Register blueprints
try:
    from .routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
except Exception as e:
    print(f"Auth routes could not be loaded: {e}")

try:
    from .routes.farmer_routes import farmer_bp
    app.register_blueprint(farmer_bp, url_prefix='/api/farmer')
except Exception as e:
    print(f"Farmer routes could not be loaded: {e}")

try:
    from .routes.buyer_routes import buyer_bp
    app.register_blueprint(buyer_bp, url_prefix='/api')
except Exception as e:
    print(f"Buyer routes could not be loaded: {e}")

try:
    from .routes.godown_routes import godown_bp
    app.register_blueprint(godown_bp, url_prefix='/api')
except Exception as e:
    print(f"Godown routes could not be loaded: {e}")

try:
    from .routes.booking_routes import booking_bp
    app.register_blueprint(booking_bp, url_prefix='/api')
except Exception as e:
    print(f"Booking routes could not be loaded: {e}")

try:
    from .routes.ai_routes import ai_bp
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
except Exception as e:
    print(f"AI routes could not be loaded: {e}")

# Initialize the scheduler (Safe start)
try:
    from .jobs.scheduler import init_scheduler
    init_scheduler(app)
except Exception as e:
    print(f"AI Scheduler could not start: {e}")

# Serve React App and handle client-side routing
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

from flask import request
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return {"error": "Not found"}, 404
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
