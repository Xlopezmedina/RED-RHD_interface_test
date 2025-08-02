# Miguel A. Lopez-Medina 
# RED-RHD Pipeline. Rice University , 2025. 
# This script orchestrates the entire RED-RHD pipeline, including data transfer, audio processing, embedding extraction, and inference using a pre-trained model.
# E-mail: Miguel.Angel.Lopez-Medina@rice.edu

import os
import pandas as pd
import random
import string
import numpy as np
import json
import glob
import mlflow
from azure.ai.ml import MLClient

from azure.storage.blob import BlobClient, ContainerClient

from src.GC_cardio_to_AzureBlob import transfer_gcs_to_azure
from src.embedding import extract_embedding
from src.selector import select_region_profile
from src.model_loader import load_model_for_region
from src.blob_utils import download_blob, upload_embedding_to_blob
from azure_config import get_ml_client
from src.denoise import denoise_audio
from src.embedding import convert_embeddings_to_records


import joblib
import matplotlib
matplotlib.use('Agg')
import traceback

import requests
import json


# ---------------------------
# Azure ML Workspace config
# ---------------------------
SUBSCRIPTION_ID = "8f2b3b19-4125-48a8-8667-cccd54dfca21"
RESOURCE_GROUP = "rg_aml1"
WORKSPACE_NAME = "ws_ads_ml"

# ---------------------------
# Storage config
# ---------------------------
BLOB_URL = "https://wsadsml5029665853.blob.core.windows.net/cardiorhddata"
AZURE_SAS_TOKEN = "sp=rcwdl&st=2025-06-09T15:34:27Z&se=2026-01-01T00:34:27Z&spr=https&sv=2024-11-04&sr=c&sig=xiMml%2BGPQKj17%2BZDvLORt2HS3Is1%2BzaMokFdyGUnW8M%3D"

# ---------------------------
# Local paths
# ---------------------------
LOCAL_AUDIO_DIR = "data/audio"
LOCAL_EMBEDDING_DIR = "data/embeddings"
LOCAL_DOWNLOADED_EMBEDDINGS_DIR = "data/downloaded_embeddings"
REGION_PROFILE_PATH = "data/region_profiles.json"

# ---------------------------
# GCP source
# ---------------------------
gcp_credentials_file = r"./src/cairdio-dev-8f435-2e1bb339037a.json"
gcs_bucket_name = "nexus-rhd-data"
gcs_prefixes = ["metadata/", "metadata_fields.txt", "recordings/"]

# ---------------------------
# Azure ML model URI
# ---------------------------
MODEL_URI = (
    "azureml://locations/eastus2/workspaces/3ebc5acb-7a2a-4c74-956c-19f81f4ea4f9"
    "/models/red_rhd_model1/versions/1"
)

# ---------------------------
# Helper to download all embeddings from blob
# ---------------------------
def download_all_embeddings(local_dir):
    print("\n🟣 Downloading all embeddings from Azure Blob Storage...")
    os.makedirs(local_dir, exist_ok=True)

    container_client = ContainerClient.from_container_url(
        container_url=BLOB_URL,
        credential=AZURE_SAS_TOKEN
    )

    count = 0
    for blob in container_client.list_blobs(name_starts_with="embeddings/"):
        if blob.name.endswith(".npy"):
            local_path = os.path.join(local_dir, os.path.basename(blob.name))
            with open(local_path, "wb") as f:
                f.write(container_client.download_blob(blob).readall())
            print(f"✅ Downloaded: {blob.name} → {local_path}")
            count += 1

    print(f"✅ Total embeddings downloaded: {count}")


