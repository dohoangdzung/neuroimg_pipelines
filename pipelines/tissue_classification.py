import os
import nighres


def classify(dataset=None, overwrite=False):

    out_dir = os.path.join(os.getcwd(), 'data/tissue_classification')

    skullstripping_results = nighres.brain.mp2rage_skullstripping(
                                                second_inversion=dataset['inv2'],
                                                t1_weighted=dataset['t1w'],
                                                t1_map=dataset['t1map'],
                                                save_data=True,
                                                overwrite=overwrite,
                                                file_name='sub001_sess1',
                                                output_dir=out_dir,
                                                return_filename=True)

    mgdm_results = nighres.brain.mgdm_segmentation(
        contrast_image1=skullstripping_results['t1w_masked'],
        contrast_type1="Mp2rage7T",
        contrast_image2=skullstripping_results['t1map_masked'],
        contrast_type2="T1map7T",
        save_data=True,
        overwrite=overwrite,
        file_name="sub001_sess1",
        output_dir=out_dir,
        return_filename=True)

    return mgdm_results
