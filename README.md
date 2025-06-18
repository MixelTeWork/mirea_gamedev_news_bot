# MIREA Gamedev News Bot
## How to run

### Requirements
Python == 3.9.*

```cmd
python -m .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
```cmd
python scripts\init_values.py
```

Command will create files in project root:

`token.txt`
```
<tg bot token>
<botname - like @mycoolbot>
<webhook secret - random string>
<host url>
```

`token_vk.txt`
```
<callback confirmation code>
<secret key - random string>
```

#### Webhook configuration
set
```cmd
python scripts\configureWebhook.py set
```
delete
```cmd
python scripts\configureWebhook.py delete
```

#### Настройка VK Callback
1) Откройте управление сообществом
2) Перейдите во вкладку "Дополнительно", далее "Работа с API"
3) Откройте вкладку "Callback API" и добавте сервер
    * Версия API: 5.199
    * Адрес: <хост>/api/vk_callback
    * Отображаемый код подтверждения необходимо ввести при запуске скрипта `init_values.py` или в файл `token_vk.txt` первой строкой
    * Секретный ключ: строка выведенная скриптом `init_values.py` (сохранена в файле `token_vk.txt` второй строкой)
    * Нажмите "Сохранить"
    * Перед нажатием "Подтвердить" включите сервер
4) Настройте "Типы событий", активируйте пункт:
    * Записи на стене: Добавление


### Run

```cmd
python main.py [dev] [server]
```
* dev - run in dev mode (use `token_dev.txt` instead of `token.txt`)
* server - if passed start flask server otherwise run long polling to get bot updates

WSGI:
```py
from main import app
```