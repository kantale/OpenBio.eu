FROM python:3.8.11-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y curl wget unzip && \
    apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN (cd app/static/app && python get_bash_commands.py | bash)

EXPOSE 8200

CMD ./start.sh
