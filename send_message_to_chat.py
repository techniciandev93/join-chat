import asyncio


async def send_message(host, port, message, token, nic_name, buffer_size=1024):
    reader, writer = await asyncio.open_connection(host, port)
    print(await reader.read(buffer_size))
    writer.write(f'{token}\n'.encode())
    await writer.drain()

    print(await reader.read(buffer_size))
    writer.write(nic_name.encode() + b'\n')
    await writer.drain()

    print(await reader.read(buffer_size))
    writer.write(b'\n')
    await writer.drain()

    print(await reader.read(buffer_size))

    writer.write(message.encode() + b'\n\n')
    await writer.drain()

    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
    devman_chat_host = 'minechat.dvmn.org'
    devman_chat_port = 5050
    chat_message = 'hello world'
    name = 'Anon'
    token = ''
    asyncio.run(send_message(devman_chat_host, devman_chat_port, chat_message, token, name))
