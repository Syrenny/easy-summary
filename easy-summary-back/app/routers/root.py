import asyncio
import io
from asyncio import Queue

import numpy as np
import socketio

from faster_whisper import WhisperModel

from environment import credentials, project_root
from postprocess import MarkdownLayoutEditor

# Инициализация пула из 2 моделей
model = WhisperModel(
    credentials.faster_whisper_model,
    device=credentials.faster_whisper_device,
    compute_type=credentials.faster_whisper_compute_type,
)
md_editor = MarkdownLayoutEditor()
audio_buffer = io.BytesIO()

sio = socketio.AsyncServer(
    async_mode="asgi",  # Указываем режим работы
    cors_allowed_origins="*",  # Настройка CORS
    ping_interval=25,
    ping_timeout=120
)


@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.event
async def receive_start(sid):
    audio_buffer.seek(0)
    audio_buffer.truncate(0)
    print("Starting recognition")


@sio.event
async def audio_chunk(sid, data: bytes):
    print("Audio chunk received")
    audio_buffer.write(data)


@sio.event
async def receive_end(sid):
    print("Recognition started")
    recognition_task = asyncio.create_task(process_recognition(sid))
    await recognition_task


# Функция для отправки текста по чанкам
async def split_text(text):
    CHUNK_SIZE = 1000
    start = 0
    while start < len(text):
        # Разбиваем текст на чанки
        chunk = text[start:start + CHUNK_SIZE]
        yield chunk
        start += CHUNK_SIZE


async def process_recognition(sid):
    audio_buffer.seek(0)
    result = ""
    try:
        loop = asyncio.get_event_loop()
        # Выполняем тяжелые операции в пуле потоков
        segments, _ = await loop.run_in_executor(
            None,
            model.transcribe,
            audio_buffer,
            'ru'
        )
        for segment in segments:
            result += segment.text
        print("Structuring started")
        result = await loop.run_in_executor(None, md_editor, result)
        async for chunk in split_text(result):
            print("Returning result of recognition")
            await sio.emit('recognition_result', chunk, room=sid)
    finally:
        await sio.disconnect(sid)
