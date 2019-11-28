FROM python:3.6-alpine

WORKDIR /src/clubmate

COPY docker/requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn==19.9.0

COPY docker/ ./
COPY boot.sh ./
RUN chmod +x boot.sh

EXPOSE 5000
ENTRYPOINT ["sh", "boot.sh"]
