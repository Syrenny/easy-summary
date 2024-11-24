import queue
import asyncio
import itertools

import socketio

import grpc
import app.recognition.recognition_pb2 as recognition_pb2
import app.recognition.recognition_pb2_grpc as recognition_pb2_grpc

from app.environment import credentials, project_root
from app.postprocess import MarkdownLayoutEditor

ENCODINGS_MAP = {
    'pcm': recognition_pb2.RecognitionOptions.PCM_S16LE,
    'opus': recognition_pb2.RecognitionOptions.OPUS,
    'mp3': recognition_pb2.RecognitionOptions.MP3,
    'flac': recognition_pb2.RecognitionOptions.FLAC,
    'alaw': recognition_pb2.RecognitionOptions.ALAW,
    'mulaw': recognition_pb2.RecognitionOptions.MULAW,
}


class RecognitionManager:
    stub = None
    channel = None
    is_inited = False
    audio_queue = asyncio.Queue()
    recognition_options = recognition_pb2.RecognitionOptions(
        audio_encoding=ENCODINGS_MAP["opus"],
        # sample_rate=16000,
        model='general',
        hypotheses_count=1,
        enable_partial_results=False,
        enable_multi_utterance=True
    )

    def _connect(self):
        # Настройка канала gRPC
        ssl_cred = grpc.ssl_channel_credentials(
            root_certificates=open(project_root / "russian_trusted_root_ca_pem.crt", 'rb').read()
        )
        token_cred = grpc.access_token_call_credentials(credentials.salute_speech_access_token)

        self.channel = grpc.aio.secure_channel(
            "smartspeech.sber.ru",
            grpc.composite_channel_credentials(ssl_cred, token_cred),
        )
        self.stub = recognition_pb2_grpc.SmartSpeechStub(self.channel)
        self.is_inited = True
        print("Connected")

    async def _create_stream(self):
        print("Creating stream...")
        yield recognition_pb2.RecognitionRequest(
            options=self.recognition_options
        )
        print("Stream created")
        while True:
            audio_chunk = await self.audio_queue.get()
            if audio_chunk is None:  # Специальный сигнал для завершения потока
                print("There was None chunk, sending stopped")
                break
            # print("Sending audio chunk:", audio_chunk)
            yield recognition_pb2.RecognitionRequest(audio_chunk=audio_chunk)

    async def recognize(self):
        if not self.is_inited:
            self._connect()
        try:
            print("Processing...")
            # Отправляем аудиофрагменты в gRPC
            connection = self.stub.Recognize(self._create_stream())
            async for resp in connection:
                print("resp.results[0]", resp.results[0])
                yield resp.results[0].normalized_text
        except grpc.RpcError as err:
            print('RPC error: code = {}, details = {}'.format(err.code(), err.details()))
        except Exception as exc:
            print('Exception:', exc)

    def reset(self):
        if self.channel:
            self.channel.close()
        self.stub = None
        self.is_inited = False
        self.audio_queue = asyncio.Queue()


salute = RecognitionManager()
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
    salute.reset()


@sio.event
async def recognition_start(sid):
    print("Starting recognition")
    try:
        # Вызываем gRPC обработку
        recognition_task = asyncio.create_task(process_recognition(sid))
        await recognition_task
    except Exception as e:
        print(f"Error processing audio: {e}")
        await sio.emit('error', f"Произошла ошибка при обработке запроса.", room=sid)


async def process_recognition(sid):
    # Вызываем gRPC обработку
    async for result in salute.recognize():
        edited = md_editor(result)
        await sio.emit('recognition_result', edited, room=sid)  # Отправляем результат обратно клиенту


@sio.event
async def recognition_chunk(sid, data):
    # print("Chunk received:", data)
    await salute.audio_queue.put(data)
