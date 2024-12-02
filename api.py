from flask import Flask, jsonify, request, render_template
from rename_files import InteractiveFileRenamer
from pathlib import Path
import webview

renamer = None

def create_app():
    global renamer
    app = Flask(__name__, template_folder="templates", static_folder="static")
    renamer = InteractiveFileRenamer()

    @app.route('/')
    def index():
        return render_template("index.html")  # Render the main GUI HTML file

    @app.route('/set_directory', methods=['POST'])
    def set_directory():
        data = request.json
        directory = Path(data['directory'])
        if directory.is_dir():
            renamer.base_dir = directory
            return jsonify({"message": "Directory set successfully."})
        return jsonify({"error": "Invalid directory."}), 400

    @app.route('/discover_patterns', methods=['GET'])
    def discover_patterns():
        if renamer.base_dir:  # Check if base_dir is set
            patterns = renamer._discover_file_patterns()
            return jsonify(patterns)
        return jsonify({'error': 'Directory not set.'}), 400  # Return an error if not

    @app.route('/rename_files', methods=['POST'])
    async def rename_files_route(): # Make rename_files async
        global renamer
        if not renamer.base_dir:
            return jsonify({'error': 'Directory not set.'}), 400

        data = request.json
        renamer.filename_prefix = data.get('prefix', 'new')
        renamer.filename_extension = data.get('extension', '.txt')
        try:
            renamed, failed, failed_files = await renamer.rename_files()
            return jsonify({'renamed_count': renamed, 'failed_count': failed, 'failed_files': failed_files})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app
