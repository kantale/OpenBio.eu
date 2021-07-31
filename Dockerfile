FROM python:3.8.11-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y curl wget unzip nodejs npm && \
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

RUN npm install --prefix /app/static/app && \
    npm run get-material-icons --prefix /app/static/app && \
    npm run fix-ace --prefix /app/static/app 

RUN pip install -r requirements.txt

EXPOSE 8200

CMD ./start.sh
