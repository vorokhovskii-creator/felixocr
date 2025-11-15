import os
import base64
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from openrouter_client import OpenRouterClient
from extractor import TextExtractor
import json

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

try:
    client = OpenRouterClient()
    extractor = TextExtractor('config.json')
    
    with open('prompts/system_prompt.txt', 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    with open('prompts/user_prompt.txt', 'r', encoding='utf-8') as f:
        user_prompt = f.read()
except Exception as e:
    app.logger.error(f"Error initializing application: {str(e)}")


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def image_to_base64(file_path):
    """Convert image file to base64 string."""
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
def process_image():
    """Process uploaded image and extract text."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        image_base64 = image_to_base64(file_path)
        
        response_text = client.send_image_for_ocr(image_base64, system_prompt, user_prompt)
        
        results = extractor.extract_from_response(response_text)
        
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'data': results
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error processing image: {str(e)}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
