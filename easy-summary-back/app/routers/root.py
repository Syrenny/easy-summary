import asyncio
import io
from asyncio import Queue

import numpy as np
import socketio
from pydub import AudioSegment

from faster_whisper import WhisperModel

from environment import credentials, project_root
from postprocess import MarkdownLayoutEditor


# Инициализация пула из 2 моделей
model = WhisperModel('small', device='cpu', compute_type="int8")
md_editor = MarkdownLayoutEditor()
audio_buffer = io.BytesIO()

sio = socketio.AsyncServer(
    async_mode="asgi",  # Указываем режим работы
    cors_allowed_origins="*",  # Настройка CORS
    ping_interval=25,
    ping_timeout=60
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
        segments, _ = model.transcribe(
            audio_buffer,
            language='ru'
        )
        result = ""
        # Отправка результата обратно
        # for segment in segments:
        #     print(f"Recognized: {segment}")
        #     await sio.emit('recognition_result', segment.text, room=sid)
        for segment in segments:
            result += segment.text
        print("Structuring started")
        result = md_editor(result)
        async for chunk in split_text(result):
            print("Returning result of recognition")
            await sio.emit('recognition_result', chunk, room=sid)
