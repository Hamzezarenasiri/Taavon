# STAGE 0: base image
FROM python:3.11.8-slim

USER ${USER}

WORKDIR /var/www


RUN apt-get update \
&& apt-get install git gcc musl-dev python3-dev libffi-dev openssl libjpeg-dev zlib1g-dev libmagic1 -y \
&& apt-get clean


COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

#CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "src.main.main:src", "--reload"]
