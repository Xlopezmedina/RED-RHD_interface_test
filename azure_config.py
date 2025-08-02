from azure.identity import AzureCliCredential
from azure.ai.ml import MLClient

def get_ml_client(subscription_id, resource_group, workspace_name):
    return MLClient(
        credential=AzureCliCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name,
    )
