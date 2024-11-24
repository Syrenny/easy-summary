import io

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import ffmpeg

import grpc
import app.recognition.recognition_pb2 as recognition_pb2
import app.recognition.recognition_pb2_grpc as recognition_pb2_grpc

from app.environment import credentials, project_root

ENCODINGS_MAP = {
    'pcm': recognition_pb2.RecognitionOptions.PCM_S16LE,
    'opus': recognition_pb2.RecognitionOptions.OPUS,
    'mp3': recognition_pb2.RecognitionOptions.MP3,
    'flac': recognition_pb2.RecognitionOptions.FLAC,
    'alaw': recognition_pb2.RecognitionOptions.ALAW,
    'mulaw': recognition_pb2.RecognitionOptions.MULAW,
}


def convert_to_ogg_opus(audio_bytes: bytes):
    input_stream = io.BytesIO(audio_bytes)
    process = (
        ffmpeg
        .input('pipe:0')  # Входной файл .webm
        .output('pipe:1', acodec='libopus', format='ogg')
        .global_args('-loglevel', 'quiet')
        .run_async(pipe_stdin=True, pipe_stdout=True)  # Запускаем команду
    )
    output_data, _ = process.communicate(input=input_stream.read())  # Получаем результат из stdout

    # Возвращаем результат в виде байтов
    return output_data


def recognize(audio_chunk: bytes):
    recognition_options = recognition_pb2.RecognitionOptions(
        audio_encoding=ENCODINGS_MAP["opus"],
        # sample_rate=16000,
        model='general',
        hypotheses_count=1,
        enable_partial_results=True,
        enable_multi_utterance=True,
    )

    # Настройка канала gRPC
    ssl_cred = grpc.ssl_channel_credentials(
        root_certificates=open(project_root / "russian_trusted_root_ca_pem.crt", 'rb').read()
    )
    token_cred = grpc.access_token_call_credentials(credentials.salute_speech_access_token)

    channel = grpc.secure_channel(
        "smartspeech.sber.ru",
        grpc.composite_channel_credentials(ssl_cred, token_cred),
    )
    stub = recognition_pb2_grpc.SmartSpeechStub(channel)

    def helper():
        yield recognition_pb2.RecognitionRequest(
            options=recognition_options
        )
        yield recognition_pb2.RecognitionRequest(
        audio_chunk=audio_chunk
    )

    # Отправляем аудиофрагменты в gRPC
    connection = stub.Recognize(helper())
    try:
        for resp in connection:
            print("resp.results[0]", resp.results[0])
            return resp.results[0].normalized_text
    except grpc.RpcError as err:
        print('RPC error: code = {}, details = {}'.format(err.code(), err.details()))
    except Exception as exc:
        print('Exception:', exc)


def reset_connection(self):
    self.channel.close()
    self.stub = None
    self.is_inited = False


router = APIRouter()


@router.websocket("/recognize")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # Получаем аудиофрагменты от клиента
            audio_chunk = await websocket.receive_bytes()
            print("Received bytes:", audio_chunk)
            # audio_chunk = convert_to_ogg_opus(audio_chunk)
            # Отправляем полученные байты в функцию для распознавания
            # result = recognize_audio_bytes(audio_chunk)
            result = recognize(audio_chunk)
            print("Result:", result)
            # Отправляем результат клиенту
            await websocket.send_text(result)

    except WebSocketDisconnect:
        print("Client disconnected")
        await websocket.close()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        await websocket.send_text("Произошла ошибка при обработке запроса.")
