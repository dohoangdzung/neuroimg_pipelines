import nighres
import os

def estimate(classified_tissue, subject_id, out_dir, save_data=True, overwrite=False):

    segmentation = classified_tissue['segmentation']
    boundary_dist = classified_tissue['distance']
    max_labels = classified_tissue['labels']
    max_probas = classified_tissue['memberships']

    if not (os.path.isfile(segmentation) and os.path.isfile(boundary_dist)
            and os.path.isfile(max_labels) and os.path.isfile(max_probas)):
        print('This example builds upon the example_tissue_segmentation.py one')
        print('Please run it first')
        exit()

    cortex = nighres.brain.extract_brain_region(segmentation=segmentation,
                                                levelset_boundary=boundary_dist,
                                                maximum_membership=max_probas,
                                                maximum_label=max_labels,
                                                extracted_region='left_cerebrum',
                                                save_data=save_data,
                                                overwrite=overwrite,
                                                file_name='{0}_left_cerebrum'.format(subject_id),
                                                output_dir=out_dir)

    cruise = nighres.cortex.cruise_cortex_extraction(
        init_image=cortex['inside_mask'],
        wm_image=cortex['inside_proba'],
        gm_image=cortex['region_proba'],
        csf_image=cortex['background_proba'],
        normalize_probabilities=True,
        save_data=save_data,
        overwrite=overwrite,
        file_name="{0}_left_cerebrum".format(subject_id),
        output_dir=out_dir)

    depth = nighres.laminar.volumetric_layering(
        inner_levelset=cruise['gwb'],
        outer_levelset=cruise['cgb'],
        n_layers=4,
        save_data=save_data,
        overwrite=overwrite,
        file_name="{0}_left_cerebrum".format(subject_id),
        output_dir=out_dir)

    return depth
