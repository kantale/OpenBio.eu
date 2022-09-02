FROM python:3.9.13 AS builder

RUN apt-get update && \
    apt-get install -y python-dev && \
    python -m pip wheel --wheel-dir=/tmp backports.zoneinfo==0.2.1

FROM python:3.9.13-slim

ARG TARGETARCH

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y curl wget unzip xz-utils git vim-tiny && \
    apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base
RUN if [ "$TARGETARCH" = "amd64" ]; then ARCH=x64; else ARCH=$TARGETARCH; fi && \
    curl -LO https://nodejs.org/dist/v14.17.4/node-v14.17.4-linux-${ARCH}.tar.xz && \
    tar -Jxvf node-v14.17.4-linux-${ARCH}.tar.xz -C /usr/local --strip-components=1 node-v14.17.4-linux-${ARCH}/bin node-v14.17.4-linux-${ARCH}/lib && \
    rm -rf node-v14.17.4-linux-${ARCH}.tar.xz

COPY . /app
WORKDIR /app

RUN npm install --prefix app/static/app && \
    npm run get-material-icons --prefix app/static/app && \
    npm run fix-ace --prefix app/static/app
COPY --from=builder /tmp/*.whl /tmp/
RUN pip install --upgrade pip && \
    pip install /tmp/*.whl && \
    pip install -r requirements.txt


EXPOSE 8200

CMD ./start.sh
