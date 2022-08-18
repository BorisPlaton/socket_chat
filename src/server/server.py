import socket
import selectors
from typing import Callable

from server.user import User


class Server:
    """
    Сервер, который принимает соединения и обрабатывает
    входящие сообщения.
    """

    def request_received(self, *args, **kwargs):
        """Обрабатывает запрос от клиента."""
        pass

    def new_connection(self, *args, **kwargs):
        """Обработчик, что вызывается при новом подключении."""
        pass

    def connection_closed(self, *args, **kwargs):
        """Обработчик, если соединение было разорвано."""
        pass

    def get_handler_args(self, client_socket: socket.socket) -> list:
        """
        Возвращает список позиционных аргументов, что будут
        переданы в метод `handle` при его вызове.
        """
        return []

    def get_handler_kwargs(self, client_socket: socket.socket) -> dict:
        """
        Возвращает список ключевых аргументов, что будут
        переданы в метод `handle` при его вызове.
        """
        return {}

    def accept_connection(self):
        """Принимает соединение от клиента."""
        client_socket, _ = self.server_socket.accept()
        self.register_for_reading(client_socket, lambda: self.invoke_handler(client_socket))
        self.call_handler(client_socket, self.new_connection)

    def invoke_handler(self, client_socket: socket.socket):
        """
        Устанавливает открыто ли соединение и в зависимости
        от этого вызывает соответсвующий обработчик.
        """
        if not client_socket.recv(4096, socket.MSG_PEEK):
            self.call_handler(client_socket, self.connection_closed)
            self.unregister_client(client_socket)
        else:
            self.call_handler(client_socket, self.request_received)

    def call_handler(self, client_socket: socket.socket, handler: Callable):
        """Вызывает обработчик."""
        args = self.get_handler_args(client_socket)
        kwargs = self.get_handler_kwargs(client_socket)
        handler(*args, **kwargs)

    def register_for_reading(self, client_socket: socket.socket, handler: Callable):
        """Регистрирует сокет на слежение."""
        self.selector.register(client_socket, selectors.EVENT_READ, handler)

    def unregister_client(self, client_socket: socket.socket):
        """Убирает сокет со слежения."""
        if client_socket is self.server_socket:
            raise ValueError("Нельзя перестать следить за серверным сокетом.")
        self.selector.unregister(client_socket)
        client_socket.close()

    def start_listening(self):
        """Начинает принимать запросы и обрабатывать их."""
        self.server_socket.listen()
        self.register_for_reading(self.server_socket, self.accept_connection)
        while True:
            for reg_socket, event in self.selector.select():
                reg_socket.data()

    def get_server_socket(self) -> socket.socket:
        """Возвращает сокет сервера."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        return sock

    def __init__(self):
        self.host = 'localhost'
        self.port = 5555
        self.server_socket = self.get_server_socket()
        self.selector = selectors.DefaultSelector()


class Chat(Server):
    """Чат-сервер, позволяющий общаться пользователям."""

    def request_received(self, user: User):
        """
        Обработчик. Принимает сообщение и отправляет его всем
        остальным.
        """
        request = self.get_user_request(user)
        message = self.format_message(user, request)
        self.send_to_users_except(user, message)

    def new_connection(self, user: User):
        """
        Обработчик. Уведомляет остальных пользователей о новом
        подключении.
        """
        message = self.format_message(user, "Has connected!")
        self.send_to_users_except(user, self.get_server_mark(message))
        self.send_to(user, self.get_users_in_chat_message([user]))

    def connection_closed(self, user: User):
        """
        Обработчик. Уведомляет других клиентов, что пользователь
        вышел из чата (соединение было разорвано).
        """
        message = self.format_message(user, "Has disconnected!")
        self.send_to_users_except(user, self.get_server_mark(message))
        self.registered_users.pop(user.client_socket)
        del user

    def get_handler_args(self, client_socket: socket.socket) -> list:
        """Возвращает список с объектом `User`."""
        if client_socket not in self.registered_users:
            self.registered_users[client_socket] = User(client_socket)
        return [self.registered_users[client_socket]]

    def send_to_users_except(self, user: User, message: str):
        """
        Отправляет всем пользователям сообщение за исключением
        `user`.
        """
        for user_socket in self.registered_users:
            if user_socket != user.client_socket:
                user_socket.send(self.format_message_before_send(message))

    def send_to(self, user: User, message: str):
        """Отправляет сообщение только одному пользователю `user`."""
        user.client_socket.send(self.format_message_before_send(message))

    def get_users_in_chat_message(self, to_exclude: list = None) -> str:
        users_list = self.users_in_chat
        if to_exclude:
            users_list = [user for user in users_list if user not in to_exclude]
        users_in_chat = users_list
        if users_in_chat:
            return ", ".join(map(str, users_in_chat)) + " are in the chat."
        else:
            return "None is here."

    @staticmethod
    def format_message_before_send(message: str) -> bytes:
        if message.endswith('\n'):
            return message.encode('utf-8')
        return (message + '\n').encode('utf-8')

    @property
    def users_in_chat(self) -> list[User]:
        return [user for user in self.registered_users.values()]

    @staticmethod
    def get_user_request(user: User) -> str:
        """
        Читает сообщение отправленное пользователем,
        и возвращает его в виде строки.
        """
        request = user.client_socket.recv(4096)
        return request.decode('utf-8')

    @staticmethod
    def format_message(user: User, message: str) -> str:
        """Форматирует сообщение для его отправки."""
        formatted_message = "[%s] %s" % (user.formatted_user_addr, message)
        return formatted_message

    @staticmethod
    def get_server_mark(message: str):
        return "=== Server ===\n" + message + "\n==============\n"

    def __init__(self):
        super().__init__()
        self.registered_users: dict[socket.socket, User] = {}
