import base64
from io import BytesIO
from typing import Optional
from uuid import uuid4

import av
import magic
from PIL import Image
from fastapi import HTTPException, Response, UploadFile, status

from aws.constants import MB, SUPPORTED_FILE_TYPES_FORM_IMAGE, SUPPORTED_FILE_TYPES_FORM_AUDIO, \
    SUPPORTED_FILE_TYPES_FORM_VIDEO, SUPPORTED_FILE_TYPES_FORM_APPLICATION
from aws.schemas import FileRead
from aws.utils import s3_download, s3_upload, s3_URL


async def compress_video(video_data: bytes) -> bytes:
    try:
        # Create a BytesIO object from the passed video_data
        video_stream = BytesIO(video_data)

        # Open video container
        container = av.open(video_stream)

        # Get video stream details
        video_stream_info = container.streams.video[0]
        width = video_stream_info.width
        height = video_stream_info.height

        if width >= 1920 or height >= 1080:
            # Scale the video if needed
            output_options = {'c:v': 'libx264', 'vf': 'scale=1280:720'}
            output_stream = av.open('pipe:', format='mp4', mode='w')
            for frame in container.decode(video=0):
                output_stream.encode(frame)
            output_stream.close()
            compressed_video_data = output_stream.muxed
        else:
            compressed_video_data = video_data

        return compressed_video_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error compressing video: {str(e)}'
        )


async def compress_image(file_type: str, image_data: bytes) -> bytes:
    try:
        img = Image.open(BytesIO(image_data))
        width, height = img.size
        img_io = BytesIO()

        if width > 2048 or height > 1080:
            img = img.resize((2048, 1080))

        img.save(img_io, format=SUPPORTED_FILE_TYPES_FORM_IMAGE[file_type])

        return img_io.getvalue()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error compressing image: {str(e)}'
        )


async def upload_from_base64(base64_data: str, file_type: str) -> Optional[FileRead]:
    if not base64_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Base64 data not found!'
        )

    contents = base64.b64decode(base64_data)
    size = len(contents)

    file_name = ''

    if file_type in SUPPORTED_FILE_TYPES_FORM_AUDIO:
        max_size = 8 * MB
        error_message = f'Audio file size exceeds the maximum allowed one of {max_size / MB} MB. Try another one.'

    elif file_type in SUPPORTED_FILE_TYPES_FORM_VIDEO:
        max_size = 50 * MB if file_type in ['video/mp4', 'video/webm'] else 8 * MB
        error_message = f'Video file size exceeds the maximum allowed one of {max_size / MB} MB. Try another one.'
        if size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        if size > 8 * MB:
            contents = await compress_video(contents)

    elif file_type in SUPPORTED_FILE_TYPES_FORM_IMAGE:
        max_size = 10 * MB
        error_message = 'Image file size should not exceed 10 MB.'
        img = Image.open(BytesIO(contents))
        width, height = img.size

        if width <= 10 or height <= 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Image size is too small to be previewed. More than 10x10 is required.'
            )
        if (width > 2048 or height > 1080) or (1 * MB <= size <= 10 * MB):
            contents = await compress_image(file_type, contents)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unsupported file type: {file_type}. '
                   f'Supported types are {SUPPORTED_FILE_TYPES_FORM_AUDIO + SUPPORTED_FILE_TYPES_FORM_VIDEO + SUPPORTED_FILE_TYPES_FORM_IMAGE}'
        )

    if size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES_FORM_APPLICATION[file_type]}'
    await s3_upload(contents=contents, key=file_name)
    return FileRead(file_name=file_name)


async def upload(file: Optional[UploadFile] = None) -> Optional[FileRead]:
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File not found!'
        )

    contents = await file.read()
    size = len(contents)

    file_type = magic.from_buffer(buffer=contents, mime=True)
    file_name = ''

    if file_type in SUPPORTED_FILE_TYPES_FORM_IMAGE:
        try:
            img = Image.open(BytesIO(contents))
            width, height = img.size

            if width <= 10 or height <= 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Image size is too small to be previewed. More than 10x10 is required.'
                )
            if (width > 2048 or height > 1080) or (1 * MB <= size <= 10 * MB):
                contents = await compress_image(file_type, BytesIO(contents))
            if size > 10 * MB:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Image file size should not exceed 10 MB. '
                )
            file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES_FORM_APPLICATION[file_type]}'
        except Exception as e:
            print("Compression failed.")
            pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unsupported file type: {file_type}. '
                   f'Supported types are {SUPPORTED_FILE_TYPES_FORM_AUDIO + SUPPORTED_FILE_TYPES_FORM_VIDEO + SUPPORTED_FILE_TYPES_FORM_IMAGE}'
        )

    await s3_upload(contents=contents, key=file_name)
    return FileRead(file_name=file_name)


# async def upload_from_base64(base64_data: str, file_type: str) -> Optional[FileRead]:
#     if not base64_data:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail='Base64 data not found!'
#         )
#
#     contents = base64.b64decode(base64_data)
#     size = len(contents)
#
#     file_name = ''
#
#     if file_type in SUPPORTED_FILE_TYPES_FORM_AUDIO:
#         max_size = 8 * MB
#         error_message = f'Audio file size exceeds the maximum allowed one of {max_size/MB} MB. Try another one.'
#     elif file_type in SUPPORTED_FILE_TYPES_FORM_VIDEO:
#         if file_type == 'video/mp4' or file_type == 'video/webm':
#             max_size = 50 * MB
#         else:
#             max_size = 8 * MB
#         error_message = f'Video file size exceeds the maximum allowed one of {max_size/MB} MB. Try another one.'
#
#     elif file_type in SUPPORTED_FILE_TYPES_FORM_IMAGE:
#         max_size = 10 * MB
#         error_message = 'Image file size should not exceed 10 MB.'
#         img = Image.open(BytesIO(contents))
#         width, height = img.size
#
#         if width <= 10 or height <= 10:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail='Image size is too small to be previewed. More than 10x10 is required.'
#             )
#         if (width > 2048 or height > 1080) or (1 * MB <= size <= 10 * MB):
#             contents = await compress_image(file_type, BytesIO(contents))
#
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f'Unsupported file type: {file_type}. '
#                    f'Supported types are {SUPPORTED_FILE_TYPES_FORM_AUDIO + SUPPORTED_FILE_TYPES_FORM_VIDEO + SUPPORTED_FILE_TYPES_FORM_IMAGE}'
#         )
#
#     if size > max_size:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=error_message
#         )
#
#     file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES_FORM_IMAGE[file_type]}' if file_type in SUPPORTED_FILE_TYPES_FORM_IMAGE else file_name
#     await s3_upload(contents=contents, key=file_name)
#     return FileRead(file_name=file_name)
#


async def get_url(file_name: Optional[str] = None):
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file name provided.'
        )

    contents = await s3_URL(key=file_name)
    return contents


async def download(file_name: Optional[str] = None) -> Response:
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file name provided.'
        )

    contents = await s3_download(key=file_name)
    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'attachment;filename={file_name}',
            'Content-Type': 'application/octet-stream',
        }
    )
