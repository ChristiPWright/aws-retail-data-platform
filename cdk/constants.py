import uuid
import os

PROJ_NAME = os.environ.get("BUCKET_PREFIX_CUSTOM", "aws-retail-data-platform" ) 
ENV_NAME = os.environ.get("ENV_NAME", "dev")
AWS_USERNAME = os.environ.get("AWS_USERNAME", "") 
SHORT_UUID = str(uuid.uuid4())[:8]

BUCKET_PREFIX = f"{PROJ_NAME}-{AWS_USERNAME}-{SHORT_UUID}"
# consider BUCKET_PREFIX = f"{PROJ_NAME}-{AWS_USERNAME}-{SHORT_UUID}".lower().replace("_", "-") to avoid invalid bucket