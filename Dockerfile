FROM python:3.11

WORKDIR /myweb-api

COPY requirements.txt .
COPY ./src ./src
COPY ./templates ./templates
COPY ./static ./static


RUN pip install -r requirements.txt

CMD ["python", "./src/main.py"]