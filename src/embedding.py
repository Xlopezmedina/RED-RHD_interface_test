import openl3
import librosa
import numpy as np

import random
import string

def extract_embedding(audio_path):
    """
    Extract OpenL3 512-dimensional embedding from a heart sound audio file.
    
    Uses:
    - input_repr='mel256'
    - content_type='env'
    - embedding_size=512
    - mean pooling over time
    """
    print(f"🔎 Extracting OpenL3 embedding from {audio_path}")

    # Load audio with high enough sample rate for PCG
    audio, sr = librosa.load(audio_path, sr=48000)
    print(f"   🎼 Loaded audio: sr={sr}, duration={len(audio)/sr:.2f}s")

    # Extract OpenL3 embeddings
    embeddings, _ = openl3.get_audio_embedding(
        audio,
        sr,
        input_repr="mel256",
        content_type="env",
        embedding_size=512
    )

    print(f"   📐 Raw embedding shape: {embeddings.shape}")

    # Mean pool over time axis
    pooled_embedding = np.mean(embeddings, axis=0)
    print(f"   ✅ Pooled embedding shape: {pooled_embedding.shape}")

    return pooled_embedding





def generate_random_patient_id(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def convert_embeddings_to_records(embedding_array):
    """
    embedding_array: shape (512,) or (n_samples, 512)
    Returns: list of dicts, each with 'Patient ID' + 512 features
    """
    # Make sure it's at least 2D
    if embedding_array.ndim == 1:
        embedding_array = embedding_array.reshape(1, -1)

    if embedding_array.shape[1] != 512:
        raise ValueError(f"Expected 512 features per row, got {embedding_array.shape[1]}")

    records = []
    for row in embedding_array:
        record = {"Patient ID": generate_random_patient_id()}
        for i, val in enumerate(row):
            record[f"openl3_feature_{i}"] = float(val)
        records.append(record)

    return records
