import logging
from typing import Optional

from botocore.exceptions import ClientError

from aws.client import client
from aws.config import AWS_BUCKET


async def s3_upload(contents: bytes, key: str) -> None:
    if len(key) == 0:
        raise ValueError("Invalid 'key' length: 0")

    logging.info(f'Uploading {key} to S3...')
    client.put_object(Key=key, Body=contents, Bucket=AWS_BUCKET)
    logging.info(f'{key} successfully uploaded to S3')


async def s3_URL(key: str) -> Optional[str]:
    return client.generate_presigned_url('get_object', Params={'Bucket': AWS_BUCKET, 'Key': key})


async def s3_download(key: str) -> bytes:
    logging.info(f'Downloading {key} from s3...')
    response = client.get_object(Bucket=AWS_BUCKET, Key=key)
    return response['Body'].read()
