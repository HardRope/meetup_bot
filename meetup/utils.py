import telegram
from environs import Env

from .models import Meetuper


def notify():
    env = Env()
    env.read_env()
    meetupers = Meetuper.objects.all()
    bot = telegram.Bot(token=env.str('TELEGRAM_TOKEN'))
    for meetuper in meetupers:
        bot.send_message(
            text='Проведены изменения в программе',
            chat_id=meetuper.chat_id
        )
