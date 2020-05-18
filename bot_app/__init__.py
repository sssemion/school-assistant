import logging
# import threading

from flask import Flask

from bot_app.data import db_session

app = Flask(__name__)
app.config.from_object('config')

formatter = logging.Formatter(f"%(asctime)s %(name)s:%(levelname)s: %(message)s")

# Moving thr latest logs to the archive
for filename in ['errors', 'warning', 'debug']:
    with open(f'logs/{filename}.log', 'r') as last, \
         open(f'logs/archive/{filename}.log', 'a') as archive:
        archive.write(last.read())

error_handler = logging.FileHandler('logs/errors.log', 'w')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

warning_handler = logging.FileHandler('logs/warning.log', 'w')
warning_handler.setLevel(logging.WARNING)
warning_handler.setFormatter(formatter)

debug_handler = logging.FileHandler('logs/debug.log', 'w')
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(0)
logger.addHandler(error_handler)
logger.addHandler(warning_handler)
logger.addHandler(debug_handler)

db_session.global_init("bot_app/db/school_assistant.sqlite")

from bot_app import controllers
# from bot_app.services import vk_services
#
#
# def mailing():
#     print(*threading.enumerate())
#     import schedule
#     schedule.every().day.at("16:00").do(vk_services.mailing_hometask)
#
#     while True:
#         schedule.run_pending()
#
#
# scheduleThread = threading.Thread(target=mailing, name='ScheduleThread')
# scheduleThread.start()
