"""
Dashboard web server - serves React frontend and provides API proxy.
Run separately from main.py on port 5001.
"""
from flask import Flask, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='dashboard-frontend/dist')
CORS(app)

@app.route('/')
def serve_dashboard():
    """Serve React app."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static assets."""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Check if React build exists
    if not os.path.exists('dashboard-frontend/dist'):
        print("ERROR: React build not found!")
        print("Run: cd dashboard-frontend && npm run build")
        exit(1)

    print("Dashboard server starting on http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
