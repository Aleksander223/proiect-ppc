FROM ubuntu:20.04
WORKDIR /app
COPY . /app
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y python3 && apt-get install -y python3-pip
RUN apt-get install -y vim
RUN pip3 install pika
CMD ["python3", "worker.py"]