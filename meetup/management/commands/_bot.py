import json
import logging
import os.path
import random
from textwrap import dedent

import redis
import requests
from environs import Env
from telegram import LabeledPrice
from telegram.ext import (
    Filters,
    Updater,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
)
from django.conf import settings
from django.core.files import File

from ._keyboard import (
    get_subscribtion_menu,
    get_main_menu,
    get_donate_menu,
    get_meetup_menu,
    get_stage_menu,
    get_back_menu,
    get_meetup_description_menu,
    get_communication_menu,
    get_block_speakers,
    get_contact_menu,
)

from meetup.models import (
    Meetuper,
    MeetupProgram,
    Stage,
    Speaker,
    Block,
    Donation,
    Question
)

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
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name

    meetup = MeetupProgram.objects.last()

    Meetuper.objects.get_or_create(
        chat_id=tg_id,
        defaults={
            'firstname': first_name,
            'lastname': last_name,
        }
    )

    if Speaker.objects.filter(participant__chat_id=tg_id):
        message_text = f'''
        Приветствую, {first_name}!         
        Вы подписались на чат-бота митапа <b><i>"{meetup.title}"</i></b>.
        Наш митап пройдет {meetup.date} с {meetup.start_time} до {meetup.end_time}.
        
        <b>Рады видеть Вас в качестве спикера на нашем митапе!</b>
        
        
        Подтвердите регистрацию на митап <b><i>"{meetup.title}"</i></b> отправив нам свой e-mail. Обещаем не спамить.))
        А можете и не отправлять мы все равно вам рады.)))
        '''

    else:
        message_text = f'''
        Приветствую, {first_name}! 
        Вы подписались на чат-бота митапа <b><i>"{meetup.title}"</i></b>.
        Наш митап пройдет {meetup.date} с {meetup.start_time} до {meetup.end_time}.
        
        
        Подтвердите регистрацию на митап <b><i>"{meetup.title}"</i></b> отправив нам свой e-mail. Обещаем не спамить.))
        А можете и не отправлять мы все равно вам рады.)))
        '''

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=dedent(message_text),
        parse_mode='HTML',
        reply_markup=get_subscribtion_menu()
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    return 'CONFIRM_MENU'


