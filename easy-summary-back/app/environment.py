import os
import uuid
import time
import threading
from pathlib import Path

from pydantic_settings import BaseSettings
import requests


project_root = Path(__file__).parent.parent


class Credentials(BaseSettings):
    salute_speech_auth_key: str
    salute_speech_access_token: str = ""

    class Config:
        env_file = os.path.join(project_root, '.env')


credentials = Credentials()


class TokenManager:
    def __init__(self, cred):
        self.cred = cred
        self.get_token()

    def get_token(self):
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        payload={
          'scope': 'SALUTE_SPEECH_PERS'
        }
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json',
          'RqUID': str(uuid.uuid4()),
          'Authorization': f'Basic {self.cred.salute_speech_auth_key}'
        }

        response = requests.request("POST", url, headers=headers, data=payload, verify=False).json()

        self.cred.salute_speech_access_token = response["access_token"]

        # Получаем текущее время в миллисекундах
        current_time_ms = int(time.time() * 1000)

        # Рассчитываем время до истечения токена
        time_left_ms = response["expires_at"] - current_time_ms

        # Вычитаем 60 секунд (60 000 миллисекунд), чтобы сработать за минуту до истечения токена
        trigger_time_ms = time_left_ms - 60000

        print(f"Обновление токена сработает через {trigger_time_ms / 1000} секунд.")
        print("Токен:", self.cred.salute_speech_access_token)

        threading.Timer(trigger_time_ms / 1000, self.get_token).start()

TokenManager(cred=credentials)



