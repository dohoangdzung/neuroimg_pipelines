# Replace <dzungdohoang/nighres:latest> with your Nighres docker image
FROM dzungdohoang/nighres:latest

USER root

RUN python3 -m pip install dask && \
    python3 -m pip install dask[bag] --upgrade && \
    python3 -m pip install dask distributed --upgrade

COPY pipelines /home/neuro/pipelines
COPY example.py /home/neuro
COPY example.ipynb /home/neuro

RUN cd /home/neuro

USER neuro