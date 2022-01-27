# proiect-ppc

Requirements:
```sh
$ apt install rabbitmq-server
``` 

Usage:
```sh
$ # start the rabbitmq server
$ service rabbitmq-server start/enable/restart
$ # build the worker image
$ docker build -f Dockerfile . -t worker:1
$ # start your worker (you can define as many as you want in docker-compose file)
$ docker-compose up -d
```
