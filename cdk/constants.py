import uuid
import os

PROJ_NAME = "aws-retail-data-platform"  
ENV_NAME = "dev"
AWS_USERNAME = os.environ.get("AWS_USERNAME", "") 
SHORT_UUID = str(uuid.uuid4())[:8]

BUCKET_PREFIX = f"{PROJ_NAME}-{AWS_USERNAME}-{SHORT_UUID}"