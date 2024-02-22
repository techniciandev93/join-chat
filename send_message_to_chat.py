import asyncio
import json
import logging

from environs import Env


logger = logging.getLogger('Logger send message to chat')


async def send_message(host, port, message, token, buffer_size=1024):
    reader, writer = await asyncio.open_connection(host, port)
    logger.info(await reader.read(buffer_size))
    writer.write(f'{token}\n'.encode())
    await writer.drain()

    check_token = await reader.readline()
    if json.loads(check_token) is None:
        logger.info('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
    else:
        logger.info(await reader.read(buffer_size))
        writer.write(f'\n'.encode())
        await writer.drain()

        logger.info(await reader.read(buffer_size))

        writer.write(f'{message}\n\n'.encode())
        await writer.drain()

    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    chat_token = env.str('CHAT_TOKEN')

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger.setLevel(logging.INFO)

    devman_chat_host = 'minechat.dvmn.org'
    devman_chat_port = 5050
    chat_message = 'hello world'
    asyncio.run(send_message(devman_chat_host, devman_chat_port, chat_message, chat_token))
