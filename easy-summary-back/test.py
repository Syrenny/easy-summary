import asyncio
import websockets
import aiofiles
import ffmpeg
import os
import glob


async def send_audio_file(file_path, websocket_url, chunk_duration_sec=1):
    """
    Отправляет аудиофайл на сервер через WebSocket, нарезая его на фрагменты и перекодируя в ogg/opus.

    :param file_path: Путь к аудиофайлу (.webm).
    :param websocket_url: URL WebSocket сервера.
    :param chunk_duration_sec: Длительность каждого фрагмента в секундах.
    """
    chunk_template = "chunk_%03d.webm"  # Шаблон для фрагментов

    # Разбиваем аудио на части с перекодированием с использованием ffmpeg-python
    try:
        # Используем ffmpeg-python для нарезки и перекодировки
        (
            ffmpeg
            .input(file_path)  # Входной файл .webm
            .output(chunk_template, f='segment', segment_time=str(chunk_duration_sec), c='copy')
            .run(overwrite_output=True)  # Запускаем команду
        )

        # Подключаемся к WebSocket серверу и отправляем фрагменты
        async with websockets.connect(websocket_url) as websocket:
            i = 0
            while True:
                chunk_path = chunk_template % i
                if not os.path.exists(chunk_path):
                    break  # Все фрагменты отправлены

                async with aiofiles.open(chunk_path, mode='rb') as f:
                    audio_chunk = await f.read()
                    await websocket.send(audio_chunk)
                    print(f"Sent chunk {i}: {len(audio_chunk)} bytes")

                i += 1
                await asyncio.sleep(chunk_duration_sec)  # Имитация реального времени

            # Получаем ответ от сервера
            result = await websocket.recv()
            print(f"Received result: {result}")

    finally:
        # Удаляем временные файлы
        for file in glob.glob("chunk_*.webm"):
            os.remove(file)


async def main():
    file_path = 'data/Fonvizin.webm'  # Укажите путь к вашему .webm файлу
    websocket_url = 'ws://localhost:7256/easy-summary/recognize'  # Укажите URL вашего WebSocket сервера
    await send_audio_file(file_path, websocket_url)


# Запуск асинхронной программы
if __name__ == "__main__":
    asyncio.run(main())
