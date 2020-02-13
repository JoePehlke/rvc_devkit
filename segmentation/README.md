# Robust Vision Challenge 2020 - Panoptic, Instance, and Semantic Segmentation Devkit #

## Dataset Download ##

We provide a devkit to download, extract, and convert the challenge datasets into a unified format.
However, some segmentation benchmarks require users to register and to confirm the license terms before granting access to their data.
Therefore, you need to manually download the following datasets:

Please register on [Cityscapes](https://www.cityscapes-dataset.com/login/) and download the following archives: "leftImg8bit_trainvaltest.zip" and "gtFine_trainvaltest.zip".
Similarly, signup on [WildDash](http://wilddash.cc/accounts/login?next=/download) and download the archive "wd_val_01.zip".

Please prepare the following file structure before running the devkit (Kitti2015 and ScanNet will be downloaded automatically).
```
- devkit/instance/archives/
   - Cityscapes_archives/leftImg8bit_trainvaltest.zip
   - Cityscapes_archives/gtFine_trainvaltest.zip
   - WildDash_archives/wd_val_01.zip
```

The simplest way to use the devkit is to run the main script without any program
arguments:
```
python instance_devkit.py
```
On Windows, one may double-click instance_devkit.py if Python is installed.
The script may ask about a few settings and then download the datasets into a
folder in the current working directory. The folder layout is as follows:

```
datasets_<format_name>/
   metadata
   test
   training
```

If the optional program argument `--keep_archives` is given, the downloaded
archive files will not be deleted after the datasets are extracted
and converted.




## Dataset Format ##

#### Input ####

The Kitti 2015 segmentation format (described below) is used as common format for all datasets. 
The image names are prefixed by the dataset's benchmark name.
Exactly the same image names are used for the input images and the ground truth files.
```
datasets_kitti2015/
   test/
      image_2/
         <dataset>_<img_name>.png
         ...
   training/
      image_2/
         <dataset>_<img_name>.png
         ...
      instance/
         <dataset>_<img_name>.png
         ...
      semantic/
         <dataset>_<img_name>.png
         ...
```

The "semantic" folder contains the semantic segmentation ground truth for the training images. Each file is a single channel uint8 8-bit PNG image with each pixel value representing its semantic label ID. The "instance" folder contains the combined instance and semantic segmentation ground truth. Each file is a single channel uint16 16-bit PNG image where the lower 8 bits of each pixel value are its instance ID, while the higher 8 bits of each pixel value are its semantic labels ID. Instance IDs start from 1 for each semantic class (ex. car:1,2,3 ... etc. - buiding:1,2,3 ... etc.). Instance ID value of 0 means no instance ground truth is available and should be ignored for instance segmentation. An example code for reading the instance and semantic segmentation ground truth from the combined ground truth file in python could look like this :
```
import scipy.misc as sp
instance_semantic_gt = sp.imread('instance/<image name>.png')
instance_gt = instance_semantic_gt  % 256
semantic_gt = instance_semantic_gt // 256

```
The labels IDs, names and instance classes of the Cityscapes dataset are used and can be found [here](https://github.com/mcordts/cityscapesScripts/blob/master/cityscapesscripts/helpers/labels.py)

#### Output ####

The output structure should be analogous to the input.
If your algorithm is called MYALGO, the result files for your instance
or semantic segmentation method must be named and placed as follows:
```
datasets_kitti2015/
    test/
        algo_MYALGO_instance/
            pred_list/
                <dataset>_<img_name>.txt
                ...
            pred_img/
                <dataset>_<img_name>_000.png
                <dataset>_<img_name>_001.png
                ...
        algo_MYALGO_semantic/
            <dataset>_<img_name>.png
            ...
```

You may provide results for instance segmentation, semantic segmentation or both.
The `datasets_kitti2015/test/` directory for your algorithm output is the same directory which
contains the `ìmage_2` input images of the test scenes.

The txt files of the instance segmentation should look as follows:
```
relPathPrediction1 labelIDPrediction1 confidencePrediction1
relPathPrediction2 labelIDPrediction2 confidencePrediction2
relPathPrediction3 labelIDPrediction3 confidencePrediction3
...
```

For example, the Kitti2015_000000_10.txt may contain:
```
../pred_img/Kitti2015_000000_10_000.png 026 0.976347
../pred_img/Kitti2015_000000_10_001.png 026 0.973782
../pred_img/Kitti2015_000000_10_002.png 026 0.973202
...
```

with binary instance masks in `datasets_kitti2015/test/algo_MYALGO_instance/pred_img/`:
```
Kitti2015_000000_10_000.png
Kitti2015_000000_10_001.png
Kitti2015_000000_10_002.png
...
```



#### Running ####

Currently, it is required to manually call your method and create an
output file structure as described above.


## Result Submission ##

After an instance segmentation method has been run on all datasets, the results can be
automatically packaged for submission to each individual benchmark. To do so,
simply run the respective devkit script again in the same directory:
```
python instance_devkit.py
```
or
```
python semantic_devkit.py
```
It will then offer to create the submission archives. Notice that this requires
that results with the same method name are available for all datasets of all
relevant benchmarks (either for training or for both training and testing). If
the option to create a submission is missing, make sure that all required files
exist.

The resulting archives must be submitted to the respective benchmarks:
* [Cityscapes](https://www.cityscapes-dataset.com/login/)
* [Kitti2015](http://www.cvlibs.net/datasets/kitti/user_login.php)
* [ScanNet](http://www.scan-net.org/)
* [WildDash](http://wilddash.cc/accounts/login)

Furthermore, the submission must be completed by filling a short form on the
Robust Vision Challenge website: TODO


## Command Line Interface ##

As an alternative to the interactive interface, a command line interface is
available:

```
# Download the datasets:
# Either devkit will download and unpack both, instance and semantic segmentation
python instance_devkit.py obtain
# or: python semantic_devkit.py obtain

# Create archives for result submission:
# - method_name is the method to generate the submission archives for
python instance_devkit.py submit <method_name>
```
