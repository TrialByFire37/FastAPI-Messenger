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


# todo: FS_Media_2: прикрепляешь совсем мелкие картинки - появляются сперва как пустые
# сообщение, и после перезагрузки страницы исчезают; 1080p не сжимается по соотношению до 720p; видео не сжимаются
# по весу (отсюда и не загружаются)

# todo: FS_Media_3: файлы любого формата можно прикрепить. Мб в проводнике задать ограничение для разрешений файлов?
async def compress_video(video_data: bytes, file_type: str) -> bytes:
    try:
        # Определение формата и кодеков
        format_name = SUPPORTED_FILE_TYPES_FORM_VIDEO.get(file_type)

        if format_name == 'mp4':
            audio_codec, video_codec = 'aac', 'h264'
        elif format_name == 'webm':
            audio_codec, video_codec = 'vorbis', 'vp8'
        elif format_name == 'avi':
            audio_codec, video_codec = 'mp3', 'mpeg4'
        elif format_name == 'mov':
            audio_codec, video_codec = 'aac', 'h264'

        # Создание контейнера для входного видео
        input_container = av.open(BytesIO(video_data), mode='r')

        # Создание байтового потока для выходного видео
        output_io = BytesIO()

        # Создание контейнера для выходного видео
        output_container = av.open(output_io, mode='w', format=format_name)

        # Создание потоков для выходного видео
        out_stream_v = output_container.add_stream(video_codec)
        out_stream_a = output_container.add_stream(audio_codec)

        # Перебор потоков входного видео
        for packet in input_container.demux():
            if packet.stream.type == 'video':
                # Декодирование пакета
                frames = packet.decode()

                for frame in frames:
                    # Проверка соотношения сторон
                    aspect_ratio = frame.width / frame.height
                    if aspect_ratio not in [1, 4 / 3, 16 / 9, 16 / 10]:
                        continue

                    # Проверка и изменение размера
                    if max(frame.width, frame.height) > 720:
                        out_stream_v.height = 720
                        out_stream_v.width = int(720 * aspect_ratio)

                    # Перекодирование фрейма
                    for packet in out_stream_v.encode(frame):
                        if packet.pts is not None and packet.time_base is not None and out_stream_v.time_base is not None:
                            packet.pts = int(packet.pts * out_stream_v.time_base / packet.time_base)
                        if packet.dts is not None and packet.time_base is not None and out_stream_v.time_base is not None:
                            packet.dts = int(packet.dts * out_stream_v.time_base / packet.time_base)
                        output_container.mux(packet)

            elif packet.stream.type == 'audio':
                # Перекодирование аудио
                for frame in packet.decode():
                    for packet in out_stream_a.encode(frame):
                        if packet.pts is not None and packet.time_base is not None and out_stream_a.time_base is not None:
                            packet.pts = int(packet.pts * out_stream_a.time_base / packet.time_base)
                        if packet.dts is not None and packet.time_base is not None and out_stream_a.time_base is not None:
                            packet.dts = int(packet.dts * out_stream_a.time_base / packet.time_base)
                        output_container.mux(packet)

        # Закрытие контейнеров
        input_container.close()
        output_container.close()

        # Возвращение сжатого видео
        return output_io.getvalue()

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
