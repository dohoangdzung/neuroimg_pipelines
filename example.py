import os
import nighres
from pipelines.pipelines import Classification, CortexDepthEst

DATA_DIR = 'data/data_sets/'


def get_nighres_subject_data(subject_id):
    in_dir = os.path.join(os.getcwd(), '{0}{1}/'.format(DATA_DIR, subject_id))
    result = nighres.data.download_7T_TRT(in_dir, subject_id=subject_id)
    # result['subject_id'] = subject_id
    return {
        'images': result,
        'subject_id': subject_id
    }


def get_data():
    dataset = [get_nighres_subject_data('sub001_sess1')]
    return dataset


subjects = ['sub001_sess1', 'sub002_sess1', 'sub003_sess1']

# Create a cortex depth estimation pipeline and run with input data
pipeline = CortexDepthEst(get_data())
res = pipeline.compute()
