FROM ubuntu:20.04 AS builder-image

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install --no-install-recommends -y python3.8 python3.8-dev python3.8-venv python3-pip python3-wheel build-essential libpq-dev && \
    apt-get clean && rm -Rf /var/lib/apt/lists/*

# create and activate virtual environments
# using final folder name to avoid path issues with packages
RUN python3.8 -m venv /home/appuser/venv
ENV PATH="/home/appuser/venv/bin:$PATH"

# ARG PRIVATE_TOKEN
# ENV PRIVATE_TOKEN=${PRIVATE_TOKEN}

# install requirements
COPY requirements.txt .
RUN pip3 install --upgrade pip setuptools
RUN pip3 install wheel
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt 

FROM ubuntu:20.04 as runner-image
RUN apt-get update && apt-get install --no-install-recommends -y python3.8 python3.8-venv && \
    apt-get clean && rm -Rf /var/lib/apt/lists/*

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser

COPY --from=builder-image /home/appuser/venv /home/appuser/venv

RUN mkdir /home/appuser/code
WORKDIR /home/appuser/code
COPY ./app ./app
COPY ./configs ./configs

RUN pwd && chown -R appuser ./

USER appuser

# EXPOSE 8888

# make sure all messages always reach console
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# activate virtual environment
ENV VIRTUAL_ENV=/home/appuser/venv
ENV PATH="/home/appuser/venv/bin:$PATH"

CMD ["python", "app/main.py"]
