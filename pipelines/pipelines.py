import os
import nighres
import dask
import dask.bag as db
import dask.delayed as delayed
from abc import ABC, abstractmethod


class Pipeline(ABC):
    """Create a neuroimaging pipeline using Dask."""

    # Location of the output
    OUTPUT_DIR = 'data/output/'

    def __init__(self, subjects, split=True, save_data=True, overwrite=False, return_filename=True):
        self.subjects = subjects
        self.split = split
        self.save_data = save_data
        self.overwrite = overwrite
        self.return_filename = return_filename
        self.bag = db.from_sequence(self.subjects)
        self.delays = {}

    @abstractmethod
    def combine(self, subject, subject_id):
        """ Combine all steps in this pipeline.

        :param subject: subject image object or file names
        :param subject_id: id of the subject, used for tracking
        :param save_data: save data to file or not
        :param overwrite: overwrite existing files or not
        :param return_filename: True if return file names instead of objects
        :return: (tissue_classified_images, subject_id)
        """
        return None

    def compute_bag(self):
        return self.bag.compute()

    def compute_delayed(self):
        delays = self.delays.values()
        return dask.compute(*delays)


class Classification(Pipeline):
    """Create a brain tissue classification pipeline using Dask."""

    def __init__(self, subjects, split=True, save_data=True, overwrite=False, return_filename=True):

        Pipeline.__init__(self, subjects, split, save_data, overwrite, return_filename)

        # Init dask.delayed
        for subject in subjects:
            subject_id = subject['subject_id']

            stripping = delayed(self.skull_stripping)(subject, subject_id)
            segmented = delayed(self.segmentation)(stripping, subject_id)
            self.delays[subject_id] = segmented

        # Init dask.bag
        if split:
            self.bag = self.bag.map(lambda subject: self.skull_stripping(subject, subject['subject_id'])) \
                .map(lambda result: self.segmentation(result[0], result[1]))

        else:
            self.bag = self.bag.map(lambda subject: self.combine(subject, subject['subject_id']))

    def skull_stripping(self, subject, subject_id):
        """ Call to nighres.skull_stripping function.

        :param subject: subject image object or file names
        :param subject_id: id of the subject, used for tracking
        :return: (skull_stripped_images, subject_id)
        """
        classification_out_dir = os.path.join(os.getcwd(),
                                              '{0}{1}/tissue_classification'.format(self.OUTPUT_DIR, subject_id))
        skullstripping_results = nighres.brain.mp2rage_skullstripping(
            second_inversion=subject['inv2'],
            t1_weighted=subject['t1w'],
            t1_map=subject['t1map'],
            save_data=self.save_data,
            overwrite=self.overwrite,
            file_name=subject_id,
            output_dir=classification_out_dir,
            return_filename=self.return_filename)

        return skullstripping_results, subject_id

    def segmentation(self, stripped_img, subject_id):
        """Call to nighres.mgdm_segmentation function.

        :param stripped_img: subject image object or file names
        :param subject_id: id of the subject, used for tracking
        :return: (tissue_classified_images, subject_id)
        """
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
            output_dir=classification_out_dir,
            return_filename=self.return_filename)

        return mgdm_results, subject_id

    def combine(self, subject, subject_id):
        skullstripping_result = self.skull_stripping(subject, subject_id)
        mgdm_result = self.segmentation(skullstripping_result)

        return mgdm_result, subject_id


class CortexDepthEst(Classification):
    """Create a cortex depth estimation pipeline using Dask."""

    def __init__(self, subjects, split=True, save_data=True, overwrite=False, return_filename=True):
        Classification.__init__(self, subjects, split, save_data, overwrite, return_filename)

        # Init dask.delayed
        for subject in subjects:
            subject_id = subject['subject_id']

            classified = self.delays[subject_id]
            cortex = delayed(self.extract_region)(classified, subject_id)
            cruise = delayed(self.cruise_extraction)(cortex, subject_id)
            depth_est = delayed(self.volumetric_layering)(cruise, subject_id)
            self.delays[subject_id] = depth_est

        # Init dask.bag
        if split:
            self.bag = self.bag.map(lambda result: self.extract_region(result[0], result[1])) \
                .map(lambda result: self.cruise_extraction(result[0], result[1])) \
                .map(lambda result: self.volumetric_layering(result[0], result[1]))

        else:
            self.bag = self.bag.map(lambda subject: self.combine(subject, subject['subject_id']))
        pass

    def extract_region(self, classified_tissue, subject_id):
        """Call to nighres.extract_brain_region function.

        :param classified_tissue: tissue classification output
        :param subject_id: id of the subject, used for tracking
        :return: (cortex_images, subject_id)
        """

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

        return cortex, subject_id

    def cruise_extraction(self, cortex, subject_id):
        """Call to nighres.cruise_cortex_extraction function.

        :param cortex: extracted cortex images
        :param subject_id: id of the subject, used for tracking
        :return: (cruise_images, subject_id)
        """
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

        return cruise, subject_id

    def volumetric_layering(self, cruise, subject_id):
        """Call to nighres.volumetric_layering function.

        :param cruise: extracted cortex images
        :param subject_id: id of the subject, used for tracking
        :return: (depth_estimation_images, subject_id)
        """
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

        return depth

    def combine(self, classified_tissue, subject_id):
        cortex = self.extract_region(classified_tissue, subject_id)
        cruise = self.cruise_extraction(cortex, subject_id)
        depth = self.volumetric_layering(cruise, subject_id)

        return depth, subject_id
