#Download WAV file from Blob Storage


from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobClient
import os

def download_blob(blob_url, local_path, sas_token):
    """
    Download all .wav files from an Azure Blob Storage container using a SAS token.

    Parameters:
        blob_url (str): Full container URL, e.g., "https://<account>.blob.core.windows.net/<container>"
        local_path (str): Local directory to save downloaded files.
        sas_token (str): Shared Access Signature token (no '?' prefix).
    
    Returns:
        List[str]: Paths to downloaded files.
    """
    container_url = f"{blob_url}?{sas_token}"
    container_client = ContainerClient.from_container_url(container_url)

    os.makedirs(local_path, exist_ok=True)
    downloaded_files = []

    for blob in container_client.list_blobs():
        if blob.name.endswith(".wav"):
            blob_client = container_client.get_blob_client(blob.name)
            local_file_path = os.path.join(local_path, os.path.basename(blob.name))

            with open(local_file_path, "wb") as f:
                f.write(blob_client.download_blob().readall())

            print(f"⬇️ Downloaded: {blob.name}")
            downloaded_files.append(local_file_path)

    return downloaded_files


def upload_embedding_to_blob(local_path, blob_url, sas_token):
    blob_name = f"embeddings/{os.path.basename(local_path)}"
    full_url = f"{blob_url}/{blob_name}?{sas_token}"
    blob_client = BlobClient.from_blob_url(full_url)
    with open(local_path, "rb") as f:
        blob_client.upload_blob(f, overwrite=True)
    print(f"⬆️ Uploaded embedding: {blob_name}")