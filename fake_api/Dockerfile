FROM python:3.8

# We copy just the requirements.txt first to leverage Docker cache
WORKDIR /app

RUN pip install flask==1.1.2 pytz

COPY . /app

EXPOSE 5000

ENTRYPOINT [ "python" ]

CMD [ "/app/app.py" ]
