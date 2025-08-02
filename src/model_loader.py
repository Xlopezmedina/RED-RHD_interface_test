import joblib
import tempfile

def load_model_for_region(region, ml_client):
    model = ml_client.models.get(name=f"redrhd-{region}-model", version="latest")
    with tempfile.TemporaryDirectory() as tmpdir:
        model.download(target_path=tmpdir, unpack=True)
        model_path = f"{tmpdir}/model.joblib"
        return joblib.load(model_path)
