import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging

# It's good practice to set up a logger for utility functions
logger = logging.getLogger(__name__)

def generate_presigned_s3_url(object_key: str) -> str | None:
    """
    Generates a pre-signed URL for a given S3 object key.

    This function is designed to work with a CharField that stores the
    path to the file in S3 (e.g., 'profile_images/scdc9r8ud5pb1.jpg').

    Args:
        object_key: The key (path) of the object in the S3 bucket.

    Returns:
        A pre-signed URL string if successful, otherwise None.
    """
    if not object_key:
        return None

    # Initialize the S3 client using credentials from Django settings
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        # You might need to add this for pre-signed URLs
        config=boto3.session.Config(signature_version='s3v4')
    )

    try:
        # Generate the pre-signed URL.
        # The 'Key' is the object_key passed to the function.
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': object_key
            },
            ExpiresIn=3600  # URL expires in 1 hour (in seconds)
        )
        return presigned_url
    except ClientError as e:
        # Log the error for debugging purposes
        logger.error(f"Error generating pre-signed URL for key '{object_key}': {e}")
        return None