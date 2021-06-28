# Fitness Dial
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![CI test](https://github.com/misialq/fitness-dial/actions/workflows/test_and_build.yaml/badge.svg)

Fitness Dial is a Django app that connects to Withings API and fetches your fitness data for most of the supported devices.
The data is stored in a PostgreSQL database and can be viewed using the provided Grafana dashboard. If exposed on the Internet,
it can also serve as a notification endpoint for receiving data notifications from Withings API. 
Additionally, it supports manual imports of nutritional data as provided by MyFtinessPal in a form of CSV files.

This is a work in progress project and all the necessary guides will be added/updated in the near future.  

## Deploy the stack
To deploy the stack as is (the DB, Django API, Celery workers, Celery flower for monitoring, 
RabbitMQ, Grafana and the "Fake Withings API") run:

`docker compose -f dc-fitness-dial-dev.yml -p fitness-dial up -d`

This will build all the required images (or pull them from the registry) and start all the containers.

The default configuration allows making "fake" request using the mock Withings API which just returns
some random data for some endpoints, rather than connecting to the actual API. If you want to use it with the real Withings API
you will need to adjust the `WITHINGS_API_URL` environment variable and point to the correct URL.

Before using though, you still need to adjust a couple of things - see below.

## RabbitMQ
1. Exec into RabbitMQ container and adjust the password for the management user in case it doesn't work.
- `docker exec -it rabbitmq /bin/bash`
- `rabbitmqctl list_users`
- `rabbitmqctl change_password <user> <new password>`
2. Create a user for the fitness-dial container (according to the values set for Celery broker in [vars-dev.env](vars-dev.env) file:
- `rabbitmqctl add_user testuser pwd123`
3. Go to [localhost:15672](http://localhost:15672), log in as the management user
4. Go to __Admin__ tab:
- select your new user in the table below
- set * permissions to __/__ virtual host

## Database
1. Exec into the __web__ container
2. Run `python manage.py migrate` to prepare the DB for first use
3. Open the interactive shell and create a user:

```shell
python manage.py shell
```

```python
from connector.models import WithingsAuthentication, APIUser
from django.utils import timezone
from datetime import timedelta
now = timezone.now()

user = APIUser(
   first_name='Test',
   last_name='User',
   email='test@user.com',
   user_id=123,
   demo=False,
   height=1.65,
   date_of_birth=now
)
user.save()

auth = WithingsAuthentication(
   access_token="faketoken", 
   refresh_token="fakerefreshtoken", 
   expires_in=360000, 
   valid_from=now, 
   valid_to=now+timedelta(seconds=360000), 
   scope=["user.metrics","user.activity"], 
   token_type="Bearer", 
   user=user, 
   demo=False, 
   expired=False
)
auth.save()
```

## Grafana dashboard

1. Create a DB user for Grafana (you can use [pgAdmin](https://www.pgadmin.org/)).
2. Grant SELECT permissions to the newly created user (you can use the Grant Wizard in pgAdmin).
3. Log in to Grafana at [localhost:3000](http://localhost:3000) using the default credentials (admin/admin) - change password when prompted.
4. Add a new PostgreSQL data source in the __Configuration__ tab and adjust the values according to the ones set via [environment variables](vars-dev.env):
    - host: `db:5432`
    - database: `test`
    - user/password: as created in step 1.
    - TLS/SSL Mode: `disable`
5. Create a new dashboard using the provided [template](grafana-dashboard.json):
    - in the Dashboards/Manage tab click on __Import__
    - select __Upload JSON file__ and select the template
    - adjust the name and folder, if desired, and __Import__
    - alternatively, you can copy the contents of the [template](grafana-dashboard.json)
    to the __Import via panel json__ field and continue as described above
      
[![Buy me a coffee](img/bmc-button.png)](https://www.buymeacoffee.com/misialq)
