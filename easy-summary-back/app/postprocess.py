from openai import OpenAI
from environment import credentials


# Промпт для формирования Markdown
prompt_template = """
Ты — эксперт в структурировании текста в формате Markdown. Преобразуй следующий текст в Markdown, используя 
заголовки, списки, выделение жирным шрифтом и курсивом, если это необходимо:

Текст:
{raw_text}

Ответ должен быть чистым, хорошо форматированным Markdown текстом, сохрани содержание текста. Исправь опечатки, если они присутствуют в тексте. Нормализуй предложения в тексте по смыслу
"""


class MarkdownLayoutEditor:
    params = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "temperature": 0.4,
    }
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=credentials.open_router_key,
    )

    def _create_message(self, text):
        """
        Создание сообщения для передачи в модель с добавлением текста.

        :return: словарь с ролью и текстом сообщения
        """
        prompt = prompt_template.format(
            raw_text=text,
        )
        return {
            "role": "user",  # Роль пользователя
            "content": prompt
        }

    def _generate_markdown(self, text: str) -> str:
        """
        Отправка запроса в модель для преобразования текста в Markdown.

        :param text: текст для преобразования
        :return: ответ модели, преобразованный в Markdown
        """
        if not text:
            return ""

        completion = self.client.chat.completions.create(
            messages=[self._create_message(text)],
            **self.params
        )
        # Извлечение ответа модели
        self.history = completion.choices[0].message.content
        # Добавляем полученный ответ в историю для дальнейшего контекста
        print("Edited:", self.history)
        return self.history

    def __call__(self, text: str) -> str:
        """
        Метод, который позволяет использовать экземпляр класса как функцию.

        :param text: текстовый корпус для преобразования в Markdown
        :return: текст, преобразованный в Markdown
        """
        return self._generate_markdown(text)
