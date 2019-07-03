.. -*- mode: rst -*-

Neuroimaging pipelines with Nighres and Dask
=======

Dask is a Python library for parallel computing. It provides a set of big data collections that extends NumPy, Pandas
such as dask.array, dask.bag, dask.dataframe and task schedulers for computation.

https://docs.dask.org/

The source code implements some examples of neuroimaging pipelines using Dask for scheduling Nighres processing tasks.
It basically build pipelines with steps which are Nighres function calls wrapped in Dask mapping functions.
The pipelines accept multiple objects as the input for parallel computing.


Required packages
=================

In order to run the pipelines, you will need to install:

* Nighres: https://nighres.readthedocs.io/en/latest/installation.html
* Dask: https://docs.dask.org/en/latest/install.html


Docker
======

You can try quickly by running a docker image built with Jupyter Notebook.
This docker image is built based on an docker image in which Nighres is installed.
You can run with this Nighres version, or use your own Nighres docker image by replacing
<dzungdohoang/nighres:latest> on the first line of the dockerfile with your image.

To build the Docker image, do the following::

    docker build . -t pipelines

To run the Docker container::

    docker run -p 8888:8888 pipelines

Now go with your browser to https://localhost:8888 to start a notebook. You should be able
to import pipelines by entering::

    import pipelines.pipelines

into the first cell of your notebook.

Use your own data input by granting data folder access to docker image by running image with `-v` option
Then you can write your code to load the input data as the input of pipelines.::

    docker run -v /home/me/my_data:/data -p 8888:8888 pipelines
