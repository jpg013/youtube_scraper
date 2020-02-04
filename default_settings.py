import os

# Grabs the folder where the script runs.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Set environment variable
DEBUG=True
SERVER_NAME="127.0.0.1:9080"
S3_ACCESS_KEY_ID="AKIAIWI5KF57TEG4Q3CA"
S3_SECRET_ACCESS_KEY="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"
S3_BUCKET="dunami-reporting-nonprod"