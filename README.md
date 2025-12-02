# CNED scenario

[[_TOC_]]

## Requirements

- python >= 3.7

## Installation conda env

``` python
conda create -n cned-scenario python=3.7
conda activate cned-scenario
cd bin/
pip install -r requirements.txt
```

## Run scenario

### On local machine

**Note**: You should be in the root of the project

``` bash
conda activate cned-scenario
nextflow run main.nf
```

### With docker

1. Build the Docker image

``` bash
cd bin/
docker build -t cned-scenario:latest .
docker images | grep cned-scenario
cned-scenario     latest      9cdc71c25edf   26 hours ago    1.09GB
```

2. Run nextflow


**Note**: You should be in the root of the project
``` bash
nextflow -c nextflow_docker.config run main.nf
```

### Use switchable algorithms with the sandbox

Read the doc [here](docs/sandbox.md)

## TODO

- Add first step to gather results from xAPI LRS
- Add switchable algorithm (example welcomes)
