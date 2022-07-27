import json
from django.core.management.base import BaseCommand

from meetup.models import (
    MeetupProgram,
    Stage,
    Block,
    Event
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        meetups_filepath = 'meetups.json'

        with open(meetups_filepath, encoding='UTF-8', mode='r') as f:
            meetups = json.loads(f.read())
        for serialized_meetup in meetups:
            meetup, _ = MeetupProgram.objects.get_or_create(
                title=serialized_meetup['title'],
                defaults={
                    'date': serialized_meetup['date'],
                    'start_time': serialized_meetup['start_time'],
                    'end_time': serialized_meetup['end_time'],
                }
            )
            for serialized_stage in serialized_meetup['stages']:
                stage, _ = Stage.objects.get_or_create(
                    title=serialized_stage['title'],
                    defaults={
                        'program': meetup,
                        'start_time': serialized_stage['start_time'],
                        'end_time': serialized_stage['end_time'],
                    }
                )
                for serialized_block in serialized_stage['blocks']:
                    block, _ = Block.objects.get_or_create(
                        title=serialized_block['title'],
                        defaults={
                            'stage': stage,
                            'start_time': serialized_block['start_time'],
                            'end_time': serialized_block['end_time'],
                        }
                    )
                    for serialized_event in serialized_block['events']:
                        event, _ = Event.objects.get_or_create(
                            title=serialized_event['title'],
                            defaults={
                                'block': block,
                                'start_time': serialized_event['start_time'],
                                'end_time': serialized_event['end_time'],
                            }
                        )
