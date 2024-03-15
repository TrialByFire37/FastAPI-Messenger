import os
import unittest
from http.client import HTTPException
from unittest.mock import AsyncMock, Mock, ANY, MagicMock
from unittest.mock import patch

from fastapi import HTTPException, status

from aws.constants import MB, SUPPORTED_FILE_TYPES_FORM_AUDIO, SUPPORTED_FILE_TYPES_FORM_VIDEO, \
    SUPPORTED_FILE_TYPES_FORM_IMAGE
from aws.service import upload, upload_from_base64, download, get_url, compress_image, compress_video


class TestService(unittest.IsolatedAsyncioTestCase):

    # @patch('aws.service.s3_upload')
    # @patch('aws.service.get_url')
    # @patch('aws.service.shotstack_sdk.ApiClient')
    # @patch('aws.service.shotstack_sdk.EditApi')
    # @patch('aws.service.time.sleep', MagicMock())
    # async def test_compress_video(self, mock_edit_api, mock_api_client, mock_get_url, mock_s3_upload):
    #     video_data = b'fake_video_data'
    #     file_type = 'mp4'
    #     resize_flag = False
    #
    #     mock_edit_api_instance = MagicMock()
    #     mock_edit_api.return_value = mock_edit_api_instance
    #
    #     mock_get_url.return_value = 'fake_url'
    #
    #     mock_api_instance = MagicMock()
    #     mock_api_client.return_value = mock_api_instance
    #
    #     mock_probe_response = {
    #         'response': {
    #             'metadata': {
    #                 'streams': [{'codec_type': 'video', 'duration': 10}]
    #             }
    #         }
    #     }
    #     mock_api_instance.probe.return_value = mock_probe_response
    #
    #     mock_post_render_response = {'response': {'id': 'fake_id'}}
    #     mock_api_instance.post_render.return_value = mock_post_render_response
    #
    #     mock_get_render_response_done = {'response': {'status': 'done', 'url': 'fake_rendered_url'}}
    #     mock_get_render_response_processing = {'response': {'status': 'processing'}}
    #     mock_api_instance.get_render.side_effect = [mock_get_render_response_processing, mock_get_render_response_done]
    #
    #     result = await compress_video(video_data, file_type, resize_flag)
    #
    #     self.assertEqual(result.file_name, 'fake_rendered_url')


    # todo: все ок
    async def test_compress_image_invalid(self):
        invalid_image_data = b""

        with self.assertRaises(HTTPException):
            await compress_image("jpg", invalid_image_data)


    @patch('aws.service.s3_upload', new_callable=AsyncMock)
    @patch('aws.service.compress_image', new_callable=AsyncMock)
    @patch('aws.service.Image.open', new_callable=MagicMock)
    @patch('aws.service.base64.b64decode', new_callable=MagicMock)
    async def test_upload_from_base64_unauthorized_file_type(self, mock_decode, mock_image_open, mock_compress_image,
                                                             mock_s3_upload):
        file_type = 'image/xpng'
        base64_data = os.urandom(8 * MB)
        mock_decode.return_value = base64_data
        mock_image_open.return_value.size = (200, 200)
        mock_compress_image.return_value = MagicMock()
        mock_s3_upload.return_value = MagicMock()
        with self.assertRaises(HTTPException) as context:
            result = await upload_from_base64(str(base64_data), file_type)

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail,
                         f'Unsupported file type: {file_type}. '
                         f'Supported types are {SUPPORTED_FILE_TYPES_FORM_AUDIO}'
                         f'{SUPPORTED_FILE_TYPES_FORM_VIDEO}'
                         f'{SUPPORTED_FILE_TYPES_FORM_IMAGE}')

    @patch('aws.service.s3_upload', new_callable=AsyncMock)
    @patch('aws.service.compress_image', new_callable=AsyncMock)
    @patch('aws.service.Image.open', new_callable=MagicMock)
    @patch('aws.service.base64.b64decode', new_callable=MagicMock)
    async def test_upload_from_base64_image(self, mock_decode, mock_image_open, mock_compress_image, mock_s3_upload):
        base64_data = os.urandom(3 * MB)
        mock_decode.return_value = base64_data
        mock_image_open.return_value.size = (200, 200)
        mock_compress_image.return_value = MagicMock()
        mock_s3_upload.return_value = MagicMock()

        result = await upload_from_base64(str(base64_data), 'image/png')

        assert result.file_name == mock_s3_upload.call_args[1]['key']

    @patch('aws.service.s3_upload', new_callable=AsyncMock)
    @patch('aws.service.compress_image', new_callable=AsyncMock)
    @patch('aws.service.Image.open', new_callable=MagicMock)
    @patch('aws.service.base64.b64decode', new_callable=MagicMock)
    async def test_upload_from_base64_image_width_or_height_too_small(self, mock_decode, mock_image_open,
                                                                      mock_compress_image, mock_s3_upload):
        base64_data = os.urandom(3 * MB)
        mock_decode.return_value = base64_data
        mock_image_open.return_value.size = (99, 50)
        mock_compress_image.return_value = MagicMock()
        mock_s3_upload.return_value = MagicMock()

        with self.assertRaises(HTTPException) as context:
            result = await upload_from_base64(str(base64_data), 'image/png')

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail,
                         'Image size is too small. More than 100x100 is required.'
                         )

    @patch('aws.service.s3_upload')
    @patch('aws.service.compress_video')
    @patch('aws.service.av.open')
    @patch('aws.service.base64.b64decode')
    async def test_upload_from_base64_video_compress(self, mock_decode, mock_av_open, mock_compress_video,
                                                     mock_s3_upload):
        base64_data = os.urandom(3 * MB)
        mock_decode.return_value = base64_data
        mock_av_open.return_value.streams.video[0].width = 1920
        mock_av_open.return_value.streams.video[0].height = 1080
        mock_compress_video.return_value = MagicMock()
        mock_s3_upload.return_value = MagicMock()

        result = await upload_from_base64(str(base64_data), 'video/mp4')

        assert result is not None

    @patch('aws.service.s3_upload')
    @patch('aws.service.compress_video')
    @patch('aws.service.av.open')
    @patch('aws.service.base64.b64decode')
    async def test_upload_from_base64_video(self, mock_decode, mock_av_open, mock_compress_video,
                                            mock_s3_upload):
        base64_data = os.urandom(3 * MB)
        mock_decode.return_value = base64_data
        mock_av_open.return_value.streams.video[0].width = 900
        mock_av_open.return_value.streams.video[0].height = 900
        mock_compress_video.return_value = MagicMock()
        mock_s3_upload.return_value = MagicMock()

        result = await upload_from_base64(str(base64_data), 'video/mp4')

        assert result.file_name == mock_s3_upload.call_args[1]['key']

    @patch('aws.service.s3_upload')
    @patch('aws.service.compress_video')
    @patch('aws.service.av.open')
    @patch('aws.service.Image.open')
    @patch('aws.service.base64.b64decode')
    async def test_upload_from_base64_video_size_too_big(self, mock_decode, mock_image_open, mock_av_open,
                                                         mock_compress_video, mock_s3_upload):
        max_size = 50 * MB
        base64_data = os.urandom(max_size + 1)
        mock_decode.return_value = base64_data
        mock_image_open.return_value.size = (200, 200)
        mock_av_open.return_value.streams.video[0].width = 900
        mock_av_open.return_value.streams.video[0].height = 900
        mock_compress_video.return_value = MagicMock()
        #mock_compress_image.return_value = MagicMock()
        mock_s3_upload.return_value = MagicMock()
        with self.assertRaises(HTTPException) as context:
            await upload_from_base64(str(base64_data), 'video/mp4')

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail,
                         f'Video file size exceeds the maximum allowed one of {max_size / MB} MB. Try another one.')

    @patch('aws.service.s3_upload', new_callable=AsyncMock)
    @patch('aws.service.base64.b64decode', new_callable=MagicMock)
    async def test_upload_from_base64_audio(self, mock_decode, mock_s3_upload):
        base64_data = os.urandom(3 * MB)
        mock_decode.return_value = base64_data
        mock_s3_upload.return_value = MagicMock()

        result = await upload_from_base64(str(base64_data), 'audio/mpeg')

        assert result.file_name == mock_s3_upload.call_args[1]['key']

    @patch('aws.service.s3_upload', new_callable=AsyncMock)
    @patch('aws.service.base64.b64decode', new_callable=MagicMock)
    async def test_upload_from_base64_audio_size_too_big(self, mock_decode, mock_s3_upload):
        max_size = 8 * MB
        base64_data = os.urandom(max_size + 1)
        mock_decode.return_value = base64_data
        mock_s3_upload.return_value = MagicMock()
        with self.assertRaises(HTTPException) as context:
            result = await upload_from_base64(str(base64_data), 'audio/mpeg')

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail,
                         f'Audio file size exceeds the maximum allowed one of {max_size / MB} MB. Try another one.')

    async def test_upload_from_base64_no_base64_data(self):
        base64_data = ''
        with self.assertRaises(HTTPException) as context:
            await upload_from_base64(base64_data, 'image/jpeg')

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, 'Base64 data not found!')

    async def test_upload_image_size_too_big(self):
        current_bytes = os.urandom(10 * MB + 1)
        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=current_bytes)

        mock_image = MagicMock()
        mock_image.size = (1000, 1000)

        with patch('PIL.Image.open', return_value=mock_image):
            with patch('aws.service.s3_upload', new_callable=AsyncMock) as mock_s3_upload:
                with patch('magic.from_buffer', return_value='image/jpeg') as mock_magic:
                    with self.assertRaises(HTTPException) as context:
                        await upload(mock_file)

        mock_magic.assert_called_once_with(buffer=current_bytes, mime=True)

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail,
                         'Image file size should not exceed 10 MB. ')

    async def test_upload_image_size_too_small(self):
        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=b"file content")

        mock_image = MagicMock()
        mock_image.size = (5, 5)

        with patch('PIL.Image.open', return_value=mock_image):
            with patch('aws.service.s3_upload', new_callable=AsyncMock) as mock_s3_upload:
                with patch('magic.from_buffer', return_value='image/jpeg') as mock_magic:
                    with self.assertRaises(HTTPException) as context:
                        await upload(mock_file)

        mock_magic.assert_called_once_with(buffer=b"file content", mime=True)

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail,
                         'Image size is too small to be previewed. More than 10x10 is required.')

    async def test_upload_image_size_and_compression(self):
        mock_file = Mock()
        mock_file.read = AsyncMock(return_value=b"file content")

        mock_image = MagicMock()
        mock_image.size = (2049, 1081)

        with patch('PIL.Image.open', return_value=mock_image):
            with patch('aws.service.compress_image', new_callable=AsyncMock,
                       return_value=b"compressed content") as mock_compress:
                with patch('aws.service.s3_upload', new_callable=AsyncMock) as mock_s3_upload:
                    with patch('magic.from_buffer', return_value='image/jpeg') as mock_magic:
                        result = await upload(mock_file)

        mock_compress.assert_called_once_with('image/jpeg', b"file content")

        mock_s3_upload.assert_called_once_with(contents=b"compressed content", key=ANY)

        mock_magic.assert_called_once_with(buffer=b"file content", mime=True)

        assert result.file_name == mock_s3_upload.call_args[1]['key']

    async def test_upload_with_no_file(self):
        with self.assertRaises(HTTPException) as context:
            await upload()

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, 'File not found!')

    async def test_upload(self):
        mock_file = Mock()
        mock_file.read = AsyncMock(return_value=b"file content")

        mock_image = MagicMock()
        mock_image.size = (2049, 1081)

        with patch('PIL.Image.open', return_value=mock_image):
            with patch('aws.service.s3_upload', new_callable=AsyncMock) as mock_s3_upload:
                with patch('magic.from_buffer', return_value='image/jpeg') as mock_magic:
                    result = await upload(mock_file)

        mock_s3_upload.assert_called_once_with(contents=b"", key=ANY)

        mock_magic.assert_called_once_with(buffer=b"file content", mime=True)

        assert result.file_name == mock_s3_upload.call_args[1]['key']

    async def test_upload_unsupported_file_type(self):
        file_type = 'unsupported/filetype'
        mock_file = Mock()
        mock_file.read = AsyncMock(return_value=b"file content")

        with patch('aws.service.s3_upload', new_callable=AsyncMock) as mock_s3_upload:
            with patch('magic.from_buffer', return_value=file_type) as mock_magic:
                with self.assertRaises(HTTPException) as context:
                    await upload(mock_file)

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, f'Unsupported file type: {file_type}.')

        mock_s3_upload.assert_not_called()

        mock_magic.assert_called_once_with(buffer=b"file content", mime=True)

    async def test_get_url(self):
        with patch('aws.service.s3_URL') as mock_s3_URL:
            mock_s3_URL.return_value = 'http://example.com/image.jpg'

            file_name = 'image.jpg'

            result = await get_url(file_name)

            self.assertEqual(result, 'http://example.com/image.jpg')

    async def test_get_url_with_no_file_name(self):
        with self.assertRaises(HTTPException) as context:
            await get_url()

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, 'No file name provided.')

    async def test_download(self):
        with patch('aws.service.s3_download') as mock_s3_download:
            mock_s3_download.return_value = b'fake file data'

            file_name = 'image.jpg'

            result = await download(file_name)

            self.assertEqual(result.headers['Content-Type'], 'application/octet-stream')

    async def test_download_with_no_file_name(self):
        with self.assertRaises(HTTPException) as context:
            await download()

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, 'No file name provided.')
