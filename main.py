import sys
from bafser import AppConfig, create_app
# from scripts.init_values import init_values
from bot.main import process_update, setup_bot
import tgapi
import vkapi

DEV_MODE = "dev" in sys.argv
RUN = __name__ == "__main__"
RUN_FLASK_SERVER = RUN and "server" in sys.argv
RUN_BOT_LONG_POLL = RUN and not RUN_FLASK_SERVER

tgapi.setup("token_dev.txt" if DEV_MODE else "token.txt")
vkapi.setup()
setup_bot()
app, run = create_app(__name__, AppConfig(
    DEV_MODE=DEV_MODE,
))

# run(__name__ == "__main__", lambda: init_dev_values(True), port=5001)

# run(False, lambda: init_values(True))
run(RUN_FLASK_SERVER)
# run(True, port=5000)

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
