import os
import time
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
# Use absolute path to ensure correct directory resolution
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Gemini Setup
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=api_key)

# Initialize models
vision_model = genai.GenerativeModel('gemini-2.5-flash-lite')

# Helper to calculate cosine similarity
def cosine_similarity(vec_a, vec_b):
    if not vec_a or not vec_b:
        return 0
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot_product / (norm_a * norm_b)

# Embed with retry logic (Exponential Backoff)
def embed_with_retry(text, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="semantic_similarity"
            )
            return result['embedding']
        except Exception as e:
            # Check for rate limit errors (429)
            error_str = str(e)
            if "429" in error_str and attempt < max_retries - 1:
                delay_time = (2 ** attempt) # 1s, 2s, 4s, 8s...
                print(f"Rate limit hit. Retrying in {delay_time}s...")
                time.sleep(delay_time)
                attempt += 1
            else:
                print(f"Error generating embedding: {e}")
                raise e

# Processing function for a single file
def process_file(file_info):
    file_path, filename, mime_type = file_info
    print(f"Processing file: {file_path}")
    
    try:
        # Read file data
        with open(file_path, "rb") as f:
            image_data = f.read()
            
        image_part = {
            "mime_type": mime_type,
            "data": image_data
        }

        # Generate description
        response = vision_model.generate_content(
            ["Generate a detailed description of this image for similarity comparison.", image_part]
        )
        description = response.text
        
        # Generate embedding
        embedding = embed_with_retry(description)
        
        print(f"Generated embedding for {file_path}")
        return {"filename": filename, "embedding": embedding}
    except Exception as e:
        print(f"Failed to process {filename}: {e}")
        return None

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    print(f"Serving file: {filename} from {app.config['UPLOAD_FOLDER']}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/upload', methods=['POST'])
def upload_files():
    print('--- Received image upload request ---')
    if 'images' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('images')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400

    print(f"{len(files)} file(s) received.")
    
    # Save files first
    saved_files = []
    for file in files:
        if file:
            # Sanitize and timestamp filename
            timestamp = str(int(time.time() * 1000))
            original_name = secure_filename(file.filename)
            filename = f"{timestamp}-{original_name}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            file.save(file_path)
            # Store tuple: (path, filename, mimetype)
            # Mimetype might need guess if file.mimetype is octet-stream, but usually browser sends it.
            saved_files.append((file_path, filename, file.mimetype))

    image_embeddings = {}
    print('--- Generating embeddings in parallel ---')
    
    # Parallel processing with ThreadPoolExecutor
    # Max workers set to 2 to respect rate limits while still being parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(process_file, f) for f in saved_files]
        for future in futures:
            result = future.result()
            if result:
                image_embeddings[result['filename']] = result['embedding']

    # Grouping
    print('--- Grouping images ---')
    groups = {}
    image_filenames = list(image_embeddings.keys())
    similarity_threshold = 0.7
    group_index = 0
    processed_filenames = set()
    
    for filename in image_filenames:
        if filename in processed_filenames:
            continue
            
        current_group = [filename]
        processed_filenames.add(filename)
        current_embedding = image_embeddings[filename]
        
        for other_filename in image_filenames:
            if other_filename not in processed_filenames:
                other_embedding = image_embeddings[other_filename]
                similarity = cosine_similarity(current_embedding, other_embedding)
                
                if similarity >= similarity_threshold:
                    current_group.append(other_filename)
                    processed_filenames.add(other_filename)
        
        groups[f"group-{group_index}"] = current_group
        group_index += 1

    print('--- Image grouping complete ---')
    print('Generated groups:', groups)
    
    return jsonify(groups)

if __name__ == '__main__':
    # Run on port 3000 to match the frontend configuration
    app.run(port=3000, debug=True)