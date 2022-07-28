from django.core.management.base import BaseCommand

from meetup.models import Meetuper


class Command(BaseCommand):
    def handle(self, *args, **options):
        meetupers = Meetuper.objects.all()
        for meetuper in meetupers:
            meetuper.is_active = False
            meetuper.is_open_for_communication = False
            meetuper.save()
