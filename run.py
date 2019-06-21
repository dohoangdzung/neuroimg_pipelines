import os
import pipelines.tissue_classification as tc
import pipelines.cortex_depth_est as cde
import nighres
import dask.bag as db

DATA_DIR = 'data/data_sets/'
OUTPUT_DIR = 'data/output/'


def classify(subject, subject_id):
    classification_out_dir = os.path.join(os.getcwd(), '{0}{1}/tissue_classification'.format(OUTPUT_DIR, subject_id))
    return tc.combine(subject, subject_id, classification_out_dir), subject_id


def skull_stripping(subject, subject_id):
    classification_out_dir = os.path.join(os.getcwd(), '{0}{1}/tissue_classification'.format(OUTPUT_DIR, subject_id))
    return tc.skull_stripping(subject, subject_id, classification_out_dir), subject_id


def segmentation(stripped, subject_id):
    classification_out_dir = os.path.join(os.getcwd(), '{0}{1}/tissue_classification'.format(OUTPUT_DIR, subject_id))
    return tc.segmentation(stripped, subject_id, classification_out_dir), subject_id


def cortex_depth_est(classified, subject_id):
    cortex_depth_out_dir = os.path.join(os.getcwd(), '{0}{1}/cortical_depth_estimation'.format(OUTPUT_DIR, subject_id))
    return cde.combine(classified, subject_id, cortex_depth_out_dir), subject_id


def extract_region(classified, subject_id):
    cortex_depth_out_dir = os.path.join(os.getcwd(), '{0}{1}/cortical_depth_estimation'.format(OUTPUT_DIR, subject_id))
    return cde.extract_region(classified, subject_id, cortex_depth_out_dir), subject_id


def cruise_extraction(cortex, subject_id):
    cortex_depth_out_dir = os.path.join(os.getcwd(), '{0}{1}/cortical_depth_estimation'.format(OUTPUT_DIR, subject_id))
    return cde.cruise_extraction(cortex, subject_id, cortex_depth_out_dir), subject_id


def volumetric_layering(cruise, subject_id):
    cortex_depth_out_dir = os.path.join(os.getcwd(), '{0}{1}/cortical_depth_estimation'.format(OUTPUT_DIR, subject_id))
    return cde.volumetric_layering(cruise, subject_id, cortex_depth_out_dir), subject_id


def get_nighres_subject_data(subject_id):
    in_dir = os.path.join(os.getcwd(), '{0}{1}/'.format(DATA_DIR, subject_id))
    result = nighres.data.download_7T_TRT(in_dir, subject_id=subject_id)
    result['subject_id'] = subject_id
    return result


def get_data():
    dataset = [get_nighres_subject_data('sub001_sess1'),
               get_nighres_subject_data('sub002_sess1'),
               get_nighres_subject_data('sub003_sess1')]

    return dataset


subjects = ['sub001_sess1', 'sub002_sess1', 'sub003_sess1']

classification = db.from_sequence(get_data()) \
    .map(lambda subject: skull_stripping(subject, subject['subject_id'])) \
    .map(lambda tuple: segmentation(tuple[0], tuple[1]))

# estimation = classification \
#     .map(lambda tuple: extract_region(tuple[0], tuple[1])) \
#     .map(lambda tuple: cruise_extraction(tuple[0], tuple[1])) \
#     .map(lambda tuple: volumetric_layering(tuple[0], tuple[1]))

