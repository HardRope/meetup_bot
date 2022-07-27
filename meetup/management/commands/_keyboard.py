from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_subscribtion_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Отправить E-mail', callback_data='mail')],
        [InlineKeyboardButton('Не отправлять', callback_data='no_mail')],
    ]
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup


def get_meetup_description_menu():
    inline_keyboard = [
        [InlineKeyboardButton('Расписание митапа', callback_data='schedule')],
        [InlineKeyboardButton('Докладчики митапа', callback_data='speakers')],
    ]
    inline_kb_markup = InlineKeyboardMarkup(inline_keyboard)

    return inline_kb_markup

