from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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
    ]
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_donate_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Пожертвовать на мероприятие', callback_data='donate')],
        [InlineKeyboardButton('В меню', callback_data='main_menu')],
    ]

    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_meetup_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Посмотреть программу мероприятия', callback_data='description')],
        [InlineKeyboardButton('Задать вопрос {speaker}', callback_data='question')],
        [InlineKeyboardButton('В меню', callback_data='main_menu')],
    ]

    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup



