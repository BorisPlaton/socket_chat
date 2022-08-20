import asyncio
from asyncio import Task


class Client:
    """Класс для взаимодействия с сервером."""

    async def accept_server_response(self):
        """Принимает сообщение от сервера."""
        while True:
            response = await self.get_server_response()
            if response:
                self.output_message(response)
            else:
                await self.close_server_connection()
                self.output_message("The server has closed the connection.")
                self.stop_all_tasks()
                raise ValueError

    async def send_to_server(self):
        """Отправляет сообщение на сервер."""
        while True:
            user_input = await self.get_user_input()
            await self.send_message_to_server(user_input)

    async def close_server_connection(self):
        """Закрывает соединение с сервером."""
        self.writer.close()
        await self.writer.wait_closed()

    async def get_server_response(self) -> str:
        """Возвращает ответ сервера в виде строки."""
        response = await self.reader.read(1024)
        return response.decode()

    async def send_message_to_server(self, message: str):
        """Форматирует сообщение и отправляет его на сервер."""
        formatted_message = self.format_message(message)
        self.writer.write(formatted_message)
        await self.writer.drain()

    @staticmethod
    def format_message(message: str) -> bytes:
        """Форматирует сообщение и возвращает его в байтах."""
        if not message.endswith('\n'):
            message += '\n'
        return message.encode()

    async def connect_to_server(self):
        """
        Подключается к серверу и возвращает объекты для
        взаимодействия с ним.
        """
        self.reader, self.writer = await asyncio.open_connection(self.server_host, self.server_port)

    async def start_chat(self):
        """
        Подключается к серверу и отправляет сообщения
        введенные пользователем.
        """
        await self.connect_to_server()
        self.task_list = self.get_tasks()
        try:
            await asyncio.gather(*self.task_list)
        except ValueError:
            self.stop_all_tasks()

    def get_tasks(self) -> [Task, Task]:
        """Возвращает все задачи на выполнение."""
        server_request = asyncio.create_task(self.send_to_server())
        server_response = asyncio.create_task(self.accept_server_response())
        return [server_request, server_response]

    def stop_all_tasks(self):
        """Останавливает все задачи."""
        for task in self.task_list:
            task.cancel()

    @staticmethod
    def output_message(message: str):
        """Выводит сообщение в консоль."""
        print(message)

    @staticmethod
    async def get_user_input() -> str:
        """Возвращает ввод пользователя."""
        loop = asyncio.get_running_loop()
        message = await loop.run_in_executor(None, input)
        return message

    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.task_list: list[Task] = []
        self.writer: asyncio.StreamWriter | None = None
        self.reader: asyncio.StreamReader | None = None
