import telegram
from environs import Env

from .models import Meetuper, Notification


def notify_program_change():
    env = Env()
    env.read_env()
    meetupers = Meetuper.objects.filter(is_active=True)
    bot = telegram.Bot(token=env.str('TELEGRAM_TOKEN'))
    for meetuper in meetupers:
        bot.send_message(
            text='Проведены изменения в программе',
            chat_id=meetuper.chat_id
        )


def send_notification():
    env = Env()
    env.read_env()
    meetupers = Meetuper.objects.filter(is_active=True)
    notification = Notification.objects.order_by('-created_at').first()
    bot = telegram.Bot(token=env.str('TELEGRAM_TOKEN'))
    for meetuper in meetupers:
        bot.send_message(
            text=notification.text,
            chat_id=meetuper.chat_id
        )
