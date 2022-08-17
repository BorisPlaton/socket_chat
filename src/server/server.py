import socket
import selectors
from typing import Callable


class Server:
    """
    Сервер, который принимает соединения и обрабатывает
    входящие сообщения.
    """

    def handle(self, client_socket: socket.socket, *args, **kwargs):
        """Обрабатывает запрос от клиента."""
        pass

    def get_handler_args(self, client_socket: socket.socket) -> list:
        """
        Возвращает список позиционных аргументов, что будут
        переданы в метод `handle` при его вызове.
        """
        return [client_socket]

    def get_handler_kwargs(self, client_socket: socket.socket) -> dict:
        """
        Возвращает список ключевых аргументов, что будут переданы
        в метод `handle` при его вызове.
        """
        return {}

    def accept_connection(self, server_socket: socket.socket):
        """Принимает соединение от клиента."""
        conn, addr = server_socket.accept()
        self.register_for_reading(conn, self._invoke_handler)

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
                reg_socket.data(reg_socket.fileobj)

    def get_server_socket(self) -> socket.socket:
        """Возвращает сокет сервера."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        return sock

    def _invoke_handler(self, client_socket: socket.socket):
        """Вызывает обработчик, передавая ему необходимые данные."""
        args = self.get_handler_args(client_socket)
        kwargs = self.get_handler_kwargs(client_socket)
        return self.handle(*args, **kwargs)

    def __init__(self):
        self.host = 'localhost'
        self.port = 5555
        self.server_socket = self.get_server_socket()
        self.selector = selectors.DefaultSelector()


class Chat(Server):
    """Чат-сервер, позволяющий общаться пользователям."""

    def handle(self, client_socket: socket.socket, *args, **kwargs):
        mes = client_socket.recv(1024)
        client_socket.send(mes)
