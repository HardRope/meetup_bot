import telegram
from environs import Env
from django.core.management.base import BaseCommand

from meetup.models import Topic


class Command(BaseCommand):
    help = 'Send mitup approval'

    def handle(self, *args, **kwargs):
        env = Env()
        env.read_env()

        allowed_topics = Topic.objects.filter(is_allowed=True)

        meetupers = [topic.meetuper for topic in allowed_topics]

        bot = telegram.Bot(token=env.str('TELEGRAM_TOKEN'))
        for meetuper in meetupers:
            bot.send_message(
                text='Вы одобрены в качестве спикера на наш следующий митап',
                chat_id=meetuper.chat_id
            )
