import math
import png
import shutil

from benchmark import *
from benchmark_middlebury2014 import *
from util import *


class HCI2016(Benchmark):
    def Name(self):
        return "HCI Stereo Geometry Challenge 2016"
    
    
    def Prefix(self):
        return "HCI2016_"
    
    
    def Website(self):
        return 'http://hci-benchmark.org/challenges?hc=stereo_geometry'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return True
    
    
    def GetOptions(self):
        return  # No options
    
    
    def DownloadAndConvert(self, archive_dir_path, unpack_dir_path, datasets_dir_path, training_dir_path, test_dir_path):
        # NOTE(Thomas): Is it fine to hard-code this URL, or should we use the website's API to find it out based on the challenge ID?
        DownloadAndUnzipFile('http://hci-benchmark.org/media/usercontent/iz/z8/JQ/Ib/nT/OV/Dm/hb/geometry_challenge_stereo.zip', archive_dir_path, unpack_dir_path)
        
        self.ConvertOriginalToMiddlebury(unpack_dir_path, training_dir_path, test_dir_path)
    
    
    def ConvertOriginalToMiddlebury(self, unpack_dir_path, training_dir_path, test_dir_path):
        benchmark_dir = os.path.join(unpack_dir_path, 'geometry_challenge_stereo')
        
        # Determine a list of training filenames
        gt_disparity_maps_path = os.path.join(benchmark_dir, 'demo_data', 'gt_disparity_maps')
        training_dataset_names = [filename[:filename.rfind('.')] for filename in os.listdir(gt_disparity_maps_path)]
        
        # Iterate over all datasets
        input_left_path = os.path.join(benchmark_dir, 'test_data', 'input_left')
        input_right_path = os.path.join(benchmark_dir, 'test_data', 'input_right')
        
        for image_filename in os.listdir(input_left_path):
            dataset_name = image_filename[:image_filename.rfind('.')]
            is_training_dataset = dataset_name in training_dataset_names
            
            output_dataset_path = os.path.join(training_dir_path if is_training_dataset else test_dir_path, self.Prefix() + dataset_name)
            MakeDirsExistOk(output_dataset_path)
            
            # Move images
            shutil.move(os.path.join(input_left_path, image_filename),
                        os.path.join(output_dataset_path, 'im0.png'))
            shutil.move(os.path.join(input_right_path, image_filename),
                        os.path.join(output_dataset_path, 'im1.png'))
            
            # Create calib.txt
            left_fx = -1  # TODO
            left_fy = -1  # TODO
            left_cx = -1  # TODO
            left_cy = -1  # TODO
            right_fx = -1  # TODO
            right_fy = -1  # TODO
            right_cx = -1  # TODO
            right_cy = -1  # TODO
            baseline_in_mm = -1  # TODO
            
            png_reader = png.Reader(os.path.join(output_dataset_path, 'im0.png'))
            png_data = png_reader.read()
            width = png_data[0]
            height = png_data[1]
            png_reader.close()
            
            ndisp = 160  # According to HCI's challenge README
            
            calib_path = os.path.join(output_dataset_path, 'calib.txt')
            WriteMiddlebury2014CalibFile(
                calib_path,
                left_fx, left_fy, left_cx, left_cy,
                right_fx, right_fy, right_cx, right_cy,
                baseline_in_mm,
                width,
                height,
                ndisp)
            
            # Move masks file
            shutil.move(os.path.join(benchmark_dir, 'test_data', 'masks', dataset_name + '.png'),
                        os.path.join(output_dataset_path, 'mask.png'))
            
            # For training datasets:
            if is_training_dataset:
                # Convert ground truth.
                # While HCI already provides the ground truth as .pfm files,
                # it uses NAN for invalid values while Middlebury uses INF.
                (pfm_width, pfm_height, pfm_pixels) = ReadMiddlebury2014PfmFile(os.path.join(gt_disparity_maps_path, dataset_name + '.pfm'))
                converted_pixels = []
                for pixel in pfm_pixels:
                    if math.isnan(pixel):
                        converted_pixels.append(float('inf'))
                    else:
                        converted_pixels.append(pixel)
                WriteMiddlebury2014PfmFile(os.path.join(output_dataset_path, 'disp0GT.pfm'), pfm_width, pfm_height, converted_pixels)
                
                # Move additional files
                shutil.move(os.path.join(benchmark_dir, 'demo_data', 'gt_sample_count', dataset_name + '.pfm'),
                            os.path.join(output_dataset_path, 'gt_sample_count.pfm'))
                shutil.move(os.path.join(benchmark_dir, 'demo_data', 'gt_uncertainty', dataset_name + '.pfm'),
                            os.path.join(output_dataset_path, 'gt_uncertainty.pfm'))
                shutil.move(os.path.join(benchmark_dir, 'demo_data', 'masks_dynamic_objects', dataset_name + '.png'),
                            os.path.join(output_dataset_path, 'mask_dynamic_objects.png'))
                shutil.move(os.path.join(benchmark_dir, 'demo_data', 'masks_eval', dataset_name + '.png'),
                            os.path.join(output_dataset_path, 'mask_eval.png'))
        
        # Delete original folders
        shutil.rmtree(benchmark_dir)
    
    
    def CreateSubmissionArchive(self, method, datasets_dir_path, training_dataset_names, test_dataset_names, training_dir_path, test_dir_path, pack_dir_path, archive_base_path):
        # TODO: Support confidence, code, and publication submission
        # From the README:
        # FILE STRUCTURE:
        # your_algo_name/disp_maps/geometry_00.pfm
        # your_algo_name/runtimes/geometry_00.txt
        # your_algo_name/confidence/geometry_00.pfm (OPTIONAL)
        # your_algo_name/code/* (OPTIONAL)
        # your_algo_name/publication/* (OPTIONAL)
        
        # Create output directories
        disp_maps_path = os.path.join(pack_dir_path, method, 'disp_maps')
        MakeDirsExistOk(disp_maps_path)
        runtimes_path = os.path.join(pack_dir_path, method, 'runtimes')
        MakeDirsExistOk(runtimes_path)
        
        # Handle training and test datasets in the same way.
        for item in ([(name, True) for name in training_dataset_names] +
                     [(name, False) for name in test_dataset_names]):
            benchmark_and_dataset_name = item[0]
            is_training = item[1]
            
            src_dataset_path = os.path.join(training_dir_path if is_training else test_dir_path, benchmark_and_dataset_name)
            original_dataset_name = benchmark_and_dataset_name[len(self.Prefix()):]
            
            # Copy .pfm file
            shutil.copy2(os.path.join(src_dataset_path, 'disp0' + method + '.pfm'),
                         os.path.join(disp_maps_path, original_dataset_name + '.pfm'))
            
            # Copy time file
            shutil.copy2(os.path.join(src_dataset_path, 'time' + method + '.txt'),
                         os.path.join(runtimes_path, original_dataset_name + '.txt'))
        
        # Create the archive and clean up.
        archive_filename = ZipDirectory(archive_base_path, pack_dir_path)
        DeleteFolderContents(pack_dir_path)
        
        return archive_filename
    
