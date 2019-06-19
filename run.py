import os
import pipelines.tissue_classification as tc
import pipelines.cortex_depth_est as cde
import nighres
import dask.bag as db


dataset = []

in_dir = os.path.join(os.getcwd(), 'data/data_sets/')
classification_out_dir = os.path.join(os.getcwd(), 'data/tissue_classification')
cortex_depth_out_dir = os.path.join(os.getcwd(), 'data/cortical_depth_estimation')

data1 = nighres.data.download_7T_TRT(in_dir, subject_id='sub001_sess1')
dataset.append(data1)

clasification = db.from_sequence(dataset).map(lambda subject: tc.classify(subject, classification_out_dir))
estimation = clasification.map(lambda classified: cde.estimate(classified, cortex_depth_out_dir))
