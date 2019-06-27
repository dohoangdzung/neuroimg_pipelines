import os
import nighres
from dask.diagnostics import Profiler, ResourceProfiler, CacheProfiler, visualize
from pipelines.pipelines import Classification, CortexDepthEst

DATA_DIR = 'data/data_sets/'


def get_nighres_subject_data(subject_id):
    in_dir = os.path.join(os.getcwd(), '{0}{1}/'.format(DATA_DIR, subject_id))
    result = nighres.data.download_7T_TRT(in_dir, subject_id=subject_id)
    result['subject_id'] = subject_id
    return result


def get_data():
    dataset = [get_nighres_subject_data('sub001_sess1')]
    return dataset


subjects = ['sub001_sess1', 'sub002_sess1', 'sub003_sess1']

pipeline = Classification(get_data())
with Profiler() as prof, ResourceProfiler(dt=0.5) as rprof, CacheProfiler() as cprof:
    result = pipeline.compute_bag()
visualize([prof, rprof, cprof])
