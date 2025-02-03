from flask import Flask, request, send_file, jsonify, render_template_string, render_template
from flask_cors import CORS
import os
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import ssl
from cryptography.fernet import Fernet
import base64
import tempfile

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'shared_files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'zip'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store shared file information
shared_files = {}

# Create a Fernet key for encryption/decryption
def get_or_create_key():
    key_file = 'server_key.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

# Initialize Fernet cipher
cipher = Fernet(get_or_create_key())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/share', methods=['POST'])
def share_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    username = request.form.get('username', 'anonymous')
    password = request.form.get('password', '')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    file_id = datetime.now().strftime('%Y%m%d_%H%M%S_') + filename
    
    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, file_id)
    file.save(file_path)
    
    # Store file information
    shared_files[file_id] = {
        'filename': filename,
        'password': password,
        'username': username,
        'timestamp': datetime.now().isoformat()
    }
    
    # Generate share link
    share_link = f"http://{request.host}/view/{file_id}"
    return jsonify({'link': share_link})

@app.route('/view/<file_id>', methods=['GET'])
def view_file(file_id):
    if file_id not in shared_files:
        return "File not found", 404
    
    file_info = shared_files[file_id]
    file_path = os.path.join(UPLOAD_FOLDER, file_id)
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    # Render template with file information
    return render_template('view_file.html',
                         filename=file_info['filename'],
                         username=file_info['username'],
                         timestamp=file_info['timestamp'],
                         file_id=file_id)

@app.route('/download/<file_id>', methods=['POST'])
def download_file(file_id):
    if file_id not in shared_files:
        return "File not found", 404
    
    password = request.form.get('password', '')
    file_info = shared_files[file_id]
    
    if password != file_info['password']:
        return "Incorrect password", 403
    
    file_path = os.path.join(UPLOAD_FOLDER, file_id)
    return send_file(file_path,
                    download_name=file_info['filename'],
                    as_attachment=True)

if __name__ == '__main__':
    try:
        # Try different ports if the default is in use
        ports = [5000,8081, 8082, 5001]
        
        for port in ports:
            try:
                print(f"Attempting to start server on http://localhost:{port}")
                app.run(host='localhost', port=port, debug=True)
                break  # If successful, break the loop
            except OSError as e:
                print(f"Port {port} is in use, trying next port...")
                continue
            
    except Exception as e:
        print(f"Server error: {e}")
    
    # Keep SSL code commented out until you have proper certificates
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # ssl_context.load_cert_chain('certificate.pem', 'private_key.pem')
    # app.run(host='0.0.0.0', port=5000, ssl_context=ssl_context)
