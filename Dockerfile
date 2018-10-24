FROM python:3.6.4
COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt
