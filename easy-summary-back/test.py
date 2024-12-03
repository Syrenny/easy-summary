from faster_whisper import WhisperModel
import os


def transcribe_audio(file_path: str, model_name: str = "base"):
    """
    Транскрибирует аудиофайл с использованием модели Whisper.

    :param file_path: Путь к аудиофайлу.
    :param model_name: Название модели (base, small, medium, large).
    :return: Текст транскрипции.
    """
    # Загрузка модели
    print(f"Загрузка модели: {model_name}")
    model = WhisperModel(model_name, device='cpu', compute_type="float32")
    # Проверка файла
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Аудиофайл {file_path} не найден!")

    result = ""
    # Транскрибирование
    print(f"Начало обработки файла: {file_path}")
    segments, _ = model.transcribe(file_path)
    for segment in segments:
        result += segment.text + " "
    # Вывод результата
    print("Транскрипция завершена!")
    return result


if __name__ == "__main__":
    # Пример использования
    audio_file = "data/Fonvizin.webm"
    model_size = "tiny"

    try:
        # Транскрибирование
        transcription = transcribe_audio(audio_file, model_size)
        print("\nРаспознанный текст:\n")
        print(transcription)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
