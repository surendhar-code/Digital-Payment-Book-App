FROM python:3.7.6-alpine
WORKDIR /app
ADD . /app

RUN set -e; \
        apk add --no-cache --virtual .build-deps \
                gcc \
                libc-dev \
                linux-headers \
                mariadb-dev \
                python3-dev \
                postgresql-dev \
				libffi-dev \
				openssl-dev \
        ;

COPY requirements.txt /app
RUN pip install -r requirements.txt
CMD ["python","paymentbook.py"]