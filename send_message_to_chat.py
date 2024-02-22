import asyncio

from environs import Env


async def send_message(host, port, message, token, buffer_size=1024):
    reader, writer = await asyncio.open_connection(host, port)
    print(await reader.read(buffer_size))
    writer.write(f'{token}\n'.encode())
    await writer.drain()

    print(await reader.read(buffer_size))
    writer.write(f'\n'.encode())
    await writer.drain()

    print(await reader.read(buffer_size))

    writer.write(f'{message}\n\n'.encode())
    await writer.drain()

    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
    env = Env()
    env.read_env()

    token = env.str('CHAT_TOKEN')

    devman_chat_host = 'minechat.dvmn.org'
    devman_chat_port = 5050
    chat_message = 'hello world'
    asyncio.run(send_message(devman_chat_host, devman_chat_port, chat_message, token))
