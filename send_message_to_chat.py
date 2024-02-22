import asyncio
import json
import logging
import os


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
        logger.info(f'Данные пользователя есть в файле - {user_file_path}')
        return account_hash

    reader, writer = await asyncio.open_connection(host, port)
    logger.debug(await reader.read(buffer_size))

    writer.write('\n'.encode())
    await writer.drain()

    logger.debug(await reader.read(buffer_size))
    writer.write(f'{nickname.strip()}\n'.encode())
    await writer.drain()

    chat_info = await reader.readline()
    json.loads(chat_info.decode())

    with open('user.json', mode='w', encoding='utf-8') as json_file:
        json.dump(json.loads(chat_info.decode()), json_file)

    logger.info(f'Пользователь создан, данные записаны в файл - {user_file_path}')
    writer.close()
    await writer.wait_closed()
    return account_hash


async def authorise(host, port, token, buffer_size=1024):
    reader, writer = await asyncio.open_connection(host, port)
    logger.debug(await reader.read(buffer_size))

    writer.write(f'{token}\n'.encode())
    await writer.drain()

    response = await reader.readline()
    if json.loads(response) is None:
        logger.info('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
        return False

    writer.close()
    await writer.wait_closed()
    logger.info('Авторизация прошла успешно.')
    return True


async def submit_message(host, port, message, token, buffer_size=1024):
    if not token:
        logger.info('Необходимо выполнить авторизацию перед отправкой сообщения.')
        return

    reader, writer = await asyncio.open_connection(host, port)
    logger.debug(await reader.read(buffer_size))
    writer.write(f'{token}\n'.encode())
    await writer.drain()

    check_token = await reader.readline()
    if json.loads(check_token) is None:
        logger.info('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
        logger.debug(await reader.read(buffer_size))
    else:
        logger.debug(await reader.read(buffer_size))
        writer.write(f'\n'.encode())
        await writer.drain()

        logger.debug(await reader.read(buffer_size))

        writer.write(f'{message.strip()}\n\n'.encode())
        await writer.drain()
        logger.info('Сообщение отправлено.')
    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger.setLevel(logging.INFO)

    devman_chat_host = 'minechat.dvmn.org'
    devman_chat_port = 5050

    nickname = 'vaiz'
    chat_message = 'hello\nworld'
    user_file_path = 'user.json'

    account_hash = asyncio.run(register(devman_chat_host, devman_chat_port, nickname, user_file_path))
    check_authorise = asyncio.run(authorise(devman_chat_host, devman_chat_port, account_hash))
    if check_authorise:
        asyncio.run(submit_message(devman_chat_host, devman_chat_port, chat_message, account_hash))
