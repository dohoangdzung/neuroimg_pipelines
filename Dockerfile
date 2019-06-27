FROM dzungdohoang/nighres:latest

USER root

RUN sudo apt install -y python-pydot python-pydot-ng graphviz

RUN python3 -m pip install dask && \
    python3 -m pip install dask[bag] --upgrade && \
    python3 -m pip install dask distributed --upgrade && \
    python3 -m pip install bokeh && \
    python3 -m pip install pydot graphviz

COPY pipelines /home/neuro/pipelines
COPY run.py /home/neuro

RUN cd /home/neuro

USER neuro