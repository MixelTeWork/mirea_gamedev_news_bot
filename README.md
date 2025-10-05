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
* /news_bot_version - display current bot version
