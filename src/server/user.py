import socket

from names.name import Names


class User:
    """Абстракция, что предоставляет пользователя."""

    names_generator = Names()

    @property
    def user_address(self) -> tuple[str, int]:
        """Возвращает данные об адресе пользователя."""
        return self.client_socket.getpeername()

    @property
    def formatted_user_addr(self) -> str:
        """
        Возвращает строку удаленного адреса пользователя
        вида `HOST:PORT`.
        """
        return ':'.join(map(str, self.user_address))

    def __del__(self):
        """
        При удалении пользователя удаляет его имя из
        генератора имен.
        """
        self.names_generator.delete_name(self.username)

    def __init__(self, client_socket: socket.socket):
        self.username = self.names_generator.get_name()
        self.client_socket = client_socket


class ChatUsers:
    """Коллекция списка пользователей."""

    def add_user(self, user: User):
        """Добавляет пользователя."""
        self.users.add(user)

    def remove_user(self, user: User = None, user_socket: socket.socket = None) -> bool:
        """
        Удаляет пользователя. Если он был, возвращает `True`,
        иначе `False`.
        """
        if user:
            try:
                self.users.remove(user)
            except KeyError:
                return False
        elif user_socket:
            for user in self.users:
                if user.client_socket == user_socket:
                    self.users.remove(user)
                    break
            else:
                return False
        else:
            raise ValueError("Предоставьте пользователя или его сокет.")
        return True

    @property
    def users_sockets(self) -> list[socket.socket]:
        """Возвращает список сокетов пользователей."""
        return [user.client_socket for user in self.users]

    def get_user(self, user_socket: socket.socket) -> User:
        """Возвращает пользователя, который имеет сокет `user_socket`."""
        for user in self.users:
            return user if user.client_socket == user_socket else None

    def __iter__(self):
        return self.users

    def __init__(self):
        self.users = set()
