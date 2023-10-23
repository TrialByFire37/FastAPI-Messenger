from typing import Optional
from uuid import uuid4

import magic
from fastapi import HTTPException, Response, UploadFile, status

from aws.constants import MB, SUPPORTED_FILE_TYPES_FORM_IMAGE
from aws.utils import s3_download, s3_upload, s3_URL


async def upload(file: Optional[UploadFile] = None):
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file found!!'
        )

    contents = await file.read()
    size = len(contents)

    if not 0 < size <= 1 * MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Supported file size is 0 - 1 MB'
        )

    file_type = magic.from_buffer(buffer=contents, mime=True)
    if file_type not in SUPPORTED_FILE_TYPES_FORM_IMAGE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unsupported file type: {file_type}. Supported types are {SUPPORTED_FILE_TYPES_FORM_IMAGE}'
        )

    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES_FORM_IMAGE[file_type]}'
    await s3_upload(contents=contents, key=file_name)
    return {'file_name': file_name}


async def get_url(file_name: Optional[str] = None):
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file name provided'
        )

    contents = await s3_URL(key=file_name)
    return contents


async def download(file_name: Optional[str] = None):
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file name provided'
        )

    contents = await s3_download(key=file_name)
    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'attachment;filename={file_name}',
            'Content-Type': 'application/octet-stream',
        }
    )
