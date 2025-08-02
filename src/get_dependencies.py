import mlflow

model_uri = "C:/Users/MiguelALópez-Medina/red_rhd_model_downloaded"
mlflow.pyfunc.get_model_dependencies(model_uri)