#------------------------------------
# This function generates a random patient ID consisting of uppercase letters and digits.
#------------------------------------
def generate_random_patient_id(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# ---------------------------
# Main pipeline
# ---------------------------
def run_pipeline():
    print("\n🚀 Starting RED-RHD Pipeline...")

    # ------------------------------------------
    # STEP 0: Collect data from GCP → Azure Blob
    # ------------------------------------------
    print("\n🟣 Transferring data from GCP to Azure Blob Storage...")
    transfer_gcs_to_azure(
        gcp_credentials_file,
        gcs_bucket_name,
        gcs_prefixes,
        BLOB_URL,
        AZURE_SAS_TOKEN
    )

    # ------------------------------------------
    # STEP 1: Download audio recordings
    # ------------------------------------------
    print("\n🟣 Downloading audio files from Azure Blob...")
    downloaded_files = download_blob(BLOB_URL, LOCAL_AUDIO_DIR, AZURE_SAS_TOKEN)

    print(f"✅ Total audio files downloaded: {len(downloaded_files)}")
    for f in downloaded_files:
        print(f"📁 {f}")

    # ------------------------------------------
    # STEP 2: Connect to Azure ML Workspace
    # ------------------------------------------
    print("\n🟣 Connecting to Azure ML...")
    ml_client = get_ml_client(SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME)

    # ------------------------------------------
    # STEP 3: Make local embeddings directory
    # ------------------------------------------
    os.makedirs(LOCAL_EMBEDDING_DIR, exist_ok=True)

    # ------------------------------------------
    # STEP 4: Process each audio file
    # ------------------------------------------
    for audio_file in downloaded_files:
        print(f"\n🎧 Processing: {audio_file}")

        # Optional: apply denoising before embedding
        denoised_file = denoise_audio(audio_file)

        # Extract embedding
        embedding = extract_embedding(denoised_file)

        # Save locally
        embedding_filename = os.path.basename(audio_file).replace(".wav", "_embedding.npy")
        local_embedding_path = os.path.join(LOCAL_EMBEDDING_DIR, embedding_filename)
        np.save(local_embedding_path, embedding)
        print(f"💾 Saved embedding locally: {local_embedding_path}")

        # Upload to Azure Blob Storage
        blob_path = f"embeddings/{embedding_filename}"
        blob_client = BlobClient.from_blob_url(
            blob_url=f"{BLOB_URL}/{blob_path}",
            credential=AZURE_SAS_TOKEN
        )

        with open(local_embedding_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"⬆️ Uploaded embedding to Azure Blob: {blob_path}")

    print("\n✅ Upload phase completed successfully.")

    # ------------------------------------------
    # STEP 5: Inference Phase via Azure Endpoint
    # ------------------------------------------
    print("\n🚀 Starting Inference Phase...")

    LOCAL_DOWNLOADED_EMBEDDINGS_DIR = "data/downloaded_embeddings"
    embedding_files = glob.glob(os.path.join(LOCAL_DOWNLOADED_EMBEDDINGS_DIR, "*.npy"))
    X = []
    valid_files = []

    if not embedding_files:
        print(f"❌ No embedding .npy files found in {LOCAL_DOWNLOADED_EMBEDDINGS_DIR}. Exiting.")
        exit(1)

    for path in embedding_files:
        try:
            emb = np.load(path, allow_pickle=True).squeeze()
        except Exception as e:
            print(f"❌ ERROR loading {path}: {e}")
            continue

        if emb.ndim == 0:
            print(f"⚠️ Skipping {path}: scalar value detected (shape={emb.shape})")
            continue

        if emb.shape[-1] != 512:
            print(f"⚠️ Skipping {path}: invalid shape {emb.shape} (expected last dim=512)")
            continue

        emb = emb.reshape(-1, 512)
        for row in emb:
            X.append(row)
            valid_files.append(path)

    X = np.array(X)

    if len(X) == 0:
        print("❌ No valid embeddings to predict. Exiting.")
        exit(1)

    print(f"✅ Loaded {len(X)} embeddings for prediction.")

    # ------------------------------------------
    # 5.2 Convert embeddings to DataFrame
    # ------------------------------------------
    print("\n🟣 Converting embeddings to inference DataFrame...")

    try:
        records = convert_embeddings_to_records(X)
        df_inference = pd.DataFrame(records)

        # Cast features to float32
        feature_cols = [col for col in df_inference.columns if col.startswith('openl3_feature_')]
        df_inference[feature_cols] = df_inference[feature_cols].astype('float32')

        print("✅ DataFrame ready for prediction:")
        print(df_inference.head())

    except Exception as e:
        print(f"❌ ERROR during DataFrame preparation: {e}")
        traceback.print_exc()
        exit(1)

    # ------------------------------------------
    # 5.3 Call Azure ML Online Endpoint
    # ------------------------------------------
    print("\n🟣 Calling Azure ML Online Endpoint for scoring...")

    AZURE_ENDPOINT_URI = "https://ep-red-rhd-model1.eastus2.inference.ml.azure.com/score"
    AZURE_ENDPOINT_KEY = "AZISPKUHZQ267shHdC8DQfUwo7IrvfE5z9HaOflRe10JW0OJSMtpJQQJ99BGAAAAAAAAAAAAINFRAZML1FTS"

    def call_azure_endpoint(df, endpoint_uri, api_key):
        import requests
        import json

        # ✅ Correct Azure ML format expected by your endpoint
        payload = {
            "input_data": df.to_dict(orient="split")
        }

        # Optional debug
        print("\n🟣 Payload preview:")
        print(json.dumps(payload)[:500] + " ...")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        print("\n🟣 Sending request to Azure endpoint...")
        response = requests.post(endpoint_uri, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"❌ ERROR: Azure endpoint returned status {response.status_code}")
            print(response.text)
            exit(1)

        return response.json()

    try:
        predictions_response = call_azure_endpoint(df_inference, AZURE_ENDPOINT_URI, AZURE_ENDPOINT_KEY)

        # Handle Azure typical response format
        if isinstance(predictions_response, dict) and "predictions" in predictions_response:
            predictions = predictions_response["predictions"]
        else:
            predictions = predictions_response

        print("\n✅ Prediction step completed successfully.")

    except Exception as e:
        print(f"❌ ERROR during endpoint call: {e}")
        traceback.print_exc()
        exit(1)

    # ------------------------------------------
    # 5.4 Print results
    # ------------------------------------------
    print("\n✅ Predictions:")
    for fname, pred in zip(valid_files, predictions):
        print(f"📈 {os.path.basename(fname)} → predicted: {pred}")

    print("\n✅ Inference Phase completed successfully.")

    # ------------------------------------------
    # 5.5 Upload predictions to Azure Blob
    # ------------------------------------------
    print("\n🟣 Storing predictions to Azure Blob Storage...")

    # Prepare a DataFrame to save
    results_df = pd.DataFrame({
        "file": [os.path.basename(f) for f in valid_files],
        "prediction": predictions
    })

    # Choose output filename
    local_predictions_file = "predictions_results.csv"
    results_df.to_csv(local_predictions_file, index=False)
    print(f"✅ Saved local predictions file: {local_predictions_file}")

    # Upload to Azure Blob
    blob_predictions_path = f"predictions/{local_predictions_file}"
    blob_client = BlobClient.from_blob_url(
        blob_url=f"{BLOB_URL}/{blob_predictions_path}",
        credential=AZURE_SAS_TOKEN
    )

    with open(local_predictions_file, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    print(f"⬆️ Uploaded predictions file to Azure Blob Storage: {blob_predictions_path}")



# ---------------------------
# Entrypoint
# ---------------------------
if __name__ == "__main__":
    run_pipeline()

