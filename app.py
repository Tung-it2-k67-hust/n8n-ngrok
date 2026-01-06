from flask import Flask, render_template, request, Response, jsonify
import os
import json
import time
from openrouter_pdf_analyzer import analyze_pdf_stream

app = Flask(__name__)

# Ensure upload directory exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    # Save file
    safe_filename = file.filename.replace(" ", "_")
    filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
    file.save(filepath)

    def generate():
        # Yield start event
        yield f"data: {json.dumps({'type': 'log', 'message': f'Processing {file.filename}...'})}\n\n"
        
        # Stream results
        try:
            for event in analyze_pdf_stream(filepath):
                yield f"data: {json.dumps(event)}\n\n"
            
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("Starting server at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
