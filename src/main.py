from server.server import Chat


def main():
    server = Chat()
    server.start_listening()


if __name__ == '__main__':
    main()
