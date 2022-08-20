import asyncio
from handler import Client


async def main():
    """Подключается к серверу."""
    client_ = Client('localhost', 5555)
    await client_.start_chat()


if __name__ == '__main__':
    asyncio.run(main())
