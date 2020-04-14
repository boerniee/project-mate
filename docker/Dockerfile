FROM python:3.6-alpine

WORKDIR /src/clubmate

COPY requirements.txt requirements.txt
COPY . ./
COPY docker/boot.sh ./

RUN pip install -r requirements.txt && \
    pip install gunicorn==19.9.0 && \
    chmod +x boot.sh

EXPOSE 5000
ENTRYPOINT ["sh", "boot.sh"]
