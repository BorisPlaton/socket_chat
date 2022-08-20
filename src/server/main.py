from server.handlers import Chat


def main():
    """Запускает сервер."""
    server = Chat('localhost', 5555)
    server.start_listening()


if __name__ == '__main__':
    main()
