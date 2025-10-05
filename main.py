import sys

import bafser_tgapi as tgapi
from bafser import AppConfig, create_app

import vkapi
from bot.bot import Bot

app, run = create_app(__name__, AppConfig(DEV_MODE="dev" in sys.argv))
tgapi.setup(botCls=Bot, app=app)
vkapi.setup()

RUN = __name__ == "__main__"
RUN_SERVER = RUN and "poll" not in sys.argv
if RUN_SERVER:
    tgapi.set_webhook()
run(RUN_SERVER, port=5000)

if not RUN_SERVER:
    if RUN:
        tgapi.run_long_polling()
    else:
        tgapi.set_webhook()
