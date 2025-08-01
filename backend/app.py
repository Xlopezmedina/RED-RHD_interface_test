from flask import Flask, jsonify, Response
from flask_cors import CORS
from azure.storage.blob import ContainerClient
from dotenv import load_dotenv
import os

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
                "url": f"/api/audio/{blob.name}",
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
        stream = blob_client.download_blob()
        audio_data = stream.readall()
        
        # Determine content type based on file extension
        content_type = "audio/wav"
        if filename.lower().endswith('.mp3'):
            content_type = "audio/mpeg"
        elif filename.lower().endswith('.m4a'):
            content_type = "audio/mp4"
        
        return Response(audio_data, mimetype=content_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/comments', methods=['POST'])
def save_comment():
    # This would typically save to a database
    # For now, just return success
    return jsonify({"status": "success", "message": "Comment saved successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)