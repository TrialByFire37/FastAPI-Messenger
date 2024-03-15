import unittest

from aws.utils import s3_upload, s3_URL, s3_download


class TestService(unittest.IsolatedAsyncioTestCase):
    async def test_s3_upload(self):
        contents = b"File contents"
        key = "test_file.txt"
        await s3_upload(contents, key)

    async def test_s3_upload_value_error(self):
        contents = b"File contents"
        key = ""
        with self.assertRaises(ValueError):
            await s3_upload(contents, key)

    async def test_s3_URL(self):
        key = "test_file.txt"
        await s3_URL(key)

    async def test_s3_download(self):
        key = "test_file.txt"
        await s3_download(key)
