from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from meetup.models import (
    Meetuper,
    MeetupProgram,
    Stage,
    Speaker
)


def check_question(chat_id):
    speaker = Speaker.objects.filter(participant__chat_id=chat_id).first()
    questions = speaker.received_questions.all()

    return speaker and questions


def check_communication(chat_id):
    return Meetuper.objects.get(chat_id=chat_id).is_open_for_communication


def get_subscribtion_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Отправить E-mail', callback_data='mail')],
        [InlineKeyboardButton('Не отправлять', callback_data='no_mail')],
    ]
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_main_menu(chat_id):
    inline_keyboard = [
        [InlineKeyboardButton('Мероприятие', callback_data='meetup')],
        [InlineKeyboardButton('Общение', callback_data='communication')],
        [InlineKeyboardButton('Донат', callback_data='donate')],
    ]

    if check_question(chat_id):
        inline_keyboard.append([InlineKeyboardButton('Вопросы от пользователей', callback_data='questions')])

    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_meetup_description_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Посмотреть программу мероприятия', callback_data='description')],
        [InlineKeyboardButton('Задать вопрос спикеру', callback_data='question')],
        [InlineKeyboardButton('В меню', callback_data='main_menu')]
    ]
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_donate_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Пожертвовать 500 рублей', callback_data=500)],
        [InlineKeyboardButton('Пожертвовать 1000 рублей', callback_data=1000)],
        [InlineKeyboardButton('В меню', callback_data='main_menu')],
    ]

    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_meetup_menu():
    meetup = MeetupProgram.objects.last()

    inline_keyboard = [
        [InlineKeyboardButton(stage.title, callback_data=stage.id)] for stage in meetup.stages.all()
    ]

    inline_keyboard.append([InlineKeyboardButton('В меню', callback_data='main_menu')])
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_stage_menu(stage):
    stage = Stage.objects.get(id=stage)
    inline_keyboard = [
        [
            InlineKeyboardButton(f'{block.start_time}\n{block.title}', callback_data=block.id)
        ] for block in stage.blocks.all()
    ]
    inline_keyboard.append([InlineKeyboardButton('Назад', callback_data='back')])
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_back_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Назад', callback_data='back')],
    ]

    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_communication_menu(chat_id):
    inline_keyboard = []
    open_for_communication_meetuper = Meetuper.objects.filter(is_open_for_communication=True)

    if not check_communication(chat_id):
        inline_keyboard.append([InlineKeyboardButton('Заполнить анкету', callback_data='form')])
    if check_communication(chat_id):
        inline_keyboard.append([InlineKeyboardButton('Пообщаться', callback_data='communicate')])
    inline_keyboard.append([InlineKeyboardButton('В меню', callback_data='main_menu')])

    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_stage_speakers(stage_id):
    stage = MeetupProgram.objects.last().stages.get(id=stage_id)
    blocks = stage.blocks.all()
    speakers_chat_id = []
    for block in blocks:
        events = block.events.all()
        event_speakers = [event.speaker.participant.chat_id for event in events]
        speakers_chat_id.extend(event_speakers)

    inline_keyboard = [
        [InlineKeyboardButton(Meetuper.objects.get(chat_id=speaker_id).firstname, callback_data=speaker_id)]
        for speaker_id in speakers_chat_id
    ]

    inline_keyboard.append([InlineKeyboardButton('Назад', callback_data='back')])
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_form_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Заполнить анкету', callback_data='form')],
        [InlineKeyboardButton('В меню', callback_data='main_menu')],
    ]

    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_contact_menu(chat_id=0):
    inline_keyboard = []
    if chat_id:
        meetuper = Meetuper.objects.get(chat_id=chat_id)
        inline_keyboard.append(
            [InlineKeyboardButton(
                f'Начать чат c {meetuper.lastname} {meetuper.firstname}',
                callback_data=f'chat {meetuper.chat_id}',
                url=f'tg://user?id={meetuper.chat_id}'
            )]
        )
    inline_keyboard.append([InlineKeyboardButton('В меню', callback_data='main_menu')])

    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup
