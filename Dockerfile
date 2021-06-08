FROM misialq/withconn:base-latest

COPY Pipfile /Pipfile
COPY Pipfile.lock /Pipfile.lock
RUN pipenv install --system --deploy

COPY dial/ ${SITE_DIR}
COPY runner.sh ${SITE_DIR}/runner.sh

# set file ownership to the user and grant x permissions to the entrypoint
RUN chown -R $user_name:$user_group .
RUN chmod u+x runner.sh

# switch to the new user
USER $user_name

EXPOSE 8000

# Add any static environment variables needed by Django or your settings file here:
#ENV DJANGO_SETTINGS_MODULE='dial.settings.dev'

# run entrypoint.sh
#ENTRYPOINT ["/dial/entrypoint.sh"]
ENTRYPOINT [ "/app/runner.sh" ]