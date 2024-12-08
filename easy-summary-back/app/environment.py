import os
import logging
from pathlib import Path

from pydantic_settings import BaseSettings


# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent


class Credentials(BaseSettings):
    production: bool = False
    open_router_key: str
    faster_whisper_model: str
    faster_whisper_device: str
    faster_whisper_compute_type: str
    chat_model: str
    chat_model_t: float

    class Config:
        env_file = os.path.join(project_root, '.env')

    def load_key_from_file(self):
        if self.production:
            try:
                with open(self.open_router_key, 'r') as file:
                    self.open_router_key = file.read().strip()
            except FileNotFoundError:
                raise ValueError(f"Файл с ключом не найден: {self.open_router_key}")
            except Exception as e:
                raise ValueError(f"Ошибка при чтении файла: {e}")

credentials = Credentials()
credentials.load_key_from_file()



