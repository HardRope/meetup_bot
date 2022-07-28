from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Meetuper(models.Model):
    firstname = models.CharField(
        'имя участника',
        max_length=255,
        blank=True,
        default=''
    )
    lastname = models.CharField(
        'фамилия участника',
        max_length=255,
        blank=True,
        default=''
    )
    email = models.EmailField(
        'email участника',
        blank=True,
        default=''
    )
    phone_number = PhoneNumberField(
        'номер телефона',
        blank=True,
        null=True
    )
    organization = models.CharField(
        'место работы',
        max_length=255,
        blank=True,
        default=''
    )
    position = models.CharField(
        'должность',
        max_length=255,
        blank=True,
        default=''
    )
    chat_id = models.PositiveIntegerField(
        verbose_name='чат-id участника в Telegram',
        primary_key=True
    )
    is_open_for_communication = models.BooleanField(
        'открыт к общению',
        default=False
    )

    def __str__(self):
        return f'{self.chat_id}: {self.firstname} {self.lastname}'

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'


class Speaker(models.Model):
    participant = models.OneToOneField(Meetuper, on_delete=models.CASCADE)
    is_active = models.BooleanField(
        'является спикером на сегодня',
        default=False,
        db_index=True
    )

    def __str__(self):
        return f'''
            Спикер {self.participant.firstname} {self.participant.lastname}
        '''

    class Meta:
        verbose_name = 'Спикер'
        verbose_name_plural = 'Спикеры'


class MeetupProgram(models.Model):
    title = models.CharField('название мероприятия', max_length=255)
    date = models.DateField('дата мероприятия', db_index=True)
    start_time = models.TimeField('время начала мероприятия')
    end_time = models.TimeField('время завершения мероприятия')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'


class Stage(models.Model):
    title = models.CharField('название этапа', max_length=255)
    program = models.ForeignKey(
        MeetupProgram,
        on_delete=models.CASCADE,
        related_name='stages',
        db_index=True
    )
    start_time = models.TimeField('время начала этапа')
    end_time = models.TimeField('время завершения этапа')

    def __str__(self):
        return f'''
            {self.title}
            \nС {self.start_time} по {self.end_time}
        '''

    class Meta:
        verbose_name = 'Этап'
        verbose_name_plural = 'Этапы'


class Block(models.Model):
    title = models.CharField('название блока', max_length=255)
    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name='blocks',
        db_index=True
    )
    start_time = models.TimeField('время начала блока')
    end_time = models.TimeField('время завершения блока')

    def __str__(self):
        return f'''
            {self.start_time}
            \n{self.title}
        '''

    class Meta:
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'


class Event(models.Model):
    title = models.CharField('название события', max_length=255)
    speaker = models.ForeignKey(
        Speaker,
        on_delete=models.CASCADE,
        related_name='presentations',
        blank=True,
        null=True,
        db_index=True
    )
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE,
        related_name='events'
    )
    start_time = models.TimeField('время начала события')
    end_time = models.TimeField('время завершения события')
    is_active = models.BooleanField(
        'текущее событие',
        default=False,
        db_index=True
    ) 

    def __str__(self):
        return f'''
            {self.start_time} - {self.end_time}
            \n{self.title}
        '''

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'


class Question(models.Model):
    text = models.TextField('текст вопроса')
    speaker = models.ForeignKey(
        Speaker,
        on_delete=models.PROTECT,
        related_name='received_questions',
        db_index=True
    )
    meetuper = models.ForeignKey(
        Meetuper,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    date = models.DateField(
        'дата вопроса',
        auto_now=True,
        db_index=True
    )
    is_answered = models.BooleanField(
        'ответ отправлен',
        default=False,
        db_index=True
    )

    def __str__(self):
        return f'''
            Вопрос от {self.meetuper.lastname} к {self.speaker.participant.lastname}
        '''

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Donation(models.Model):
    meetuper = models.ForeignKey(
        Meetuper,
        on_delete=models.PROTECT,
        related_name='donations'
    )
    date = models.DateField('дата доната', auto_now=True)
    amount = models.PositiveSmallIntegerField('сумма доната в рублях')
    
    def __str__(self):
        return f'Донат от {self.meetuper.firstname} {self.meetuper.lastname}'

    class Meta:
        verbose_name = 'Донат'
        verbose_name_plural = 'Донаты'
