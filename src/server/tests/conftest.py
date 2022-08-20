import socket

import pytest

from server.handlers import Server, Chat
from server.user import Names


@pytest.fixture
def server():
    return Server('localhost', 5151)


@pytest.fixture
def chat_server():
    return Chat('localhost', 5151)


@pytest.fixture
def client_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


@pytest.fixture
def name_class():
    return Names()
