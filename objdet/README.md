# Robust Vision Challenge 2020 - Object Detection Devkit #

The Object detection challenge consists of four datasets:
- [MS COCO](cocodataset.org/)
- [OpenImages](https://storage.googleapis.com/openimages/web/index.html) (OID)
- [Mapillary Vistas](https://www.mapillary.com/dataset/vistas) (MVD)

**Update 2020-07-17: Megvii had to remove Obj365 from the RVC due to internal policy changes (see objects365.org); we will rank the obj. det. challenge using the three benchmarks COCO, OID, and MVD**

## Requirements ##
Install additional requirements with:
    ``` pip install -r requirements.txt ```


## Dataset Download ##

We provide a devkit to download, extract, and convert the challenge datasets into a unified format.

1. Specify the target root directory for all RVC datasets with ``` export RVC_DATA_DIR=/path/to/rvc_dataroot  ```

2. Get an authentication token for the Kaggle API as described here: https://www.kaggle.com/docs/api. This is required to download the OpenImages test data from kaggle.

3. Execute the download script ``` bash download_obj_det.sh ``` which will download most of the RVC datasets. The extracted dataset needs ca. 600GB of disk space (COCO: 26GB, OID: 527GB, MVD: 25GB). Please note that up to 50% more disc space is required during the extraction process.

4. To download the Mapillary Vistas (Research Edition) dataset you need to manually register and download at https://www.mapillary.com/dataset/vistas You will receive an email with download instructions. Save/Move the downloaded zip file into the folder RVC_DATA_DIR/mvd.

5. After successfully downloading all datasets, execute ``` bash extract_and_cleanup.sh ``` to extract and delete clean up files.

### Dataset remapping ###

RVC does not force you to remap the datasets in a certain way. We do provide a "best-effort" mapping, which can be a good starting point. This mapping will contain overlapping classes and some dataset entries might miss relevant labels (as they were annotated using different policies/mixed hierarchical  levels). Combine and remap datasets by executing the script 

 ```bash remap_obj_det.sh ```

## Dataset Format / Training ##

The above step creates a joint training and a separate joint validation json file in COCO Object Detection format (only bbox entries, without "segmentation" entries):

http://cocodataset.org/#format-data

The "file_name" tag of each image entry has been prepended with the relative path calculated from RVC_DATA_DIR.
These files can directly be used in your object detector training framework.

## Result Submission ##

Fill in the "Register Method to RVC" form here: http://www.robustvision.net/submit.php
You have to run the evaluation for the test set of each dataset individually as specified on http://www.robustvision.net/submit.php .
For predictions in the coco format we provide a script to map the predicted categories back from the joint embedding space. Use

 ```bash remap_results.sh -p /path/to/predictions -d DATASET ```
 
 Replace DATASET with the corresponding datasets abbreviation:
 - `mvd` for mapillary vistas
 - `coco` for COCO 
 - `oid` for OpenImages. 
 The converted predictions will be saved in the same location as the predictions but the filename fill be changed to FILENAME_remapped_results.json.
 After that, upload your predictions for the respective test sets of each benchmark:

- COCO : https://competitions.codalab.org/competitions/25334
- MVD : https://codalab.mapillary.com/competitions/41
- OID : https://www.kaggle.com/c/open-images-object-detection-rvc-2020
