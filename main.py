import argparse
import asyncio
from datetime import datetime

import aiofiles


async def save_message(history_file, message, buffer_size=1024):
    timestamp = datetime.now().strftime("[%d.%m.%y %H:%M]")
    formatted_message = f"{timestamp} {message.decode()}"
    print(formatted_message)
    await history_file.write(formatted_message)
    history_file_tell = await history_file.tell()
    if history_file_tell >= buffer_size:
        await history_file.flush()


async def connect_to_chat(chat_host, chat_port, history_file_path, buffer_size=1024):
    async with aiofiles.open(history_file_path, mode='w') as history_file:
        try:
            reader, writer = await asyncio.open_connection(chat_host, chat_port)
            while not reader.at_eof():
                try:
                    message = await reader.read(buffer_size)
                    await save_message(history_file, message)
                except asyncio.IncompleteReadError:
                    print('Connection closed unexpectedly.')
                    break
                except asyncio.CancelledError:
                    print('Connection cancelled.')
                    break

        except BaseException as error:
            print(f'BaseException occurred. Exiting. {error}')
            raise

        finally:
            print('Close the connection')
            writer.close()
            await writer.wait_closed()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Этот скрипт подключается к чату и сохраняет переписку в файл.')
    parser.add_argument('--host', type=str, help='Укажите --host адрес хоста. По умолчанию '
                                                 'будет использоваться хост minechat.dvmn.org.',
                        nargs='?', default='minechat.dvmn.org')

    parser.add_argument('--port', type=int, help='Укажите --port порт хоста. '
                                                 'По умолчанию будет 5000 порт.', nargs='?', default=5000)

    parser.add_argument('--history', type=str, help='Укажите --history путь к файлу для сохранения истории '
                                                    'переписки. По умолчанию'
                                                    'будет использоваться chat_history.txt файл будет в корне '
                                                    'проекта.',
                        nargs='?', default='chat_history.txt')

    args = parser.parse_args()

    chat_history_file_path = 'chat_history.txt'
    devman_chat_host = 'minechat.dvmn.org'
    devman_chat_port = 5000
    asyncio.run(connect_to_chat(args.host, args.port, args.history))
