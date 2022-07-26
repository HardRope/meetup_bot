from django.conf import settings
from django.core.management.base import BaseCommand

from ._bot import main


class Command(BaseCommand):
    help = 'Start bot'

    def handle(self, *args, **options):
        main()
