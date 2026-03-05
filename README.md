# MIREA Gamedev News Bot
## How to run

### Requirements
Python == 3.12.*

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
```cmd
python scripts\init_values.py
```
(Command can be called without requirements installed)

Command will create files in project root:

`config.txt`
```
bot_token = <tg bot token>
bot_name = <botname - like @mycoolbot>
webhook_token = <webhook secret - random string>
url = <host url>
quest_room = <id of tg supergroup>
```

`config_vk.txt`
```
confirmation_code = <callback confirmation code>
callback_secret = <secret key - random string>
```


#### Настройка VK Callback
1) Откройте управление сообществом
2) Перейдите во вкладку "Дополнительно", далее "Работа с API"
3) Откройте вкладку "Callback API" и добавте сервер
    * Версия API: 5.199
    * Адрес: <хост>/api/vk_callback
    * Отображаемый код подтверждения необходимо ввести при запуске скрипта `init_values.py` или в файл `config_vk.txt` первой строкой
    * Секретный ключ: строка выведенная скриптом `init_values.py` (сохранена в файле `config_vk.txt` второй строкой)
    * Нажмите "Сохранить"
    * Перед нажатием "Подтвердить" включите сервер
4) Настройте "Типы событий", активируйте пункт:
    * Записи на стене: Добавление


### Run

```cmd
docker compose up
docker compose up --force-recreate --build
```

#### Without docker
```cmd
gunicorn 'main:app' --bind=0.0.0.0:5000
```
or
```cmd
python main.py [dev] [poll]
```
* dev - run in dev mode (use `config_dev.txt` instead of `config.txt`)
* poll - if passed run long polling to get bot updates, otherwise start flask server


### Usage

#### Commands:

* /set_news_chat - news will be sent to chat where command was sent
* /unset_news_chat - cancel news sending in the current chat
* /news_bot_version - display current bot version

#### Настройка квестов

1. Создайте супергруппу (с топиками)
2. Добавте бота в группу
3. Выполните команду /get_chat_id
4. Полученное число (с минусом) запишите в файл конфига `config.txt`
    ```
    quest_room = -1234567891011
    ```
5. Перезапустите бота -> Готово!

* Каждый созданный топик в группе будет зарегистрирован как квест.
* Название квеста совпадает с названием топика (обновляется автоматически при изменении).
* В каждый новый топик бот отправит сообщение с кнопкой для открытия сканера qr-кода игроков для засчета выполнения данного квеста.
* Игрок получает qr-код при старте бота.
* Все участники группы могут использовать сканер.
* Награду за квест можно назначить командой `/set_reward целое`, использовав её в нужном топике
* В группе доступна команда `/stats` для получения краткой статистики по квестам.
