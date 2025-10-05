import shutil


def main():
    print("Update")
    update_cfg(False)
    update_cfg(True)
    update_cfg_vk()
    print("Moving 'db/' -> 'storage/db/")
    shutil.move("db/", "storage/db/")
    print("Updated")


def update_cfg(dev: bool):
    try:
        token_path = "token_dev.txt" if dev else "token.txt"
        config_path = "config_dev.txt" if dev else "config.txt"
        print(f"Updating {token_path} -> {config_path}")
        with open(token_path, "r", encoding="utf8") as f:
            bot_token = f.readline().strip()
            botname = f.readline().strip()
            webhook_token = f.readline().strip()
            url = f.readline().strip()
        with open(config_path, "w", encoding="utf8") as f:
            f.write(f"bot_token = {bot_token}\n")
            f.write(f"bot_name = {botname}\n")
            f.write(f"webhook_token = {webhook_token}\n")
            f.write(f"url = {url}\n")
    except Exception as x:
        print(x)


def update_cfg_vk():
    try:
        token_vk_path = "token_vk.txt"
        config_vk_path = "config_vk.txt"
        print(f"Updating {token_vk_path} -> {config_vk_path}")
        with open(token_vk_path, "r", encoding="utf8") as f:
            confirmation = f.readline().strip()
            secret = f.readline().strip()
        with open(config_vk_path, "w", encoding="utf8") as f:
            f.write(f"confirmation_code = {confirmation}\n")
            f.write(f"callback_secret = {secret}\n")
    except Exception as x:
        print(x)


if __name__ == "__main__":
    main()
