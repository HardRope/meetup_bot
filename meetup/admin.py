import json

from django.contrib import admin
from django.db.models.functions import TruncDay
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import path
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder

from .models import (
    Meetuper,
    Speaker,
    MeetupProgram,
    Stage,
    Block,
    Event,
    Question,
    Donation,
    Notification,
    Topic,
)
from .utils import notify_program_change, send_notification


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Meetuper)
class MeetuperAdmin(admin.ModelAdmin):
    list_display = [
        'chat_id',
        'firstname',
        'lastname',
        'email',
        'phone_number',
        'organization',
        'position',
        'is_open_for_communication',
        'is_active',
    ]
    list_filter = [
        'organization',
        'position',
        'is_open_for_communication',
        'is_active',
    ]
    list_editable = [
        'is_open_for_communication',
        'is_active',
    ]
    search_fields = [
        'firstname',
        'lastname',
    ]
    inlines = [
        QuestionInline,
    ]
    save_on_top = True


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_filter = ['is_active']
    list_display = [
        'participant',
        'is_active',
    ]
    list_editable = [
        'is_active',
    ]
    inlines = [
        QuestionInline,
    ]


class StageInline(admin.TabularInline):
    model = Stage
    extra = 1


@admin.register(MeetupProgram)
class MeetupProgramAdmin(admin.ModelAdmin):
    list_filter = ['date']
    list_display = [
        'title',
        'date',
        'start_time',
        'end_time',
        'current',
    ]
    list_editable = [
        'current',
    ]
    search_fields = [
        'title',
    ]
    inlines = [
        StageInline,
    ]
    save_on_top = True
    save_as = True
    change_form_template = 'meetups_change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:pk>/change/notify/', self.send_notifications),
            path(
                '<int:pk>/change/program_changed/',
                self.send_program_notifications
            )
        ]
        return my_urls + urls

    def send_notifications(self, request, pk):
        send_notification()
        self.message_user(request, 'Объявление отправлено')
        return redirect(f'../../../{pk}/change/')

    def send_program_notifications(self, request, pk):
        notify_program_change()
        self.message_user(
            request,
            'Оповещения об изменениях в программе отправлены'
        )
        return redirect(f'../../../{pk}/change/')


class BlockInline(admin.TabularInline):
    model = Block
    extra = 1


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_filter = ['program']
    list_display = [
        'title',
        'program',
        'start_time',
        'end_time'
    ]
    search_fields = [
        'title',
    ]
    inlines = [
        BlockInline,
    ]
    save_as = True
    save_on_top = True


class EventInline(admin.TabularInline):
    model = Event
    extra = 1


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_filter = ['stage']
    list_display = [
        'title',
        'stage',
        'start_time',
        'end_time'
    ]
    search_fields = ['title']
    inlines = [
        EventInline,
    ]
    save_as = True
    save_on_top = True


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_filter = ['is_active', 'speaker']
    list_display = [
        'title',
        'speaker',
        'block',
        'start_time',
        'end_time',
        'is_active'
    ]
    list_editable = [
        'is_active',
    ]
    save_as = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_filter = [
        'date',
        'is_answered',
        'speaker'
    ]
    list_display = [
        'text',
        'date',
        'speaker',
        'meetuper',
        'is_answered'
    ]


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_filter = ['date']
    list_display = [
        'meetuper',
        'date',
        'amount',
    ]

    def changelist_view(self, request, extra_context=None):
        chart_data = self.chart_data()
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {'chart_data': as_json}

        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path('chart_data/', self.admin_site.admin_view(self.chart_data_endpoint)),
        ]
        return extra_urls + urls

    def chart_data_endpoint(self, request):
        chart_data = self.chart_data()
        return JsonResponse(list(chart_data), safe=False)

    def chart_data(self):
        return (
            Donation.objects.annotate(donation_date=TruncDay('date'))
            .values('date')
            .annotate(y=Sum('amount'))
        )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_filter = ['created_at']
    list_display = [
        'text',
        'created_at',
    ]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = [
        'meetuper',
        'title',
        'created_at',
        'is_allowed',
    ]
    list_editable = [
        'is_allowed',
    ]
