FROM nighres

USER root

COPY pipelines /home/neuro/pipelines
COPY run.py /home/neuro
COPY data /home/neuro/data

RUN python3 -m pip install dask && \
    cd /home/neuro && \
    chmod 755 /home/neuro/data && \
    chown -R neuro /home/neuro/data

USER neuro