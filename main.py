import sys
from bafser import AppConfig, create_app
# from scripts.init_values import init_values
from bot.main import process_update, setup_bot
import tgapi
import vkapi


tgapi.setup("token_dev.txt" if __name__ == "__main__" else "token.txt")
vkapi.setup()
setup_bot()
app, run = create_app(__name__, AppConfig(
    MESSAGE_TO_FRONTEND="",
    DEV_MODE="dev" in sys.argv,
    DELAY_MODE="delay" in sys.argv,
))

# run(__name__ == "__main__", lambda: init_dev_values(True), port=5001)

# run(False, lambda: init_values(True))
run(False)
# run(True, port=5000)

if __name__ == "__main__":
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
