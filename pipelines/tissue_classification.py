import nighres

def classify(subject, subject_id, out_dir, save_data=True, overwrite=False, return_filename=True):

    skullstripping_results = nighres.brain.mp2rage_skullstripping(
                                                second_inversion=subject['inv2'],
                                                t1_weighted=subject['t1w'],
                                                t1_map=subject['t1map'],
                                                save_data=save_data,
                                                overwrite=overwrite,
                                                file_name=subject_id,
                                                output_dir=out_dir,
                                                return_filename=return_filename)

    mgdm_results = nighres.brain.mgdm_segmentation(
        contrast_image1=skullstripping_results['t1w_masked'],
        contrast_type1="Mp2rage7T",
        contrast_image2=skullstripping_results['t1map_masked'],
        contrast_type2="T1map7T",
        save_data=save_data,
        overwrite=overwrite,
        file_name=subject_id,
        output_dir=out_dir,
        return_filename=return_filename)

    return mgdm_results
