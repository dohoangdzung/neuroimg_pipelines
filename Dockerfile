FROM dzungdohoang/nighres:latest

USER root

RUN python3 -m pip install dask && \
    python3 -m pip install dask[bag] --upgrade &&\
    python3 -m pip install dask distributed --upgrade

COPY pipelines /home/neuro/pipelines
COPY run.py /home/neuro
COPY data /home/neuro/data

RUN cd /home/neuro && \
    chmod 755 /home/neuro/data && \
    chown -R neuro /home/neuro/data

USER neuro