import string
import sys
import uuid
from random import choices


def init_values(dev=False):
    print(f"init_values {dev=}")
    print()
    print("-" * 20)
    print()
    print("Configuration")
    print()
    config_path = "config_dev.txt" if dev else "config.txt"
    config_vk_path = "config_vk.txt"

    bot_token = None
    botname = None
    webhook_token = str(uuid.uuid4())
    url = None
    confirmation = None
    secret = randstr(12).lower()
    try:
        with open(config_path, "r", encoding="utf8") as f:
            bot_token = f.readline().strip()
            botname = f.readline().strip()
            webhook_token = f.readline().strip()
            url = f.readline().strip()
    except Exception:
        pass
    try:
        with open(config_vk_path, "r", encoding="utf8") as f:
            confirmation = f.readline().strip()
            secret = f.readline().strip()
    except Exception:
        pass

    with open(config_path, "w", encoding="utf8") as f:
        print(f"->{config_path}")
        print("  tg bot")
        write_cfg(f, "token", bot_token, "<token>")
        write_cfg(f, "botname (like @mycoolbot)", botname, "<botname>")
        f.write(webhook_token + "\n")
        url = write_cfg(f, "host url", url, "<url>", lambda v: v.rstrip("/") + "/" if v else v)
    print()
    with open(config_vk_path, "w", encoding="utf8") as f:
        print(f"->{config_vk_path}")
        print("  VK callback")
        write_cfg(f, "confirmation code", confirmation, "<confirmation>")
        f.write(secret)
        print("  Callback url:")
        print(url + "api/vk_callback")
        print("  Secret key:")
        print(secret)

    print()
    print("-" * 20)
    print()
    print("Configured")
    print()


def randstr(N: int):
    return ''.join(choices(string.ascii_uppercase + string.digits, k=N))


def input_def(d: str):
    inp = input("> ")
    if inp == "":
        return d
    return inp


def write_cfg(f, name, cur, d, ff=None):
    print()
    print(f"  Enter {name}:")
    if cur is None:
        cur = d
    else:
        print(cur)
    v = input_def(cur)
    if ff:
        v = ff(v)
    f.write(v + "\n")
    return v


if __name__ == "__main__":
    init_values("dev" in sys.argv)
