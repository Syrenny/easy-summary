import asyncio
import io
from asyncio import Queue

import numpy as np
import socketio
from pydub import AudioSegment

from faster_whisper import WhisperModel

from environment import credentials, project_root
from postprocess import MarkdownLayoutEditor


class ModelPool:
    def __init__(self, model_count: int, model_name: str, device: str = "cpu"):
        self.model_count = model_count
        self.models = [WhisperModel(model_name, device=device, compute_type="float32") for _ in range(model_count)]
        self.queue = Queue(maxsize=model_count)

        # Добавляем модели в очередь
        for model in self.models:
            self.queue.put_nowait(model)

    async def get_model(self):
        # Забираем модель из очереди
        model = await self.queue.get()
        return model

    async def return_model(self, model: WhisperModel):
        # Возвращаем модель в пул
        await self.queue.put(model)

# Инициализация пула из 2 моделей
model_pool = ModelPool(
    model_count=1,
    model_name="tiny",
    device="cpu"
)
md_editor = MarkdownLayoutEditor()

sio = socketio.AsyncServer(
    async_mode="asgi",  # Указываем режим работы
    cors_allowed_origins="*"  # Настройка CORS
)


@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.event
async def recognition_start(sid):
    print("Starting recognition")


@sio.event
async def recognition(sid, data):
    recognition_task = asyncio.create_task(process_recognition(sid, data))
    print("Task created")
    await recognition_task


async def process_recognition(sid, data):
    print("Processing snippet")
    model = await model_pool.get_model()

    try:
        # Обработка аудио (синхронная операция, поэтому используем to_thread)
        segments, _ = await asyncio.to_thread(
            model.transcribe,
            io.BytesIO(data),
            language='ru'
        )

        # Отправка результата обратно
        for segment in segments:
            print(f"Recognized: {segment}")
            await sio.emit('recognition_result', segment.text, room=sid)
    finally:
        # Возвращаем модель обратно в пул
        await model_pool.return_model(model)
