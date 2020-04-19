#!/bin/sh

# Downloads the COCO dataset with boxable GT. (7GB of input images and 0.24GB of annotations)
# Based on https://github.com/mseg-dataset/mseg-api-staging/blob/master/download_scripts/mseg_download_cocopanoptic.sh

# By using this script, you agree to all terms
# and conditions set forth by the creators of the
# COCO Stuff, MS COCO, and COCO Boxable datasets.

# ----------- Directory Setup -----------------------
# Destination directory for MSeg
RVC_COCO_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use this script's dir
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_COCO_TRG_DIR=${RVC_OBJ365_SCRIPT_DIR}/../datasets/coco
else
  RVC_COCO_TRG_DIR=${RVC_DATA_DIR}/coco
fi

# ----------- Downloading ---------------------------
mkdir -p $RVC_COCO_TRG_DIR
cd $RVC_COCO_TRG_DIR
echo "Downloading COCO boxable dataset..."
# Get the annotations.
COCOP_ANNOT_URL="http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
wget $COCOP_ANNOT_URL

# train2017.zip will be 19GB.
TRAIN_IMGS_URL="http://images.cocodataset.org/zips/train2017.zip"
wget $TRAIN_IMGS_URL
mkdir -p images
unzip train2017.zip -d images
rm train2017.zip

VAL_IMGS_URL="http://images.cocodataset.org/zips/val2017.zip"
wget $VAL_IMGS_URL

unzip val2017.zip -d images
rm val2017.zip

unzip annotations_trainval2017.zip
rm annotations_trainval2017.zip

echo "COCO boxable dataset extracted."
