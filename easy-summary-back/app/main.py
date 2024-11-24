import os

import uvicorn
from fastapi import (FastAPI, WebSocket)
from fastapi.middleware.cors import CORSMiddleware

import socketio

from routers.root import sio

origins = [
    "http://localhost:3000",  # Для разработки на localhost
    "http://localhost:8000",  # Если вы используете другой порт
    "http://127.0.0.1:3000",  # Для IP-адреса
    "http://127.0.0.1:8000",  # Для IP-адреса
]

app_prefix = "/easy-summary"

app = FastAPI(
    openapi_url=f"{app_prefix}/docs_json",
    docs_url=f"{app_prefix}/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешенные источники
    allow_credentials=True,  # Разрешаем отправку куки и заголовков авторизации
    allow_methods=["*"],  # Разрешаем все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

def main():
    uvicorn.run(socket_app,
                host="0.0.0.0",
                port=7256)


if __name__ == '__main__':
    main()
