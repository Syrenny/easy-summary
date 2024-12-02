import os
import uuid
import time
import threading
from pathlib import Path

from pydantic_settings import BaseSettings
import requests


project_root = Path(__file__).parent.parent


class Credentials(BaseSettings):
    open_router_key: str
    salute_speech_auth_key: str

    class Config:
        env_file = os.path.join(project_root, '.env')


credentials = Credentials()



