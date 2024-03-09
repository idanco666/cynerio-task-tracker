FROM python:3.10
ENV NAME=tests
ENV HOME=/home/app/$NAME

RUN mkdir -p $HOME
RUN mkdir -p $HOME/common

WORKDIR $HOME

RUN pip install --upgrade pip

COPY ./$NAME $HOME
COPY ./common $HOME/common

RUN pip install -r requirements.txt

CMD ["pytest"]
