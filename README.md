# Подключаемся к чату

Этот скрипт предназначен для подключения и отправки сообщений в чат, а также для сохранения переписки в файл.

## Как установить

Python 3.10 должен быть уже установлен.
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

## Как запустить
### listen-minechat.py
Для подключения к чату запустите скрипт listen-minechat.py с аргументами
```
Укажите python listen-minechat.py --host адрес хоста. 
По умолчанию будет использоваться хост minechat.dvmn.org.

Укажите python listen-minechat.py --port порт хоста. По умолчанию будет 5000 порт.

Укажите python listen-minechat.py --history путь к файлу для сохранения истории переписки.
По умолчанию будет использоваться chat_history.txt файл будет в корне проекта.
```

### send_message_to_chat.py
Для отправки сообщений в чат запустите скрипт python send_message_to_chat.py с аргументами
```
Укажите python send_message_to_chat.py --host адрес хоста. 
По умолчанию будет использоваться хост minechat.dvmn.org.

Укажите python send_message_to_chat.py --port порт хоста. 
По умолчанию будет 5050 порт.

Укажите python send_message_to_chat.py --nickname ваше имя пользователя в чате. 
По умолчанию без аргумента будет использовать nicname Anonymous.

Укажите python send_message_to_chat.py --message ваше сообщение.
Укажите python send_message_to_chat.py --token ваш токен для авторизации в чате.

Укажите python send_message_to_chat.py --user_file_path путь к файлу для сохранения учётный данных пользователя в файл. 
По умолчанию без аргумента будет использовать файл user.json в корне проекта.
```