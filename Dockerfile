FROM python:3.8.5-slim-buster

RUN mkdir /pytest/

COPY ./dev-requirements.txt /pytest/
# COPY ./setup.py ./setup.py

RUN pip install --upgrade pip
RUN pip3 install --no-cache-dir -r /pytest/dev-requirements.txt

WORKDIR /pytest/

CMD "pytest"
ENV PYTHONDONTWRITEBYTECODE=true