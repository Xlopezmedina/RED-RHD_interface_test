from flask import Flask, jsonify, Response
from flask_cors import CORS
from azure.storage.blob import ContainerClient
from dotenv import load_dotenv
import os
import requests

load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Environment variables
container_url = os.getenv("AZURE_CONTAINER_URL")
sas_token = os.getenv("AZURE_SAS_TOKEN")
full_url = f"{container_url}?{sas_token}"
container_client = ContainerClient.from_container_url(full_url)

@app.route('/api/blobs')
def list_blobs():
    try:
        blob_list = []
        for blob in container_client.list_blobs():
            blob_list.append({
                "name": blob.name,
                "url": f"http://localhost:5000/api/audio/{blob.name}",
                "size": blob.size,
                "last_modified": blob.last_modified.isoformat() if blob.last_modified else None
            })
        return jsonify(blob_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/audio/<path:filename>')
def get_audio(filename):
    try:
        blob_client = container_client.get_blob_client(filename)
        
        # Get the blob URL with SAS token for direct access
        blob_url = f"{container_url}/{filename}?{sas_token}"
        
        # Stream the file directly from Azure
        response = requests.get(blob_url, stream=True)
        if response.status_code != 200:
            return jsonify({"error": "File not found"}), 404
        
        # Determine content type based on file extension
        content_type = "audio/wav"
        if filename.lower().endswith('.mp3'):
            content_type = "audio/mpeg"
        elif filename.lower().endswith('.m4a'):
            content_type = "audio/mp4"
        elif filename.lower().endswith('.ogg'):
            content_type = "audio/ogg"
        
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            generate(),
            mimetype=content_type,
            headers={
                'Content-Length': response.headers.get('Content-Length'),
                'Accept-Ranges': 'bytes',
                'Cache-Control': 'no-cache'
            }
        )
    except Exception as e:
        print(f"Error serving audio file {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 404

@app.route('/api/download/<path:filename>')
def download_file(filename):
    try:
        blob_client = container_client.get_blob_client(filename)
        
        # Get the blob URL with SAS token for direct download
        blob_url = f"{container_url}/{filename}?{sas_token}"
        
        # Stream the file directly from Azure
        response = requests.get(blob_url, stream=True)
        if response.status_code != 200:
            return jsonify({"error": "File not found"}), 404
        
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            generate(),
            headers={
                'Content-Disposition': f'attachment; filename="{filename.split("/")[-1]}"',
                'Content-Length': response.headers.get('Content-Length'),
            }
        )
    except Exception as e:
        print(f"Error downloading file {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 404

@app.route('/api/comments', methods=['POST'])
def save_comment():
    # This would typically save to a database
    # For now, just return success
    return jsonify({"status": "success", "message": "Comment saved successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)