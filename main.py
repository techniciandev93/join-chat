import asyncio
from datetime import datetime

import aiofiles


async def save_message(history_file, message):
    timestamp = datetime.now().strftime("[%d.%m.%y %H:%M]")
    formatted_message = f"{timestamp} {message.decode()}"
    print(formatted_message)
    await history_file.write(formatted_message)


async def connect_to_chat(chat_host, chat_port, history_file_path):
    async with aiofiles.open(history_file_path, mode='a') as history_file:
        try:
            reader, writer = await asyncio.open_connection(chat_host, chat_port)
            while not reader.at_eof():
                try:
                    message = await reader.read(2048)
                    await save_message(history_file, message)
                    await history_file.flush()
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
    chat_history_file_path = 'chat_history.txt'
    devman_chat_host = 'minechat.dvmn.org'
    devman_chat_port = 5000
    asyncio.run(connect_to_chat(devman_chat_host, devman_chat_port, chat_history_file_path))
