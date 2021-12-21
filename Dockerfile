FROM python:3.8.11-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y curl wget unzip xz-utils git && \
    apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base
RUN curl -LO https://nodejs.org/dist/v14.17.4/node-v14.17.4-linux-x64.tar.xz && \
    tar -Jxvf node-v14.17.4-linux-x64.tar.xz -C /usr/local --strip-components=1 node-v14.17.4-linux-x64/bin node-v14.17.4-linux-x64/lib && \
    rm -rf node-v14.17.4-linux-x64.tar.xz

COPY . /app
WORKDIR /app

RUN npm install --prefix app/static/app && \
    npm run get-material-icons --prefix app/static/app && \
    npm run fix-ace --prefix app/static/app
RUN pip install -r requirements.txt

EXPOSE 8200

CMD ./start.sh
