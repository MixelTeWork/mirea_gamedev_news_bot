import sys
import os


def init_values(dev=False, cmd=False):
    print(f"init_values {dev=}")
    if cmd:
        add_parent_to_path()

    os.environ["dev"] = "1" if dev else "0"
    import alembic.config
    import uuid
    from bafser import db_session, init_db_values, randstr
    # from data._roles import Roles
    # from data.user import User

    if cmd or not dev:
        alembic.config.main(argv=["upgrade", "head"])
        init_db_values(dev)

    # db_session.global_init(dev)
    # db_sess = db_session.create_session()

    # u = User.new(db_sess, 5377785956, False, "Mixel", "", "MixelTe", "en")
    # u.add_role(u, Roles.admin)

    # db_sess.commit()
    # db_sess.close()

    print()
    print("-" * 20)
    print()
    print("Configuration (can be skiped by Enter)")
    print()
    token_path = "token_dev.txt" if dev else "token.txt"
    token_vk_path = "token_vk.txt"

    bot_token = None
    botname = None
    webhook_token = str(uuid.uuid4())
    url = None
    confirmation = None
    secret = randstr(12).lower()
    try:
        with open(token_path, "r", encoding="utf8") as f:
            bot_token = f.readline().strip()
            botname = f.readline().strip()
            webhook_token = f.readline().strip()
            url = f.readline().strip()
    except Exception:
        pass
    try:
        with open(token_vk_path, "r", encoding="utf8") as f:
            confirmation = f.readline().strip()
            secret = f.readline().strip()
    except Exception:
        pass

    with open(token_path, "w", encoding="utf8") as f:
        print(f"->{token_path}")
        print("  tg bot")
        write_cfg(f, "token", bot_token, "<token>")
        write_cfg(f, "botname (like @mycoolbot)", botname, "<botname>")
        f.write(webhook_token + "\n")
        write_cfg(f, "host url", url, "<url>")
    print()
    with open(token_vk_path, "w", encoding="utf8") as f:
        print(f"->{token_vk_path}")
        print("  VK callback")
        write_cfg(f, "confirmation code", confirmation, "<confirmation>")
        f.write(secret)
        print("  Secret key:")
        print(secret)

    print()
    print("-" * 20)
    print()
    print("Configured")
    print()


def add_parent_to_path():
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)


def input_def(d: str):
    inp = input("> ")
    if inp == "":
        return d
    return inp


def write_cfg(f, name, cur, d):
    print()
    print(f"  Enter {name}:")
    if cur is None:
        cur = d
    else:
        print(cur)
    f.write(input_def(cur) + "\n")


if __name__ == "__main__":
    init_values("dev" in sys.argv, True)
