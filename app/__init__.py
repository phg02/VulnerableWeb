from flask import Flask
from config import config
import os

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))
    
    # Register database functions
    from app.database import close_db, init_db
    app.teardown_appcontext(close_db)
    
    # Register commands
    @app.cli.command()
    def init_db_command():
        """Initialize the database"""
        from app.database import init_db, get_db
        get_db()
        init_db()
        print("Initialized the database")
    
    # Register blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    return app
