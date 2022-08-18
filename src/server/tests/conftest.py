import socket

import pytest

from server.server import Server, Chat


@pytest.fixture
def server():
    return Server('localhost', 5151)


@pytest.fixture
def chat_server():
    return Chat('localhost', 5151)


@pytest.fixture
def client_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
