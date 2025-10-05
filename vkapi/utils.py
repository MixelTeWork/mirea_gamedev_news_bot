import logging

import bafser_tgapi as tgapi

confirmation_code = ""
callback_secret = ""


def setup(token_path="config_vk.txt"):
    global confirmation_code, callback_secret
    try:
        data = tgapi.utils.read_config(token_path)
        confirmation_code = data["confirmation_code"]
        callback_secret = data["callback_secret"]
    except Exception as e:
        logging.error(f"Cant read vk token\n{e}")
        raise e


def get_confirmation_code():
    return confirmation_code


def check_callback_secret(secret: str):
    return secret == callback_secret
