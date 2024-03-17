import unittest

from aws.utils import s3_upload, s3_URL, s3_download


class TestService(unittest.IsolatedAsyncioTestCase):

    # todo: (21) Тест загрузки в s3
    async def test_s3_upload(self):
        contents = b"File contents"
        key = "test_file.txt"
        await s3_upload(contents, key)


    # todo: (22) Тест загрузки в s3 - ValueError
    async def test_s3_upload_value_error(self):
        contents = b"File contents"
        key = ""
        with self.assertRaises(ValueError):
            await s3_upload(contents, key)


    # todo: (23) Тест генерации ссылки s3
    async def test_s3_URL(self):
        key = "test_file.txt"
        await s3_URL(key)


    # todo: (24) Тест скачивания из s3
    async def test_s3_download(self):
        key = "test_file.txt"
        await s3_download(key)
