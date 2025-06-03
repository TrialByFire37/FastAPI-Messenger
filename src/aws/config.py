import os

from dotenv import load_dotenv


load_dotenv()


ENDPOINT = os.environ.get("ENDPOINT")
KEY_ID_RO = os.environ.get("KEY_ID_RO")
APPLICATION_KEY_RO = os.environ.get("APPLICATION_KEY_RO")
AWS_BUCKET = os.environ.get("AWS_BUCKET")
SHOTSTACK_API = os.environ.get("SHOTSTACK_API")