import os

from dotenv import load_dotenv


def get_config_by_key(key:str,default=None):
    load_dotenv()
    return os.getenv(key,default)