from server.server import Server


def main():
    server = Server()
    server.start_listening()


if __name__ == '__main__':
    main()
