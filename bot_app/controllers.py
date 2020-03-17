from flask import request, render_template
from werkzeug.exceptions import abort

from bot_app import app, logger
from bot_config import *
from form_models.ReigsterForm import RegisterForm
from services import vk_services, school_services


@app.route('/')
def main_route():
    return 'Hello, world!'


@app.route('/vk', methods=["POST"])
def vk_handler():
    json_request = request.get_json()

    if json_request.get('secret') != VK_SECRET_KEY:
        logger.warning(f"Got incorrect secret_key: {json_request.get('secret')}")
        abort(403)

    request_type = json_request.get('type')

    if request_type == 'confirmation' and json_request.get('group_id') == VK_GROUP_ID:
        logger.info(f"Got confirmation request with data: {json_request}")
        return VK_CONFIRMATION_TOKEN

    if request_type == 'message_new':
        response_id = vk_services.handle_message(json_request)
        return 'ok'

    if request_type == 'message_reply':
        return 'ok'


@app.route('/register/<int:vk_id>', methods=['GET', 'POST'])
def register(vk_id):
    form = RegisterForm()
    if form.validate_on_submit():
        if not school_services.register(vk_id, form):
            return render_template('register.html', form=form, message='Неверный логин или пароль')
        return render_template('success.html', message='Поздравляю, вы успешно привязали аккаунт '
                                                       'Электронной школы! Пожалуйста, следуйте '
                                                       'инструкциям бота')
    return render_template('register.html', form=form)
