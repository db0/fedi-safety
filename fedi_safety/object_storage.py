import boto3
from botocore.exceptions import ClientError
import os
from loguru import logger
import sys
import PIL.Image
from io import BytesIO
from fedi_safety.config import Config

object_storage_endpoint = Config.object_storage_endpoint
if object_storage_endpoint is None:
    logger.error("You need to provide an OBJECT_STORAGE_ENDPOINT var in your .env file")
    sys.exit(1)
pictrs_bucket = Config.pictrs_bucket
if pictrs_bucket is None:
    logger.error("You need to provide a PICTRS_BUCKET var in your .env file")
    sys.exit(1)

s3_client = boto3.client('s3', endpoint_url=object_storage_endpoint)
s3_resource = boto3.resource('s3', endpoint_url=object_storage_endpoint)
s3_bucket = s3_resource.Bucket(pictrs_bucket)

def download_image(key):
    try:
        response = s3_client.get_object(Bucket=pictrs_bucket, Key=key)
    except ClientError as e:
        logger.error(f"Error encountered while downloading {key}: {e}")
        return None
    img = response['Body'].read()
    img = PIL.Image.open(BytesIO(img))
    return img

def delete_image(key):
    response = s3_client.delete_object(
        Bucket=pictrs_bucket,
        Key=key
    )

def get_all_images_after(cutoff_time):
    s3_paginator = s3_client.get_paginator('list_objects_v2')
    s3_iterator = s3_paginator.paginate(Bucket=pictrs_bucket)
    cutoff_time_str = cutoff_time.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Starting seek of images after: {cutoff_time_str}")
    filtered_iterator = s3_iterator.search(
        f"Contents[?to_string(LastModified)>='\"{cutoff_time_str}+00:00\"'].Key"
    )
    return filtered_iterator

def get_all_images(prefix=None):
    if prefix:
        return s3_bucket.objects.filter(Prefix=prefix)
    return s3_bucket.objects.all()