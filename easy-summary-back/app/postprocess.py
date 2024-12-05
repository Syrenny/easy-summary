from openai import OpenAI
from environment import credentials
import re


# Промпт для формирования Markdown
prompt_template = """
Ты — эксперт по обработке текста, специализирующийся на форматировании и улучшении читаемости материалов. Твоя задача:  
1. Преобразовать предоставленный текст в структурированный формат Markdown, добавляя заголовки, списки, выделения (**жирный**, *курсив*), цитаты, таблицы и другие элементы разметки, если это улучшает восприятие информации.  
2. Делить текст на логические части с соответствующими заголовками и подзаголовками. Если текст длинный, структурируй его, избегая больших монолитных блоков.  
3. Если в тексте есть опечатки, оставляй их в оригинальном виде, но рядом в скобках указывай предполагаемый правильный вариант (например, "алгортим (алгоритм)").  
4. Если текст предполагает технический или научный контекст, используй соответствующую структуру, включая разделы, такие как "Введение", "Методы", "Результаты", "Заключение".  
5. При создании списков выбирай формат (нумерованный или маркированный), который наиболее подходит к контексту.  
6. Старайся писать лаконично, чтобы текст был понятен, но не терял важной информации.  

Вот текст для обработки:  
"{raw_text}"  

"""

def extract_markdown_content(response):
    # Регулярное выражение для поиска содержимого внутри ```markdown
    pattern = r"```(?:markdown)?\n([\s\S]*?)```"
    match = re.search(pattern, response)
    return match.group(1).strip() if match else response


class MarkdownLayoutEditor:
    params = {
        "model": "mistralai/mistral-7b-instruct:free",
        "temperature": 0.1,
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
        return extract_markdown_content(self._generate_markdown(text))
