import logging


confirmation_code = ""
callback_secret = ""


def setup(token_path="token_vk.txt"):
    global confirmation_code, callback_secret
    try:
        with open(token_path) as f:
            confirmation_code = f.readline().strip()
            callback_secret = f.readline().strip()
    except Exception as e:
        logging.error(f"Cant read vk token\n{e}")
        raise e


def get_confirmation_code():
    return confirmation_code


def check_callback_secret(secret: str):
    return secret == callback_secret
