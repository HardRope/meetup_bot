from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Meetuper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.CharField('место работы', max_length=255)
    position = models.CharField('должность', max_length=255)
    is_open_for_communication = models.BooleanField(
        'открыт к общению',
        default=False
    )

    def __str__(self):
        return f'{self.user.username}'

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
        return f'{self.participant.user.username}'

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
    title = models.CharField('название этапа', max_length=255)
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
            \n{self.speaker.partisipant.user.username}
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
            Вопрос от {self.meetuper.user.username} к {self.speaker.partisipant.user.username}
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
        return f'Донат от {self.meetuper.user.username}'

    class Meta:
        verbose_name = 'Донат'
        verbose_name_plural = 'Донаты'
