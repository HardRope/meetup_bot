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
        [InlineKeyboardButton('Мероприятие', callback_data='mitup')],
        [InlineKeyboardButton('Общение', callback_data='communication')],
    ]
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_meetup_description_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Задать вопрос {speaker}', callback_data='question')],
        [InlineKeyboardButton('Посмотреть программу мероприятия', callback_data='description')],
    ]
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup

