# withings-connector

```
LDFLAGS=`echo $(pg_config --ldflags)` pipenv install psycopg2==2.8.5
```

## RabbitMQ

1. Exec into RabbitMQ container and adjust the password for the management user in case it doesn't work.
- `rabbitmqctl list_users`
- `rabbitmqctl change_password <user> <new password>`
2. Create a user for the withconn container:
- `rabbitmqctl add_user <new username> <new password>`
3. Go to [localhost:15672](http://localhost:15672), log in as the management user
4. Go to __Admin__ tab:
- select your new user in the table below
- set * permissions to __/__ virtual host

## Database

1. Exec into the __web__ container
2. Run `python manage.py migrate` to prepare the DB for first use
3. Open the interactive shell and create a user:

```
python manage.py shell

from connector.models import WithingsAuthentication
from django.utils import timezone
from datetime import timedelta
now = timezone.now()
user = WithingsAuthentication(
            access_token="faketoken", 
            refresh_token="fakerefreshtoken", 
            expires_in=360000, 
            valid_from=now, 
            valid_to=now+timedelta(seconds=360000), 
            scope=["user.metrics","user.activity"], 
            token_type="Bearer", 
            user_id=123, 
            demo=False, 
            expired=False)
user.save()
```


