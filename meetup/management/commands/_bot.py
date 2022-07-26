import logging

import redis
from environs import Env
from telegram import LabeledPrice
from telegram.ext import (Filters,
                          Updater,
                          CallbackQueryHandler,
                          CommandHandler,
                          MessageHandler,
                          PreCheckoutQueryHandler,
                          )

from meetup.models import User

env = Env()
env.read_env()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

_database = None


def error(state, error):
    logger.warning(f'State {state} caused error {error}')


def start(context, update):
    tg_id = update.message.chat.id
    print(tg_id)
    update.message.reply_text(
        'Привет! Я бот для проведения митапов'
    )

    return 'NEXT'


def start_without_shipping(update, context):
    chat_id = update.message.chat.id
    payment_token = env.str('PAY_TOKEN')
    title = f'Donate №{chat_id}'
    description = 'Своим донатом вы помогаете организовать митап'
    payload = 'Custom_order'
    currency = 'RUB'
    prices = [LabeledPrice('Test', 100000)]
    context.bot.sendInvoice(
        chat_id,
        title,
        description,
        payload,
        payment_token,
        currency,
        prices
    )


def precheckout_callback(update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != f"Custom_order":
        context.bot.answer_pre_checkout_query(
            pre_checkout_query_id=query.id,
            ok=False,
            error_message="Что то пошло не так"
        )
    else:
        context.bot.answer_pre_checkout_query(
            pre_checkout_query_id=query.id,
            ok=True
        )


def successful_payment_callback(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Спасибо за донат'
    )
    # context.bot.delete_message(
    #     chat_id=update.message.chat_id,
    #     message_id=update.message.message_id
    # )


def handle_users_reply(update, context):
    db = get_database_connection()

    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id)

    states_functions = {
        'START': start,
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(context, update)
        db.set(chat_id, next_state)
    except Exception as err:
        error(user_state, err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = env.str("DATABASE_PASSWORD")
        database_host = env.str("DATABASE_HOST")
        database_port = env.str("DATABASE_PORT")
        _database = redis.Redis(
            host=database_host,
            port=database_port,
            password=database_password,
            decode_responses=True,
        )
    return _database


def main():
    tg_token = env.str('TELEGRAM_TOKEN')

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    # dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(CommandHandler('pay', start_without_shipping))
    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
