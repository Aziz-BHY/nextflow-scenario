FROM continuumio/miniconda3:4.11.0
MAINTAINER Ben Soussia Amal <amal.ben-soussia@loria.fr>

ENV SOURCES=/cned-scenario
ENV PATH="/${SOURCES}:${PATH}"


RUN apt update && \
    apt install procps build-essential -y

COPY . ${SOURCES}
WORKDIR ${SOURCES}

RUN pip install -r requirements.txt 
