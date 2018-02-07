import math
import os.path as op
import png
import shutil

from benchmark import *
from dataset_format_kitti2015 import *
from util import *
from util_segmentation import *
from benchmark_cityscapes import Cityscapes


class WildDash(Cityscapes):
    def Name(self):
        return 'WildDash Instance Segmentation 2018'
    
    
    def Prefix(self):
        return 'WildDash_'
    
    
    def Website(self):
        return 'http://wilddash.cc/'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return True
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        file_path = op.join(archive_dir_path, 'wd_val_01.zip')
        expected_archives = [file_path]

        # Try to unpack input and ground truth files
        self.ExtractManualDownloadArchives(expected_archives, op.join(unpack_dir_path, self.Prefix() + 'dirs'))


    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)


    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        src_dir_path = op.join(unpack_dir_path, self.Prefix() + 'dirs', 'wd_val_01')

        # Read the image file names
        img_names = ['_'.join(f.split('_')[:2]) for f in os.listdir(src_dir_path) if
                     op.isfile(op.join(src_dir_path, f)) and f.endswith('_polygons.json')]

        for img_name in img_names:
            # Move the training image data
            shutil.move(op.join(src_dir_path, img_name + '.png'),
                        op.join(training_dir_path, 'image_2', self.Prefix() + img_name + '.png'))

            # Copy the semantic segmentation files
            shutil.copy2(op.join(src_dir_path, img_name + "_labelIds.png"),
                         op.join(training_dir_path, 'semantic', self.Prefix() + img_name + ".png"))

            # Convert the instance files to the Kitti2015 format
            src_path_cs_instance = op.join(src_dir_path, img_name + '_instanceIds.png')
            src_path_cs_semantic = op.join(src_dir_path, img_name + '_labelIds.png')
            dest_path = op.join(training_dir_path, 'instance', self.Prefix() + img_name + '.png')
            ConvertCityscapesToKittiInstances(src_path_cs_instance, src_path_cs_semantic, dest_path)

        shutil.rmtree(op.join(unpack_dir_path, self.Prefix() + 'dirs'))