def confirm_menu_handler(context, update):
    query = update.callback_query

    if query.data == 'no_mail':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Спасибо за подтверждение регистрации. Мы рады будем видеть Вас на митапе',
            reply_markup=get_main_menu(query.message.chat_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'MAIN_MENU'

    elif query.data == 'mail':
        message_text = f'''
        Спасибо за подтверждение регистрации. 
        
        Для завершения регистрации введите ваш email
        '''
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=dedent(message_text),
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'WAIT_EMAIL'


def wait_email_handler(context, update):
    chat_id = update.message.chat.id

    meetuper = Meetuper.objects.get(chat_id=chat_id)
    meetuper.email = update.message.text
    meetuper.save()

    meetup = MeetupProgram.objects.last()

    context.bot.send_message(
        chat_id=chat_id,
        text=f'Рады видеть Вас на митапе <b><i>"{meetup.title}"</i></b>.',
        parse_mode='HTML',
        reply_markup=get_main_menu(chat_id)
    )
    context.bot.delete_message(
        chat_id=chat_id,
        message_id=update.message.message_id - 1
    )

    return 'MAIN_MENU'


def main_menu_handler(context, update):
    query = update.callback_query
    if query.data == 'meetup':
        meetup = MeetupProgram.objects.last()
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Можете ознокомиться с программой митапа <b><i>"{meetup.title}"</i></b>.'
                 f' или задать вопрос любому спикеру',
            parse_mode='HTML',
            reply_markup=get_meetup_description_menu()
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'MEETUP_DESCRIPTION_MENU'

    elif query.data == 'communication':
        message_text = '''
        Здесь вы сможете заполнить анкету о себе и пообщаться с другими участниками митапа.
        '''

        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=dedent(message_text),
            reply_markup=get_communication_menu(query.message.chat_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'COMMUNICATION_MENU'

    elif query.data == 'donate':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Ваш вклад в наше развитие позволит нам продолжать работу над крутыми митапами',
            reply_markup=get_donate_menu()
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'DONATE'

    elif query.data == 'signup':
        message_text = '''
Чтобы стать спикером на следующем митапе нам нужно получить от Вас немного очень важной для нас информации

Для начала введите тему доклада с которой Вы хотите выступить
        '''

        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=dedent(message_text),
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'SIGNUP'

    elif query.data == 'questions':
        message_text = f'''
Вопросы от участников митапа:
{get_questions(query.message.chat_id)}
'''
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=message_text,
            reply_markup=get_back_menu()
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'QUESTIONS'


def signup_handler(context, update):
    meetuper = Meetuper.objects.get(chat_id=update.message.chat_id)
    meetuper.topics.create(
        title=update.message.text,
    )
    Speaker.objects.get_or_create(
        participant=meetuper,
    )

    message_text = '''
Чтобы узнать о Вас побольше, а потом рассказать нашим участникам о крутом докладчике на нужно ваше резюме.

Пришлите нам его в виде любого документа.
    '''

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=dedent(message_text),
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id - 1
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    return 'MAIN_MENU'


def download_cv(url, filename):
    if not os.path.exists(f'{settings.MEDIA_ROOT}'):
        os.makedirs(f'{settings.MEDIA_ROOT}')

    local_filename = f'{settings.MEDIA_ROOT}/' + filename

    response = requests.get(url)
    response.raise_for_status()

    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    return local_filename


def cv_handler(update, context):
    chat_id = update.message.chat_id

    filename = f'CV-{chat_id}.' + update.message.document.file_name.split('.')[-1]
    file_info = context.bot.get_file(update.message.document.file_id)

    cv = download_cv(file_info.file_path, filename)

    metuper = Meetuper.objects.get(chat_id=chat_id)
    with open(cv, 'rb') as f:
        metuper.cv.save(filename, File(f), False)
    metuper.save()

    context.bot.send_message(
        chat_id=chat_id,
        text=f'Как только организаторы одобрят Вас в качестве докладчика мы обязательно об этом сообщим',
        reply_markup=get_main_menu(chat_id)
    )

    context.bot.delete_message(
        chat_id=chat_id,
        message_id=update.message.message_id - 1
    )

    context.bot.delete_message(
        chat_id=chat_id,
        message_id=update.message.message_id
    )

    return 'MAIN_MENU'


def communication_menu_handler(context, update):

    query = update.callback_query

    if query.data == 'main_menu':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Рады видеть Вас на митапе',
            reply_markup=get_main_menu(query.message.chat_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'MAIN_MENU'

    elif query.data == 'form':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Введите ваше имя',
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'FIRSTNAME'

    elif query.data == 'communicate':
        meetupers_id = [
            meetuper.chat_id for meetuper in Meetuper.objects.
            filter(is_open_for_communication=True).
            exclude(chat_id=query.message.chat_id)
        ]

        if len(meetupers_id) >= 1:
            communicate_id = random.choice(meetupers_id)
            meetuper = Meetuper.objects.get(chat_id=communicate_id)

            message_text = f'''Вы можете пообщаться с 
<b><i>{meetuper.firstname} {meetuper.lastname}</i></b>.
            
{meetuper.firstname} трудится в {meetuper.organization} на должности {meetuper.position}
            
Или можете зайти сюда попозже, может быть кто-то еще будет готов пообщаться.
            '''

            context.bot.send_message(
                chat_id=query.message.chat_id,
                text=dedent(message_text),
                parse_mode='HTML',
                reply_markup=get_contact_menu(communicate_id)
            )

        else:
            message_text = '''
Нет других участников митапа, которые могут с Вами пообщаться.
            
Заходите позже.
            '''

            context.bot.send_message(
                chat_id=query.message.chat_id,
                text=dedent(message_text),
                parse_mode='HTML',
                reply_markup=get_contact_menu()
            )

        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'CHAT'


def chat_handler(context, update):
    query = update.callback_query

    if query.data == 'main_menu':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Рады видеть Вас на митапе',
            reply_markup=get_main_menu(query.message.chat_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'MAIN_MENU'


def firstname_handler(context, update):
    meetuper = Meetuper.objects.get(chat_id=update.message.chat_id)
    meetuper.firstname = update.message.text
    meetuper.save()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f'Введите вашу фамилию',
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id - 1
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    return 'LASTNAME'


def lastname_handler(context, update):
    meetuper = Meetuper.objects.get(chat_id=update.message.chat_id)
    meetuper.lastname = update.message.text
    meetuper.save()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f'Укажите место работы',
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id - 1
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    return 'ORGANIZATION'


def organization_handler(context, update):
    meetuper = Meetuper.objects.get(chat_id=update.message.chat_id)
    meetuper.organization = update.message.text
    meetuper.save()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f'Укажите вашу должность',
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id - 1
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    return 'POSITION'


def position_handler(context, update):
    meetuper = Meetuper.objects.get(chat_id=update.message.chat_id)
    meetuper.position = update.message.text
    meetuper.save()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f'Введите ваш номер телефона',
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id - 1
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    return 'PHONENUMBER'


def phonenumber_handler(context, update):
    meetuper = Meetuper.objects.get(chat_id=update.message.chat_id)
    meetuper.phone_number = update.message.text
    meetuper.save()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f'Введите ваш email',
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id - 1
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    return 'EMAIL'


def email_handler(context, update):
    meetuper = Meetuper.objects.get(chat_id=update.message.chat_id)
    meetuper.email = update.message.text
    meetuper.is_open_for_communication = True
    meetuper.save()
    message_text = '''
    Здесь вы сможете заполнить анкету о себе и пообщаться с другими участниками митапа.
    '''

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=dedent(message_text),
        reply_markup=get_communication_menu(update.message.chat_id)
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id - 1
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    return 'COMMUNICATION_MENU'


def meetup_description_menu_handler(context, update):
    query = update.callback_query

    if query.data == 'description':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Программа митапа: \n',
            reply_markup=get_meetup_menu()
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'STAGE'

    elif query.data == 'main_menu':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Рады видеть Вас на митапе',
            reply_markup=get_main_menu(query.message.chat_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'MAIN_MENU'

    elif query.data == 'question':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Выберите стейдж с интересующим Вас спикером',
            reply_markup=get_meetup_menu()
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'SPEAKERS_BLOCK'


def speakers_block_handler(context, update):
    query = update.callback_query

    if query.data.isdigit():
        user = f"user_tg_{query.message.chat_id}"
        _database.set(
            user,
            json.dumps({'stage': query.data})
        )

        message_text = f'''
        Cписок докладов потока "{Stage.objects.get(id=query.data).title}"
        '''

        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=dedent(message_text),
            reply_markup=get_stage_menu(query.data)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'SPEAKERS'

    elif query.data == 'main_menu':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Рады видеть Вас на митапе',
            reply_markup=get_main_menu(query.message.chat_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'MAIN_MENU'


def stage_handler(context, update):
    query = update.callback_query

    if query.data.isdigit():
        user = f"user_tg_{query.message.chat_id}"
        _database.set(
            user,
            json.dumps({'stage': query.data})
        )

        message_text = f'''
        Cписок докладов потока "{Stage.objects.get(id=query.data).title}"
        '''

        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=dedent(message_text),
            reply_markup=get_stage_menu(query.data)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'BLOCK'

    elif query.data == 'back':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Программа митапа: \n',
            reply_markup=get_meetup_menu()
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'STAGE'

    elif query.data == 'main_menu':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Рады видеть Вас на митапе',
            reply_markup=get_main_menu(query.message.chat_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'MAIN_MENU'


def block_handler(context, update):
    query = update.callback_query

    if query.data.isdigit():
        block = Block.objects.get(id=query.data)
        message_text = f'''
        <b><i>{block.start_time} - {block.end_time}
        Блок "{block.title}"</i></b>

        '''

        for event in block.events.all():
            message_text += f'''
            <b>{event.title}</b> 
            {event.start_time} - {event.end_time}
            '''
            if event.speaker:
                message_text += f'{event.speaker.participant.firstname} {event.speaker.participant.lastname}\n'

        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=dedent(message_text),
            parse_mode='HTML',
            reply_markup=get_back_menu()
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'BLOCK'

    elif query.data == 'back':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Программа митапа: \n',
            reply_markup=get_meetup_menu()
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'STAGE'
    
    else:
        user = f'user_tg_{query.message.chat_id}'
        stage_id = json.loads(_database.get(user))['stage']

        message_text = f'''
        
        Cписок докладов потока "{Stage.objects.get(id=stage_id).title}"             
        
        '''

        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=dedent(message_text),
            reply_markup=get_stage_menu(stage_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'STAGE'


def get_questions(tg_id):
    speaker = Meetuper.objects.get(chat_id=tg_id).speaker
    questions_query = speaker.received_questions.all()
    questions_print = ''

    for question in questions_query:
        questions_print += f'''
Вопрос от {question.meetuper.firstname} {question.meetuper.lastname}:
{question.text}
'''

    return questions_print


def speakers_handler(context, update):
    query = update.callback_query
    if query.data.isdigit():
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Спикеры в блоке {Block.objects.get(id=query.data).title}',
            reply_markup=get_block_speakers(query.data)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
            )
        return 'QUESTION'


def question_list_handler(context, update):
    query = update.callback_query

    if query.data == 'back':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Рады видеть Вас на митапе',
            reply_markup=get_main_menu(query.message.chat_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'MAIN_MENU'


def question_handler(context, update):
    query = update.callback_query

    if query.data == 'back':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Рады видеть Вас на митапе',
            reply_markup=get_main_menu(query.message.chat_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'MAIN_MENU'
    
    user = f"user_tg_{query.message.chat_id}"
    _database.set(
        user,
        json.dumps({'speaker': query.data})
    )

    context.bot.send_message(
        chat_id=query.message.chat_id,
        text='Введите Ваш вопрос',
    )
    context.bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )
    return 'SAVE_QUESTION'


def save_question_handler(context, update):
    chat_id = update.message.chat.id

    user = f'user_tg_{update.message.chat_id}'
    speaker_id = json.loads(_database.get(user))['speaker']

    speaker = Meetuper.objects.get(chat_id=speaker_id).speaker
    meetuper = Meetuper.objects.get(chat_id=chat_id)
    question_text = update.message.text

    send_notify_to_speaker(context, speaker_id)

    question = Question(
        text=question_text,
        speaker=speaker,
        meetuper=meetuper
    )
    question.save()

    context.bot.send_message(
        chat_id=chat_id,
        text=f'Ваш вопрос отправлен!',
        parse_mode='HTML',
        reply_markup=get_main_menu(chat_id)
    )
    return 'MAIN_MENU'


def send_notify_to_speaker(context, speaker_id):
    speaker = Meetuper.objects.get(chat_id=speaker_id).speaker
    questions_query = speaker.received_questions.all()
    if not questions_query:
        context.bot.send_message(
            chat_id=speaker_id,
            text=f'Вам задали вопрос.',
        )
    return

def questions_handler(context, update):
    query = update.callback_query
    if query.data.isdigit():
        speaker_id = query.data
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'{speaker_id}',
        )
        return 'ASK_QUESTION'

    elif query.data == 'back':
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Можете ознакомиться с программой митапа <b><i>"{MeetupProgram.objects.last().title}"</i></b>.'
                 f' или задать вопрос любому спикеру',
            parse_mode='HTML',
            reply_markup=get_meetup_description_menu()
        )
        return 'MEETUP_DESCRIPTION_MENU'


def start_without_shipping(context, update):
    query = update.callback_query

    if query.data.isdigit():
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        chat_id = query.message.chat.id
        payment_token = env.str('PAY_TOKEN')
        title = f'Donate №{chat_id}'
        description = 'Своим донатом вы помогаете организовать митап'
        payload = 'Custom_order'
        currency = 'RUB'
        prices = [
            LabeledPrice('Test', int(query.data) * 100),
        ]
        context.bot.sendInvoice(
            chat_id,
            title,
            description,
            payload,
            payment_token,
            currency,
            prices,
        )
        return 'MAIN_MENU'
    else:
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f'Рады видеть Вас на митапе',
            reply_markup=get_main_menu(query.message.chat_id)
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )

        return 'MAIN_MENU'


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
    meetuper = Meetuper.objects.get(chat_id=update.message.chat.id)

    Donation.objects.create(
        meetuper=meetuper,
        date=update.message.date,
        amount=update.message.successful_payment.total_amount / 100,
    )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Рады видеть Вас на митапе',
        reply_markup=get_main_menu(update.message.chat_id)
    )

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id - 1
    )

    return 'MAIN_MENU'


def set_meetuper_is_active(chat_id):
    meetuper = Meetuper.objects.get(chat_id=chat_id)
    meetuper.is_active = True
    meetuper.save()


def handle_users_reply(update, context):
    db = get_database_connection()

    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
        set_meetuper_is_active(chat_id)
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
        set_meetuper_is_active(chat_id)
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id)

    states_functions = {
        'START': start,
        'CONFIRM_MENU': confirm_menu_handler,
        'WAIT_EMAIL': wait_email_handler,
        'MAIN_MENU': main_menu_handler,
        'COMMUNICATION_MENU': communication_menu_handler,
        'MEETUP_DESCRIPTION_MENU': meetup_description_menu_handler,
        'DONATE': start_without_shipping,
        'STAGE': stage_handler,
        'BLOCK': block_handler,
        'QUESTIONS': question_list_handler,
        'ASK_QUESTION': questions_handler,
        'QUESTION': question_handler,
        'SAVE_QUESTION': save_question_handler,
        'SPEAKERS_BLOCK': speakers_block_handler,
        'SPEAKERS': speakers_handler,
        'CHAT': chat_handler,
        'FIRSTNAME': firstname_handler,
        'LASTNAME': lastname_handler,
        'ORGANIZATION': organization_handler,
        'POSITION': position_handler,
        'PHONENUMBER': phonenumber_handler,
        'EMAIL': email_handler,
        'SIGNUP': signup_handler,
    }
    print(user_state)
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

    updater = Updater(tg_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
    dispatcher.add_handler(MessageHandler(Filters.document, cv_handler))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
