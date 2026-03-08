import sys
import os

# Add the root directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up environment variables
os.environ.setdefault('FLASK_ENV', 'production')

# Import app and initialize it
from app import app, db
from werkzeug.middleware.proxy_fix import ProxyFix
from models import ArticleCategory

# Apply ProxyFix to handle Netlify's reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Ensure the application is properly initialized with app context
with app.app_context():
    # Create all tables if they don't exist (db already initialized in app.py)
    db.create_all()
    
    # Initialize experience sharing module with default categories
    if ArticleCategory.query.count() == 0:
        # Add default categories
        default_categories = [
            {'name': '维修技巧', 'description': '设备维修技巧分享'}, 
            {'name': '故障案例', 'description': '设备故障案例分析'}, 
            {'name': '技术分享', 'description': '技术知识分享'}
        ]
        
        for category_data in default_categories:
            category = ArticleCategory(**category_data)
            db.session.add(category)
        
        db.session.commit()
    
    # Ensure upload directory exists
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

def handler(event, context):
    """Netlify Functions handler for Flask application"""
    # Import the necessary modules for handling the request
    from serverless_wsgi import handle_request
    
    # Convert Netlify's event to a WSGI request and handle it with Flask
    return handle_request(app, event, context)