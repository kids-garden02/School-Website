from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
import logging
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for debugging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Registration model
class Registration(db.Model):
    __tablename__ = 'registration'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    message = db.Column(db.Text, nullable=True)

# Initialize the database
def init_db():
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database initialized successfully. Table 'registration' created.")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

@app.route('/')
def serve_html():
    logger.debug("Root route accessed: Attempting to serve index.html")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(root_dir, 'index.html')
    if os.path.exists(index_path):
        logger.info(f"Serving index.html from {index_path}")
        return send_file(index_path)
    else:
        logger.error(f"index.html not found at {index_path}")
        return """
        <h1>Error: index.html Not Found</h1>
        <p>Please ensure 'index.html' is placed in the same directory as app.py.</p>
        <p>Current directory: {}</p>
        """.format(root_dir), 404

@app.route('/<path:filename>')
def serve_html_file(filename):
    logger.debug(f"HTML file route accessed: Attempting to serve {filename}")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(root_dir, filename)
    if os.path.exists(file_path) and filename.endswith('.html'):
        logger.info(f"Serving HTML file from {file_path}")
        return send_file(file_path)
    else:
        logger.error(f"HTML file not found at {file_path}")
        return """
        <h1>Not Found</h1>
        <p>The requested URL '/{}' was not found on the server.</p>
        <p>Please check the URL or go to <a href="/">Home</a>.</p>
        """.format(filename), 404

@app.route('/images/<path:filename>')
def serve_image(filename):
    logger.debug(f"Image route accessed: Attempting to serve images/{filename}")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(root_dir, 'images')
    image_path = os.path.join(images_dir, filename)
    if os.path.exists(image_path):
        logger.info(f"Serving image from {image_path}")
        return send_from_directory(images_dir, filename)
    else:
        logger.error(f"Image not found at {image_path}")
        return jsonify({'error': f'Image {filename} not found'}), 404

@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    logger.debug("Submit-enquiry route accessed: Received form submission")
    try:
        data = request.form
        logger.debug(f"Form data: {dict(data)}")

        name = data.get('name')
        phone_no = data.get('phone_no')
        email = data.get('email')
        message = data.get('message')

        # Validate input
        if not all([name, phone_no, email]):
            logger.warning("Missing required fields")
            return jsonify({'error': 'Name, phone number, and email are required'}), 400

        # Create new registration entry
        new_registration = Registration(
            name=name,
            phone_no=phone_no,
            email=email,
            message=message
        )

        # Add to database
        db.session.add(new_registration)
        try:
            db.session.commit()
            logger.info(f"Successfully registered: {name}, {email}")
            return jsonify({'message': 'Enquiry submitted successfully!'}), 200
        except IntegrityError as e:
            db.session.rollback()
            logger.warning(f"IntegrityError: {str(e)}")
            return jsonify({'error': 'Phone number or email already exists'}), 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    # Ensure database is initialized
    init_db()
    # Check if index.html exists in the root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(root_dir, 'index.html')
    if os.path.exists(index_path):
        logger.info(f"index.html found at {index_path}")
    else:
        logger.error(f"index.html not found at {index_path}")
    # Check if other HTML files exist
    html_files = ['a1.html', 'a2.html', 'a3.html', 'a4.html', 'a5.html', 'dvm.html']
    for html_file in html_files:
        file_path = os.path.join(root_dir, html_file)
        if os.path.exists(file_path):
            logger.info(f"{html_file} found at {file_path}")
        else:
            logger.warning(f"{html_file} not found at {file_path}")
    # Check if images folder exists
    images_dir = os.path.join(root_dir, 'images')
    if os.path.exists(images_dir):
        logger.info(f"images/ folder found at {images_dir}")
    else:
        logger.error(f"images/ folder not found at {images_dir}")
    # Check if database file exists
    if os.path.exists('data.db'):
        logger.info("Database file 'data.db' found")
    else:
        logger.warning("Database file 'data.db' not found")
    app.run(debug=True, port=5000, host='0.0.0.0')