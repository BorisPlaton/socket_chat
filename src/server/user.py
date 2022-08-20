import socket

from faker import Faker


class Names:
    """Класс, что выдает случайные имена."""

    def get_name(self) -> str:
        """
        Возвращает случайное имя, которое ещё
        не использовалось.
        """
        while True:
            name = self.faker.first_name()
            if name not in self._registered_names:
                self._registered_names.add(name)
                break
        return name

    def delete_name(self, name) -> bool:
        """
        Удаляет имя из множества уже использованных
        имён. Если имя там было, вернет `True`, иначе -
        False.
        """
        try:
            self._registered_names.remove(name)
        except KeyError:
            return False
        return True

    def __init__(self):
        self.faker = Faker()
        self._registered_names = set()


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
        вида `HOST:PORT | name`.
        """
        return ':'.join(map(str, self.user_address)) + f' | {self.username}'

    def __del__(self):
        """
        При удалении пользователя удаляет его имя из
        генератора имен.
        """
        self.names_generator.delete_name(self.username)

    def __repr__(self):
        return self.username

    def __init__(self, client_socket: socket.socket):
        self.username = self.names_generator.get_name()
        self.client_socket = client_socket


class UserChatList(set):
    """Коллекция списка пользователей."""

    def remove(self, user: User = None, user_socket: socket.socket = None) -> bool:
        """
        Удаляет пользователя. Если он был, возвращает `True`,
        иначе `False`.
        """
        if user:
            try:
                super().remove(user)
            except KeyError:
                return False
        elif user_socket:
            for user in self:
                if user.client_socket == user_socket:
                    super().remove(user)
                    break
            else:
                return False
        else:
            raise ValueError("Предоставьте пользователя или его сокет.")
        return True

    @property
    def users_sockets(self) -> list[socket.socket]:
        """Возвращает список сокетов пользователей."""
        return [user.client_socket for user in self]

    def get_user(self, user_socket: socket.socket) -> User:
        """Возвращает пользователя, который имеет сокет `user_socket`."""
        for user in self:
            return user if user.client_socket == user_socket else None
