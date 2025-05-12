# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# import os
# from extractaudio import extract_audio
# from make_highlight_chunks import generate_highlight_clips
# from final_concat_clips import concatenate_clips

# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = 'uploads'
# HIGHLIGHT_FOLDER = 'highlight_clips'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(HIGHLIGHT_FOLDER, exist_ok=True)

# @app.route('/upload', methods=['POST'])
# def upload_video():
#     if 'video' not in request.files:
#         return jsonify({'error': 'No video file provided'}), 400
#     file = request.files['video']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#     video_path = os.path.join(UPLOAD_FOLDER, 'input_video.mp4')
#     file.save(video_path)
    
#     # Extract audio
#     audio_path = os.path.join(UPLOAD_FOLDER, 'audio.wav')
#     try:
#         extract_audio(video_path, audio_path)
#         return jsonify({'message': 'Video uploaded and audio extracted'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/generate-highlights', methods=['POST'])
# def generate_highlights():
#     video_path = os.path.join(UPLOAD_FOLDER, 'input_video.mp4')
#     audio_path = os.path.join(UPLOAD_FOLDER, 'audio.wav')
#     try:
#         highlight_paths = generate_highlight_clips(video_path, audio_path, HIGHLIGHT_FOLDER)
#         highlight_urls = [f'/highlights/{os.path.basename(path)}' for path in highlight_paths]
#         return jsonify({'highlights': highlight_urls}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/concatenate', methods=['POST'])
# def concatenate():
#     try:
#         final_video_path = concatenate_clips(HIGHLIGHT_FOLDER)
#         final_video_url = f'/highlights/{os.path.basename(final_video_path)}'
#         return jsonify({'finalVideo': final_video_url}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/highlights/<filename>')
# def serve_highlight(filename):
#     return send_from_directory(HIGHLIGHT_FOLDER, filename)

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import shutil
from extractaudio import extract_audio
from make_highlight_chunks import generate_highlight_clips
from final_concat_clips import concatenate_clips

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
HIGHLIGHT_FOLDER = 'highlight_clips'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HIGHLIGHT_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Clear previous highlights
    if os.path.exists(HIGHLIGHT_FOLDER):
        shutil.rmtree(HIGHLIGHT_FOLDER)
    os.makedirs(HIGHLIGHT_FOLDER, exist_ok=True)
    
    video_path = os.path.join(UPLOAD_FOLDER, 'input_video.mp4')
    file.save(video_path)
    
    # Extract audio
    audio_path = os.path.join(UPLOAD_FOLDER, 'audio.wav')
    try:
        extract_audio(video_path, audio_path)
        return jsonify({'message': 'Video uploaded and audio extracted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-highlights', methods=['POST'])
def generate_highlights():
    video_path = os.path.join(UPLOAD_FOLDER, 'input_video.mp4')
    audio_path = os.path.join(UPLOAD_FOLDER, 'audio.wav')
    try:
        highlight_paths = generate_highlight_clips(video_path, audio_path, HIGHLIGHT_FOLDER)
        highlight_urls = [f'/highlights/{os.path.basename(path)}' for path in highlight_paths]
        return jsonify({'highlights': highlight_urls}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/concatenate', methods=['POST'])
def concatenate():
    try:
        final_video_path = concatenate_clips(HIGHLIGHT_FOLDER)
        final_video_url = f'/highlights/{os.path.basename(final_video_path)}'
        return jsonify({'finalVideo': final_video_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/highlights/<filename>')
def serve_highlight(filename):
    return send_from_directory(HIGHLIGHT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)