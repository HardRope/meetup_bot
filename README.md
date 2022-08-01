# Meetup_bot

This bot helps to organize some meetups and makes easier interaction between organizer,
speakers and guests of it.

List of possibilities for different sides of meetup:
 1. Guests

  - Look the meetup timetable
  - Ask the speaker a question
  - Communicate with other guests of meetup
  - Donate for help to organize next meetups
  - Sign up to the next meetup
  - Sign up to the next meetup as speaker

 2. Speaker

  - All guests possibilities
  - See list of guests questions

 3. Organizer

  - Change information, timetables and other data of meetup
  - Send notification about changes to meetup's guests and speakers
  - Check donates statistic 

## install app
 1. Clone repository:

```commandline
git clone https://github.com/permsky/meetup_bot
```

 2. Install requirements:

```commandline
pip install -r requirements.txt
```

 4. Make migrations:

```commandline
python3 manage.py makemigrations
python3 manage.py makemigrations meetup

python3 manage.py migrate
```

 5. Create `.env` and add data:

```commandline
DATABASE_HOST=redis.host
DATABASE_PORT=redis.port
DATABASE_PASSWORD=redis.password
TELEGRAM_TOKEN=telegram_bot_token
PAY_TOKEN=payment.token
SECRET_KEY=your secret key
```

 6. Create super user to django access:

```commandline
python3 manage.py createsuperuser
```
