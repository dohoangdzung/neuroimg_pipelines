FROM nighres

USER root

RUN python3 -m pip install dask && \
    cd /home/neuro
COPY pipelines /home/neuro/pipelines

USER neuro