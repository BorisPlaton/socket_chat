import socket
import selectors

from server.user import ChatUsers, User


class Server:
    """
    Сервер, который принимает соединения и обрабатывает
    входящие сообщения.
    """

    def handle(self, client_socket: socket.socket):
        """Обработчик запроса, который отправил пользователь."""
        pass

    def accept_connection(self, server_socket: socket.socket):
        """Принимает соединение."""
        conn, addr = self.server_socket.accept()
        self.register_client(conn)

    @staticmethod
    def notify_client(client_socket: socket.socket, message):
        """Отправляет сообщение клиенту."""
        client_socket.send(bytes(str(message), 'utf-8'))

    def register_client(self, client_socket: socket.socket):
        """Регистрирует сокет на слежение."""
        self.selector.register(client_socket, selectors.EVENT_READ, self.handle)

    def unregister_client(self, client_socket: socket.socket):
        """Убирает сокет со слежения."""
        if client_socket is self.server_socket:
            raise ValueError("Нельзя перестать следить за серверным сокетом.")
        self.selector.unregister(client_socket)
        client_socket.close()

    def start_listening(self):
        """Начинает принимать запросы и обрабатывать их."""
        self.server_socket.listen()
        self.selector.register(self.server_socket, selectors.EVENT_READ, self.accept_connection)
        while True:
            for reg_socket, event in self.selector.select():
                reg_socket.data(reg_socket.fileobj)

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
