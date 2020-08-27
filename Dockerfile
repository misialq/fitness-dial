FROM python:3.8

ARG user_name=app_user
ARG user_group=app_group
ENV SITE_DIR=/app

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update && apt-get install -y netcat
RUN pip install pipenv uwsgi

# create user
RUN groupadd -r $user_group
RUN useradd -g $user_group -d /home/ubuntu -ms /bin/bash $user_name

# create a directory for the app with the right ownership and set working directory there
RUN install -g $user_group -o $user_name -d ${SITE_DIR}
WORKDIR ${SITE_DIR}

# set sticky permissions for the group
RUN find ${SITE_DIR} -type d -exec chmod g+s {} \;
RUN chmod -R g+w ${SITE_DIR}


COPY Pipfile /Pipfile
COPY Pipfile.lock /Pipfile.lock
RUN pipenv install --system --deploy

COPY withconn/ ${SITE_DIR}
COPY runner.sh ${SITE_DIR}/runner.sh

# set file ownership to the user and grant x permissions to the entrypoint
RUN chown -R $user_name:$user_group .
RUN chmod u+x runner.sh

# switch to the new user
USER $user_name

EXPOSE 8000

# Add any static environment variables needed by Django or your settings file here:
#ENV DJANGO_SETTINGS_MODULE='withconn.settings.dev'

# run entrypoint.sh
#ENTRYPOINT ["/withconn/entrypoint.sh"]
ENTRYPOINT [ "/app/runner.sh" ]