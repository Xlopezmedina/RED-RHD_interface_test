import os
import numpy as np
import json
from collections import defaultdict

# Directory with embeddings
EMBEDDING_DIR = "data/embeddings"

# File mapping embeddings to regions
METADATA_FILE = "data/embedding_region_map.csv"

# Output profile
OUTPUT_FILE = "data/region_profiles.json"

def compute_profiles(embedding_dir, metadata_file):
    region_data = defaultdict(list)

    # Load metadata: CSV with filename,region
    with open(metadata_file, "r") as f:
        for line in f.readlines()[1:]:  # Skip header
            fname, region = line.strip().split(",")
            fpath = os.path.join(embedding_dir, fname)
            embedding = np.load(fpath)
            region_data[region].append(embedding)

    # Compute mean and covariance for each region
    region_profiles = {}
    for region, embeddings in region_data.items():
        X = np.vstack(embeddings)
        mean = np.mean(X, axis=0).tolist()
        cov = np.cov(X, rowvar=False).tolist()
        region_profiles[region] = {
            "mean": mean,
            "cov": cov
        }

    return region_profiles

if __name__ == "__main__":
    profiles = compute_profiles(EMBEDDING_DIR, METADATA_FILE)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

    print(f"✅ Region profiles saved to: {OUTPUT_FILE}")
