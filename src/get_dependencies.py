import mlflow

model_uri = "C:/Users/MiguelAL�pez-Medina/red_rhd_model_downloaded"
mlflow.pyfunc.get_model_dependencies(model_uri)
