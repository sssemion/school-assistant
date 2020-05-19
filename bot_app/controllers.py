import datetime

from flask import request, render_template, jsonify
from werkzeug.exceptions import abort

from bot_app import app, logger
from bot_app.bot_config import *
from bot_app.form_models.ReigsterForm import RegisterForm
from bot_app.services import vk_services, school_services


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
    from bot_app.data.db_session import create_session
    from bot_app.data.student import Student
    session = create_session()
    if session.query(Student).filter(Student.vk_id == vk_id).first() is None or \
            session.query(Student).filter(
                Student.vk_id == vk_id).first().dialogue_point != 'register':
        try:
            logger.error(
                f"Registered user: {vk_id}. DP = {session.query(Student).filter(Student.vk_id == vk_id).first().dialogue_point}")
        except AttributeError:
            logger.error(f"Unrecognized user: {vk_id}")
        abort(404)
    form = RegisterForm()
    if form.validate_on_submit():
        if not school_services.register(vk_id, form):
            return render_template('register.html', form=form, message='Неверный логин или пароль')
        return render_template('success.html', message='Поздравляю, вы успешно привязали аккаунт '
                                                       'Электронной школы! Пожалуйста, следуйте '
                                                       'инструкциям бота')
    return render_template('register.html', form=form)


LAST_MAILING = None


@app.route('/vk/start_mailing', methods=['POST'])
def start_mailing():
    request_json = request.get_json()

    # Для защиты от сторонних запросов
    if request_json.get('key') != MAILING_KEY:
        logger.warning('Incorrect Mailing_key')
        abort(403)

    # Для защиты от повторных запросов
    global LAST_MAILING
    if LAST_MAILING is not None and \
            datetime.datetime.now() - LAST_MAILING < datetime.timedelta(hours=23, minutes=59):
        logger.warning('Mailing is not scheduled')
        abort(400)

    LAST_MAILING = datetime.datetime.now()
    vk_services.mailing_hometask()
    return jsonify({'success': True})
