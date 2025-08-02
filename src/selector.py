import json
import numpy as np
from scipy.spatial.distance import mahalanobis

import numpy as np

def mahalanobis_distance(x, mean, cov):
    return np.sqrt((x - mean).T @ np.linalg.inv(cov) @ (x - mean))

def select_region_profile(embedding, region_profiles):
    best_region = None
    best_distance = float('inf')
    for region, stats in region_profiles.items():
        mean = np.array(stats['mean'])
        cov = np.array(stats['cov'])
        dist = mahalanobis_distance(embedding, mean, cov)
        if dist < best_distance:
            best_distance = dist
            best_region = region
    return best_region
