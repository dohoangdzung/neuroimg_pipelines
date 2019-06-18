import os
import pipelines.tissue_classification as tc
import pipelines.cortex_depth_est as cde
import nighres

dataset = []

in_dir = os.path.join(os.getcwd(), 'data_sets/')
data = nighres.data.download_7T_TRT(in_dir, subject_id='sub001_sess1')
dataset.append(data)

for subject in dataset:
    classified_result = tc.classify(subject)
    estimation = cde.estimate(classified_result)
