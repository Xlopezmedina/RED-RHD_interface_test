from flask import Flask, jsonify, Response
from azure.storage.blob import ContainerClient
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

# Environment variables
container_url = os.getenv("AZURE_CONTAINER_URL")
sas_token = os.getenv("AZURE_SAS_TOKEN")
full_url = f"{container_url}?{sas_token}"
container_client = ContainerClient.from_container_url(full_url)

@app.route('/api/blobs')
def list_blobs():
    blob_list = []
    for blob in container_client.list_blobs():
        # Instead of Azure URL, return a proxy URL
        blob_list.append({
            "name": blob.name,
            "url": f"/api/audio/{blob.name}"
        })
    return jsonify(blob_list)

@app.route('/api/audio/<path:filename>')
def get_audio(filename):
    try:
        blob_client = container_client.get_blob_client(filename)
        stream = blob_client.download_blob()
        audio_data = stream.readall()
        return Response(audio_data, mimetype="audio/wav")
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True)
