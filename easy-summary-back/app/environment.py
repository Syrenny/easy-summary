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
    faster_whisper_model: str
    faster_whisper_device: str
    faster_whisper_compute_type: str
    chat_model: str
    chat_model_t: float

    class Config:
        env_file = os.path.join(project_root, '.env')


credentials = Credentials()



