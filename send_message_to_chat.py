import asyncio
import json
import logging
import os

from environs import Env


logger = logging.getLogger('Logger send message to chat')


def check_user_info(file_path):
    if not os.path.exists(file_path):
        return False
    with open(file_path, 'r', encoding='utf-8') as file:
        user_info = json.load(file)

    if 'nickname' not in user_info and 'account_hash' not in user_info:
        return False
    if not user_info['nickname'] and not user_info['account_hash']:
        return False
    return user_info['account_hash']


async def register(host, port, nickname, user_file_path, buffer_size=1024):
    account_hash = check_user_info(user_file_path)
    if account_hash:
        logger.info('Данные пользователя есть в файле')
        return account_hash

    reader, writer = await asyncio.open_connection(host, port)
    logger.info(await reader.read(buffer_size))

    writer.write('\n'.encode())
    await writer.drain()

    logger.info(await reader.read(buffer_size))
    writer.write(f'{nickname}\n'.encode())
    await writer.drain()

    chat_info = await reader.readline()
    json.loads(chat_info.decode())

    with open('user.json', mode='w', encoding='utf-8') as json_file:
        json.dump(json.loads(chat_info.decode()), json_file)

    logger.info(f'Пользователь создан, данные записаны в файл - {user_file_path}')
    writer.close()
    await writer.wait_closed()
    return account_hash


async def send_message(host, port, message, token, buffer_size=1024):
    reader, writer = await asyncio.open_connection(host, port)
    logger.info(await reader.read(buffer_size))
    writer.write(f'{token}\n'.encode())
    await writer.drain()

    check_token = await reader.readline()
    if json.loads(check_token) is None:
        logger.info('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
        logger.info(await reader.read(buffer_size))
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

    nickname = 'vaiz'
    chat_message = 'hello world'
    user_file_path = 'user.json'

    account_hash = asyncio.run(register(devman_chat_host, devman_chat_port, nickname, user_file_path))
    asyncio.run(send_message(devman_chat_host, devman_chat_port, chat_message, account_hash))
