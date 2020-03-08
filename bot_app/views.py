from flask import request
from werkzeug.exceptions import abort

from bot_app import app, logger
from bot_config import *


@app.route('/')
def main_route():
    return 'Hello, world!'


@app.route('/vk', methods=["POST"])
def vk_handler():
    json_request = request.get_json()

    if json_request.get('secret') != VK_SECRET_KEY:
        logger.warning(f"Got incorrect secret_key: {json_request.get('secret')}")
        abort(403)

    if json_request.get('type') == 'confirmation' and json_request.get('group_id') == VK_GROUP_ID:
        logger.info(f"Got confirmation request with data: {json_request}")
        return VK_CONFIRMATION_TOKEN
