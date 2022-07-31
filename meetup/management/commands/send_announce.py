import telegram
from environs import Env
from django.core.management.base import BaseCommand

from meetup.models import Meetuper,  MeetupProgram


class Command(BaseCommand):
    help = 'Send meetup announcement'

    def handle(self, *args, **kwargs):
        env = Env()
        env.read_env()

        meetup = MeetupProgram.objects.last()

        subscribed_meetupers = Meetuper.objects.filter(is_subcribed_next_meetup=True)

        bot = telegram.Bot(token=env.str('TELEGRAM_TOKEN'))
        for meetuper in subscribed_meetupers:
            message_text = f'''
Привет, {meetuper.firstname}. Рады сообщить, что очень скоро состоится наш новый митап "{meetup.title}".

Ждем тебя {meetup.date}. Начнем в {meetup.start_time}, а закончим в {meetup.end_time}.
            '''
            bot.send_message(
                text=message_text,
                chat_id=meetuper.chat_id
            )