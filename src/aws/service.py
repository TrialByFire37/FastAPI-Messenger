from io import BytesIO
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, Response, UploadFile, status
import ffmpeg
import magic
import os
from PIL import Image

from aws.constants import MB, SUPPORTED_FILE_TYPES_FORM_IMAGE, SUPPORTED_FILE_TYPES_FORM_AUDIO, \
    SUPPORTED_FILE_TYPES_FORM_VIDEO
from aws.schemas import FileRead
from aws.utils import s3_download, s3_upload, s3_URL


async def compress_video(video_name: str) -> bytes:
    try:
        probe = ffmpeg.probe(video_name)
        video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        width = video_info['width']
        height = video_info['height']

        if width >= 1920 or height >= 1080:
            ffmpeg.input(video_name).output(video_name, vf='scale=1280:720').run(overwrite_output=True)
        crf = 18
        while os.path.getsize(video_name) > 8 * MB:
            ffmpeg.input(video_name).output(video_name, crf=f'{crf}').run(overwrite_output=True)
            crf += 1

        with open(video_name, 'rb') as f:
            return f.read()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error compressing video: {str(e)}'
        )


async def compress_image(file_type: str, image_data: bytes) -> bytes:
    try:
        img = Image.open(image_data)
        width, height = img.size
        img_io = BytesIO()

        if width > 2048 or height > 1080:
            img.thumbnail((2048, 1080))

        img.save(img_io, f'{file_type.split("/")[1]}', quality='keep')
        image_file_size = img_io.tell()

        if file_type == "image/png":
            img = img.convert("P", palette=Image.ADAPTIVE, colors=256)
        if file_type == "image/jpg" or file_type == "image/jpeg":
            quality = 100
            while image_file_size > 1 * MB and quality >= 90:
                quality -= 1
                img = img.convert('RGB').quantize(colors=256, method=2).convert('RGB')
                img = img.resize((int(width * 0.9), int(height * 0.9)), Image.ANTIALIAS)
                img.save(img_io, f'{file_type.split("/")[1]}', quality=f'{quality}')

            if quality < 90:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Image quality could not be compressed within the acceptable range.'
                )

        img_bytes = img_io.getvalue()
        return img_bytes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error compressing image: {str(e)}'
        )


async def upload(file: Optional[UploadFile] = None) -> Optional[FileRead]:
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File not found!'
        )

    contents = await file.read()
    size = len(contents)

    file_type = magic.from_buffer(buffer=contents, mime=True)

    if file_type in SUPPORTED_FILE_TYPES_FORM_AUDIO:
        if size > 8 * MB:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Audio file size exceeds the maximum allowed one of 8 MB. Try another one.'
            )
    elif file_type in SUPPORTED_FILE_TYPES_FORM_VIDEO:
        try:
            if 8 * MB < size <= 50 * MB:
                contents = await compress_video(video_name=BytesIO(contents))
            elif size > 50 * MB:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Video file size exceeds the maximum allowed one of 50 MB. Try another one.'
                )
        except Exception as e:
            print("Compression failed.")
            pass
    elif file_type in SUPPORTED_FILE_TYPES_FORM_IMAGE:
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
        except Exception as e:
            print("Compression failed.")
            pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unsupported file type: {file_type}. '
                   f'Supported types are {SUPPORTED_FILE_TYPES_FORM_AUDIO + SUPPORTED_FILE_TYPES_FORM_VIDEO + SUPPORTED_FILE_TYPES_FORM_IMAGE}'
        )

    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES_FORM_IMAGE[file_type]}'
    await s3_upload(contents=contents, key=file_name)
    return FileRead(file_name=file_name)


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
