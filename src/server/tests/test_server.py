import pytest

from server.handlers import Server


@pytest.mark.parametrize(
    'host, port',
    [
        ('localhost', 5151),
        ('127.0.0.1', 5152),
        ('0.0.0.0', 10001),
        ('255.255.255.255', 12345),
    ]
)
def test_server_host_and_port(host, port):
    server = Server(host, port)
    assert server.server_socket.getsockname()[0] == host if host != 'localhost' else '127.0.0.1'
    assert server.server_socket.getsockname()[1] == port


def test_socket_registration_for_reading(server, client_socket):
    func = lambda: 'test'
    server.register_for_reading(client_socket, func)
    for fileobj, _, _, data in server.selector.get_map().values():
        assert fileobj is client_socket
        assert data is func


def test_socket_unregister_from_reading(server, client_socket):
    func = lambda: 'test'
    server.register_for_reading(client_socket, func)
    with pytest.raises(ValueError):
        server.unregister_from_reading(server.server_socket)
    server.unregister_from_reading(client_socket)
    assert not server.selector.get_map().values()


def test_socket_close_connection(server, client_socket):
    func = lambda: 'test'
    server.register_for_reading(client_socket, func)
    server.close_socket(client_socket)
    assert client_socket.fileno() == -1


def test_handler_kwargs_and_args_type(server, client_socket):
    args, kwargs = server.get_handler_args(client_socket), server.get_handler_kwargs(client_socket)
    assert isinstance(args, list)
    assert isinstance(kwargs, dict)


def test_handler_calling(server, client_socket):
    a = False

    def change_a(*args, **kwargs):
        nonlocal a
        a = True

    server.call_handler(client_socket, change_a)
    assert client_socket.fileno() != -1
    assert a


def test_handler_invoking(server, client_socket):
    connected = None

    def request_received(*args, **kwargs):
        nonlocal connected
        connected = True

    def connection_closed(*args, **kwargs):
        nonlocal connected
        connected = False

    def new_connection(*args, **kwargs):
        nonlocal connected
        connected = 'is connected'

    server.request_received = request_received
    server.connection_closed = connection_closed
    server.new_connection = new_connection

    with server.server_socket as server_socket:
        server_socket.listen()

        client_socket.connect(server_socket.getsockname())
        client_socket_created_by_server = server.accept_connection()
        assert connected == 'is connected'

        client_socket.send('data'.encode('utf-8'))
        server.invoke_handler(client_socket_created_by_server)
        assert connected is True
        client_socket_created_by_server.recv(24)

        client_socket.close()
        server.invoke_handler(client_socket_created_by_server)
        assert connected is False
        assert client_socket_created_by_server.fileno() == -1
        assert not server.selector.get_map().values()
