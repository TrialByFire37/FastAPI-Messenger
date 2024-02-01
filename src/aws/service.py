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

import io
import ffmpeg

VVV = {
    'video/mp4': ['mp4', 'aac', 'h264'],
    'video/webm': ['webm', 'vorbis', 'vp8'],
    'video/avi': ['avi', 'mp3', 'mpeg4'],
    'video/mov': ['mov', 'aac', 'h264']
}


async def compress_video(video_data: bytes, file_type: str) -> bytes:
    try:
        # Определение формата и кодеков
        format_name, audio_codec, video_codec = VVV.get(file_type)

        # Создание file-like объекта
        video_file = BytesIO(video_data)

        # Получение информации о видео
        probe = ffmpeg.probe(video_data)
        video_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        width = int(video_info['width'])
        height = int(video_info['height'])

        # Проверка соотношения сторон
        aspect_ratio = width / height
        standard_ratios = [1, 4 / 3, 16 / 9, 16 / 10]
        if aspect_ratio not in standard_ratios:
            raise ValueError("Видео не соответствует стандартным соотношениям сторон")

        # Установка параметров сжатия
        resolution = '720p' if max(width, height) > 720 else None

        mem_in_MiB = len(video_data) / MB

        crf = 18
        if resolution is None:
            if 8 < mem_in_MiB <= 10:
                crf = 19
            elif 10 < mem_in_MiB <= 12:
                crf = 20
            elif 12 < mem_in_MiB <= 15:
                crf = 21
            elif 15 < mem_in_MiB <= 20:
                crf = 22
            elif 20 < mem_in_MiB <= 25:
                crf = 23
            elif 25 < mem_in_MiB <= 30:
                crf = 24
            elif 30 < mem_in_MiB <= 35:
                crf = 25
            elif 35 < mem_in_MiB <= 40:
                crf = 26
            elif 40 < mem_in_MiB <= 45:
                crf = 27
            elif 45 < mem_in_MiB <= 50:
                crf = 28
            else:
                crf = 40

        # Перекодирование видео
        output_file = BytesIO()
        ffmpeg.input('pipe:0').output('pipe:1', format=format_name, vcodec=video_codec, acodec=audio_codec, crf=crf,
                                      vf='scale=-1:720' if resolution else None).run(input=video_file,
                                                                                     output=output_file)

        return output_file.getvalue()

    except Exception as e:
        print(f"Ошибка при сжатии видео: {e}")
        return video_data


async def compress_image(file_type: str, image_data: bytes) -> bytes:
    try:
        img = Image.open(BytesIO(image_data))
        width, height = img.size
        img_io = BytesIO()

        if width >= 2048 or height >= 1080:
            img.thumbnail((2048, 1080))

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

    if file_type in SUPPORTED_FILE_TYPES_FORM_AUDIO:
        max_size = 8 * MB
        error_message = f'Audio file size exceeds the maximum allowed one of {max_size / MB} MB. Try another one.'

    elif file_type in SUPPORTED_FILE_TYPES_FORM_VIDEO:
        max_size = 50 * MB
        error_message = f'Video file size exceeds the maximum allowed one of {max_size / MB} MB. Try another one.'

        container = av.open(BytesIO(contents))
        video_stream_info = container.streams.video[0]
        width = video_stream_info.width
        height = video_stream_info.height

        resize_flag = width >= 1920 or height >= 1080
        size_flag = size >= 8 * MB

        if resize_flag or size_flag:
            contents = await compress_video(contents, file_type)

    elif file_type in SUPPORTED_FILE_TYPES_FORM_IMAGE:
        max_size = 10 * MB
        error_message = 'Image file size should not exceed 10 MB.'
        img = Image.open(BytesIO(contents))
        width, height = img.size

        if width <= 100 or height <= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Image size is too small. More than 100x100 is required.'
            )
        if (width > 2048 or height > 1080) or (1 * MB <= size <= 10 * MB):
            contents = compress_image(file_type, contents)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unsupported file type: {file_type}. '
                   f'Supported types are {SUPPORTED_FILE_TYPES_FORM_AUDIO}'
                   f'{SUPPORTED_FILE_TYPES_FORM_VIDEO}'
                   f'{SUPPORTED_FILE_TYPES_FORM_IMAGE}'
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
                contents = await compress_image(file_type, contents)
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
