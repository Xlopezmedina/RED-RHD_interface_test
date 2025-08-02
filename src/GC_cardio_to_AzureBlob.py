# Transfer files from Google Cloud Storage to Azure Blob Storage using SAS token
# Author: Miguel A. Lopez
# Date: 2025-06-02
# Version: 1.0.0

from google.cloud import storage as gcs_storage
from azure.storage.blob import BlobClient
import os

def transfer_gcs_to_azure(gcp_credentials_file: str, gcs_bucket_name: str, gcs_prefixes: list,
                           azure_container_url: str, azure_sas_token: str):
    """
    Transfers files from a Google Cloud Storage bucket to an Azure Blob Storage container using a SAS token.

    Parameters:
        gcp_credentials_file (str): Path to GCP service account JSON key.
        gcs_bucket_name (str): Name of the GCS bucket.
        gcs_prefixes (list): List of GCS object prefixes or paths to transfer.
        azure_container_url (str): Azure Blob Storage container URL (excluding SAS).
        azure_sas_token (str): SAS token string (do not include '?' at the beginning).
    """
    try:
        # Set GCP credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_credentials_file
        gcs_client = gcs_storage.Client()
        bucket = gcs_client.bucket(gcs_bucket_name)
        print(f"✅ Connected to Google Cloud bucket: {gcs_bucket_name}")

        for prefix in gcs_prefixes:
            blobs = gcs_client.list_blobs(gcs_bucket_name, prefix=prefix)
            for blob in blobs:
                if blob.name.endswith("/"):  # Skip folders
                    continue

                print(f"⬇️ Downloading: {blob.name}")
                blob_data = blob.download_as_bytes()

                # Azure blob path
                blob_url = f"{azure_container_url}/{blob.name}?{azure_sas_token}"
                blob_client = BlobClient.from_blob_url(blob_url)

                print(f"⬆️ Uploading to Azure: {blob.name}")
                blob_client.upload_blob(blob_data, overwrite=True)

        print("✅ All files transferred successfully.")

    except Exception as e:
        print("❌ An error occurred during transfer:", e)



if __name__ == "__main__":
    gcp_credentials_file = ".\src\cairdio-dev-8f435-2e1bb339037a.json"
    gcs_bucket_name = "nexus-rhd-data"
    gcs_prefixes = ["metadata/", "metadata_fields.txt", "recordings/"]

    azure_container_url = "https://wsadsml5029665853.blob.core.windows.net/cardiorhddata"
    azure_sas_token = "sp=rcwdl&st=2025-06-09T15:34:27Z&se=2026-01-01T00:34:27Z&spr=https&sv=2024-11-04&sr=c&sig=xiMml%2BGPQKj17%2BZDvLORt2HS3Is1%2BzaMokFdyGUnW8M%3D"






    transfer_gcs_to_azure(
        gcp_credentials_file,
        gcs_bucket_name,
        gcs_prefixes,
        azure_container_url,
        azure_sas_token
    )
