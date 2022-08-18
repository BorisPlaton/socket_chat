from server.server import Chat


def main():
    server = Chat('localhost', 5555)
    server.start_listening()


if __name__ == '__main__':
    main()
