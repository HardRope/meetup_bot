from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from meetup.models import MeetupProgram, Stage, Block

def get_subscribtion_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Отправить E-mail', callback_data='mail')],
        [InlineKeyboardButton('Не отправлять', callback_data='no_mail')],
    ]
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_main_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Мероприятие', callback_data='meetup')],
        [InlineKeyboardButton('Общение', callback_data='communication')],
        [InlineKeyboardButton('Донат', callback_data='donate')],
    ]
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_meetup_description_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Посмотреть программу мероприятия', callback_data='description')],
        [InlineKeyboardButton('Задать вопрос {speaker}', callback_data='question')],
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
        [InlineKeyboardButton(f'{block.start_time}\n{block.title}', callback_data=block.id)] for block in stage.blocks.all()
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
