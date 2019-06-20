import os
import pipelines.tissue_classification as tc
import pipelines.cortex_depth_est as cde
import nighres
import dask.bag as db


DATA_DIR = 'data/data_sets/'
OUTPUT_DIR = 'data/output/'


def get_data(subject_id):
    in_dir = os.path.join(os.getcwd(), '{0}{1}/'.format(DATA_DIR, subject_id))
    result = nighres.data.download_7T_TRT(in_dir, subject_id=subject_id)
    result['subject_id'] = subject_id
    return result

def classify(subject, subject_id):
    classification_out_dir = os.path.join(os.getcwd(), '{0}{1}/tissue_classification'.format(OUTPUT_DIR, subject_id))
    return tc.classify(subject, subject_id, classification_out_dir), subject_id

def cortex_depth_est(classified, subject_id):
    cortex_depth_out_dir = os.path.join(os.getcwd(), '{0}{1}/cortical_depth_estimation'.format(OUTPUT_DIR, subject_id))
    return cde.estimate(classified, subject_id, cortex_depth_out_dir), subject_id


dataset = []
dataset.append(get_data('sub001_sess1'))
dataset.append(get_data('sub002_sess1'))
dataset.append(get_data('sub003_sess1'))


classification = db.from_sequence(dataset).map(lambda subject: classify(subject, subject['subject_id']))

# estimation = classification.map(lambda classified, subject_id: cortex_depth_est(classified, subject_id))
