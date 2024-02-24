import argparse
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


async def register(host, port, nickname, user_file_path):
    writer = None
    account_hash = check_user_info(user_file_path)
    if account_hash:
        logger.info(f'Данные пользователя есть в файле - {user_file_path}')
        return account_hash
    try:
        reader, writer = await asyncio.open_connection(host, port)
        logger.debug(await reader.readline())

        writer.write('\n'.encode())
        await writer.drain()

        logger.debug(await reader.readline())
        writer.write(f'{nickname.strip()}\n'.encode())
        await writer.drain()

        chat_info = await reader.readline()
        json.loads(chat_info.decode())

        with open('user.json', mode='w', encoding='utf-8') as json_file:
            json.dump(json.loads(chat_info.decode()), json_file)

        logger.info(f'Пользователь создан, данные записаны в файл - {user_file_path}')

    except asyncio.exceptions.TimeoutError as error:
        logger.error(f'Тайм-аут при подключении к серверу: {error}', exc_info=True)
    except asyncio.exceptions.CancelledError:
        logger.error('Подключение было отменено', exc_info=True)
    except Exception as error:
        logger.error(f'Ошибка при регистрации: {error}', exc_info=True)

    finally:
        if writer is not None:
            writer.close()
            await writer.wait_closed()
    return account_hash


async def authorise(host, port, token):
    writer = None
    try:
        reader, writer = await asyncio.open_connection(host, port)
        logger.debug(await reader.readline())

        writer.write(f'{token}\n'.encode())
        await writer.drain()

        response = await reader.readline()
        if json.loads(response) is None:
            logger.info('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
            return False

        logger.info('Авторизация прошла успешно.')
        return True
    except asyncio.exceptions.TimeoutError as error:
        logger.error(f'Тайм-аут при подключении к серверу: {error}', exc_info=True)
    except asyncio.exceptions.CancelledError:
        logger.error('Подключение было отменено', exc_info=True)
    except Exception as error:
        logger.error(f'Ошибка при авторизации: {error}', exc_info=True)
    finally:
        if writer is not None:
            writer.close()
            await writer.wait_closed()
    return False


async def submit_message(host, port, message, token):
    writer = None
    if not token:
        logger.info('Необходимо выполнить авторизацию перед отправкой сообщения.')
        return
    try:
        reader, writer = await asyncio.open_connection(host, port)
        logger.debug(await reader.readline())
        writer.write(f'{token}\n'.encode())
        await writer.drain()

        check_token = await reader.readline()
        if json.loads(check_token) is None:
            logger.info('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
            logger.debug(await reader.readline())
        else:
            logger.debug(await reader.readline())
            writer.write(f'\n'.encode())
            await writer.drain()

            logger.debug(await reader.readline())

            writer.write(f'{message.strip()}\n\n'.encode())
            await writer.drain()
            logger.info('Сообщение отправлено.')
    except asyncio.exceptions.TimeoutError as error:
        logger.error(f'Тайм-аут при подключении к серверу: {error}', exc_info=True)
    except asyncio.exceptions.CancelledError:
        logger.error('Подключение было отменено', exc_info=True)
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения: {error}', exc_info=True)
    finally:
        if writer is not None:
            writer.close()
            await writer.wait_closed()


async def send_message_main(host, port, nickname, message, token, user_file_path):
    account_hash = token
    if account_hash is None:
        account_hash = await register(host, port, nickname, user_file_path)
    check_authorise = await authorise(host, port, account_hash)
    if check_authorise:
        await submit_message(host, port, message, account_hash)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Этот скрипт отправляет сообщения в чат.')
    parser.add_argument('--host', type=str, help='Укажите --host адрес хоста. По умолчанию '
                                                 'будет использоваться хост minechat.dvmn.org.',
                        nargs='?', default='minechat.dvmn.org')

    parser.add_argument('--port', type=int, help='Укажите --port порт хоста. '
                                                 'По умолчанию будет 5050 порт.', nargs='?', default=5050)

    parser.add_argument('--nickname', type=str, help='Укажите --nickname ваше имя пользователя в чате. '
                                                     'По умолчанию без аргумента будет использовать nicname Anonymous.',
                        nargs='?', default='Anonymous')

    parser.add_argument('--message', type=str, help='Укажите --message ваше сообщение.')

    parser.add_argument('--token', type=str, help='Укажите --token ваш токен для авторизации в чате.',
                        nargs='?', default=None)

    parser.add_argument('--user_file_path', type=str, help='Укажите --user_file_path путь к файлу для сохранения '
                                                           'учётный данных'
                                                           'пользователя в файл. По умолчанию без аргумента будет '
                                                           'использовать файл user.json в корне проекта.',
                        nargs='?', default='user.json')

    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger.setLevel(logging.INFO)

    if not args.message:
        parser.error('--message это обязательный аргумент cli')

    asyncio.run(send_message_main(args.host, args.port, args.nickname, args.message, args.token, args.user_file_path))
