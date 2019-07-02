import os
import nighres
import dask.bag as db
from abc import ABC, abstractmethod


class Pipeline(ABC):
    """Create a neuroimaging pipeline using Dask."""

    # Location of the output
    OUTPUT_DIR = 'data/output/'

    def __init__(self, subjects, split=True, save_data=True, overwrite=False):
        self.subjects = subjects
        self.split = split
        self.save_data = save_data
        self.overwrite = overwrite
        self.bag = db.from_sequence(self.subjects)

    @abstractmethod
    def combine(self, subject):
        """ Combine all steps in this pipeline.

        :param subject: dictionary of image objects or file names and subject id
        :return: (tissue_classified_images, subject_id)
        """
        return None

    def compute(self):
        return self.bag.compute()


class Classification(Pipeline):
    """Create a brain tissue classification pipeline using Dask."""

    def __init__(self, subjects, split=True, save_data=True, overwrite=False):
        """Constructor to init pipelines.

        :param save_data: save data to file or not
        :param overwrite: overwrite existing files or not
        """

        Pipeline.__init__(self, subjects, split, save_data, overwrite)

        if split:
            self.bag = self.bag.map(self.skull_stripping) \
                .map(self.segmentation)

        else:
            self.bag = self.bag.map(lambda subject: self.combine(subject))

    def skull_stripping(self, subject_data):
        """ Call to nighres.skull_stripping function.

        :param subject_data: dictionary of image objects or file names and subject id
        :return: {
            'images': skullstripping_results,
            'subject_id': subject_id
        }
        """

        subject = subject_data['images']
        subject_id = subject_data['subject_id']

        classification_out_dir = os.path.join(os.getcwd(),
                                              '{0}{1}/tissue_classification'.format(self.OUTPUT_DIR, subject_id))
        skullstripping_results = nighres.brain.mp2rage_skullstripping(
            second_inversion=subject['inv2'],
            t1_weighted=subject['t1w'],
            t1_map=subject['t1map'],
            save_data=self.save_data,
            overwrite=self.overwrite,
            file_name=subject_id,
            output_dir=classification_out_dir)

        return {
            'images': skullstripping_results,
            'subject_id': subject_id
        }

    def segmentation(self, stripped_output):
        """Call to nighres.mgdm_segmentation function.

        :param stripped_output: dictionary of skull stripped images or file names and subject id
        :return: {
            'images': mgdm_results,
            'subject_id': subject_id
        }
        """

        stripped_img = stripped_output['images']
        subject_id = stripped_output['subject_id']

        classification_out_dir = os.path.join(os.getcwd(),
                                              '{0}{1}/tissue_classification'.format(self.OUTPUT_DIR, subject_id))
        mgdm_results = nighres.brain.mgdm_segmentation(
            contrast_image1=stripped_img['t1w_masked'],
            contrast_type1="Mp2rage7T",
            contrast_image2=stripped_img['t1map_masked'],
            contrast_type2="T1map7T",
            save_data=self.save_data,
            overwrite=self.overwrite,
            file_name=subject_id,
            output_dir=classification_out_dir)

        # Return file name instead of objects to make it available input of extracting brain region
        if not isinstance(mgdm_results['segmentation'], str):
            image_files = {
                'segmentation': mgdm_results['segmentation'].get_filename(),
                'labels': mgdm_results['labels'].get_filename(),
                'memberships': mgdm_results['memberships'].get_filename(),
                'distance': mgdm_results['distance'].get_filename()
            }
        else:
            image_files = mgdm_results

        return {
            'images': image_files,
            'subject_id': subject_id
        }

    def combine(self, subject):

        subject_id = subject['subject_id']

        skullstripping_output = self.skull_stripping(subject)
        mgdm_result = self.segmentation(skullstripping_output)

        return {
            'images': mgdm_result,
            'subject_id': subject_id
        }


