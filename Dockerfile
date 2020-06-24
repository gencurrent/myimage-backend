FROM python:3.7-alpine

RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add jpeg-dev zlib-dev libjpeg
RUN apk add libffi-dev

RUN mkdir /src
WORKDIR /src

ADD requirements.txt /src/
RUN pip install -r requirements.txt

COPY . /src/


RUN mkdir -p /shared/nginx/static
RUN mkdir -p /shared/nginx/media
RUN mkdir -p /shared/nginx/public

CMD ./wait_for_depends.sh --debug