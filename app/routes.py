from flask import Blueprint, request, jsonify
from .detector import detect_anomalies

routes = Blueprint('routes', __name__)

@routes.route('/analyze', methods=['POST'])
def analyze_logs():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    content = file.read().decode('utf-8')
    result = detect_anomalies(content)
    return jsonify(result)