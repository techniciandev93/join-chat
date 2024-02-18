import asyncio


async def connect_to_chat(chat_host, chat_port):
    reader, writer = await asyncio.open_connection(chat_host, chat_port)
    try:
        while not reader.at_eof():
            try:
                message = await reader.read(2048)
                print(f'Received: {message.decode()}')
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
    devman_chat_host = 'minechat.dvmn.org'
    devman_chat_port = 5000
    asyncio.run(connect_to_chat(devman_chat_host, devman_chat_port))
