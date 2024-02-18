from io import BytesIO
from PIL import Image
import pytest

from aws.service import compress_image, compress_video


@pytest.mark.parametrize("file_type, image_path", [
    ("jpg", "resources/1653975016_28.jpg"),
])
async def test_compress_image(file_type, image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()

    compressed_image_data = await compress_image(file_type, image_data)

    assert len(compressed_image_data) < len(image_data)

    compressed_img = Image.open(BytesIO(compressed_image_data))
    width, height = compressed_img.size
    assert width <= 2048
    assert height <= 1080


# todo: определиться с тем, как закидывать для тестов видеофайлы (очевидно, что не в гит грузить)
# @pytest.mark.parametrize("file_type, video_path, resize_flag", [
#     ("mp4", "path_to_large_video", True),
# ])
# async def test_compress_video_valid_data(file_type, video_path, resize_flag):
#     with open(video_path, "rb") as f:
#         video_data = f.read()
#
#     compressed_video_data = await compress_video(video_data, file_type, resize_flag)
#
#     assert len(compressed_video_data) < len(video_data)