class CortexDepthEst(Classification):
    """Create a cortex depth estimation pipeline using Dask."""

    def __init__(self, subjects, split=True, save_data=True, overwrite=False):
        Classification.__init__(self, subjects, split, save_data, overwrite)

        # Init dask.bag
        if split:
            self.bag = self.bag.map(self.extract_region) \
                .map(self.cruise_extraction) \
                .map(self.volumetric_layering)

        else:
            self.bag = self.bag.map(self.combine)
        pass

    def extract_region(self, classified_data):
        """Call to nighres.extract_brain_region function.

        :param classified_data: dictionary of classification output images or file names and subject id
        :return: {
            'images': cortex,
            'subject_id': subject_id
        }
        """

        classified_tissue = classified_data["images"]
        subject_id = classified_data["subject_id"]

        segmentation = classified_tissue['segmentation']
        boundary_dist = classified_tissue['distance']
        max_labels = classified_tissue['labels']
        max_probas = classified_tissue['memberships']

        if not (os.path.isfile(segmentation) and os.path.isfile(boundary_dist)
                and os.path.isfile(max_labels) and os.path.isfile(max_probas)):
            print('This example builds upon the example_tissue_segmentation.py one')
            print('Please run it first')
            exit()

        cortex_depth_out_dir = os.path.join(os.getcwd(),
                                            '{0}{1}/cortical_depth_estimation'.format(self.OUTPUT_DIR, subject_id))
        cortex = nighres.brain.extract_brain_region(segmentation=segmentation,
                                                    levelset_boundary=boundary_dist,
                                                    maximum_membership=max_probas,
                                                    maximum_label=max_labels,
                                                    extracted_region='left_cerebrum',
                                                    save_data=self.save_data,
                                                    overwrite=self.overwrite,
                                                    file_name='{0}_left_cerebrum'.format(subject_id),
                                                    output_dir=cortex_depth_out_dir)

        return {
            'images': cortex,
            'subject_id': subject_id
        }

    def cruise_extraction(self, cortex_output):
        """Call to nighres.cruise_cortex_extraction function.

        :param cortex_output: dictionary of extracting brain region output images or file names and subject id
        :return: {
            'images': cruise,
            'subject_id': subject_id
        }
        """

        cortex = cortex_output["images"]
        subject_id = cortex_output["subject_id"]

        cortex_depth_out_dir = os.path.join(os.getcwd(),
                                            '{0}{1}/cortical_depth_estimation'.format(self.OUTPUT_DIR, subject_id))

        cruise = nighres.cortex.cruise_cortex_extraction(
            init_image=cortex['inside_mask'],
            wm_image=cortex['inside_proba'],
            gm_image=cortex['region_proba'],
            csf_image=cortex['background_proba'],
            normalize_probabilities=True,
            save_data=self.save_data,
            overwrite=self.overwrite,
            file_name="{0}_left_cerebrum".format(subject_id),
            output_dir=cortex_depth_out_dir)

        return {
            'images': cruise,
            'subject_id': subject_id
        }

    def volumetric_layering(self, cruise_output):
        """Call to nighres.volumetric_layering function.

        :param cruise_output: dictionary of cruise extraction output images or file names and subject id
        :return: {
            'images': depth,
            'subject_id': subject_id
        }
        """

        cruise = cruise_output["images"]
        subject_id = cruise_output["subject_id"]

        cortex_depth_out_dir = os.path.join(os.getcwd(),
                                            '{0}{1}/cortical_depth_estimation'.format(self.OUTPUT_DIR, subject_id))

        depth = nighres.laminar.volumetric_layering(
            inner_levelset=cruise['gwb'],
            outer_levelset=cruise['cgb'],
            n_layers=4,
            save_data=self.save_data,
            overwrite=self.overwrite,
            file_name="{0}_left_cerebrum".format(subject_id),
            output_dir=cortex_depth_out_dir)

        return {
            'images': depth,
            'subject_id': subject_id
        }

    def combine(self, classified_tissue):

        cortex = self.extract_region(classified_tissue)
        cruise = self.cruise_extraction(cortex)
        depth = self.volumetric_layering(cruise)

        return {
            'images': depth,
            'subject_id': classified_tissue['subject_id']
        }
