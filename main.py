import sys
from bafser import AppConfig, create_app
# from scripts.init_values import init_values
from bot.main import process_update, setup_bot
import tgapi
import vkapi

DEV_MODE = "dev" in sys.argv
RUN = __name__ == "__main__"
RUN_BOT_LONG_POLL = RUN and "poll" in sys.argv
RUN_FLASK_SERVER = RUN and not RUN_BOT_LONG_POLL

tgapi.setup("token_dev.txt" if DEV_MODE else "token.txt")
vkapi.setup()
setup_bot()
app, run = create_app(__name__, AppConfig(
    DEV_MODE=DEV_MODE,
))


# run(False, lambda: init_values(True))
run(RUN_FLASK_SERVER, port=5000)

if RUN_BOT_LONG_POLL:
    print("listening for updates...")
    update_id = -1
    while True:
        ok, updates = tgapi.getUpdates(update_id + 1, 60)
        if not ok:
            print("Error!", updates)
            break
        for update in updates:
            update_id = max(update_id, update.update_id)
            process_update(update)
