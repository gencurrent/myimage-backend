FROM python:3.8-alpine

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    && apk add jpeg-dev zlib-dev libjpeg 

RUN mkdir /src
WORKDIR /src

ADD requirements.txt /src/
RUN pip install -r requirements.txt

COPY . /src/

CMD ./wait_for_depends.sh --debug