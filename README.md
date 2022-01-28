# proiect-ppc

## Introduction
This app simulates a distributed weather prediction service. It uses multiple workers to distribute the requests, thus ensuring better operation. The data is taken from the open weather dataset
```noaa-gsod```, and was processed into a dataset using Google BigQuery. The data is localised to Romania.

## Technologies
* Docker
* MongoDB
* Python
* FastAPI
* Google BigQuery
* Nginx

## Requirements

* Docker

## Usage
```sh
$ docker-compose up build
$ docker-compose up
```
