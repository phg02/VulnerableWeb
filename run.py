import os
from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Initialize database
    with app.app_context():
        from app.database import get_db, init_db
        get_db()
        init_db()
    
    # Run development server on port 8080 to avoid macOS conflicts
    debug = os.environ.get('FLASK_DEBUG', True)
    app.run(host='127.0.0.1', port=8080, debug=debug)
