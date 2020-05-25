#!/bin/sh
# Remaps individual boxable ground truth of RVC datasets into a joint dataset
# requires git, python and pycocotools which can be installed via:
# pip install pycocotools
# (use gitbash for MS Windows)

RVC_SEM_SEG_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_DATA_SRC_DIR=${RVC_SEM_SEG_SCRIPT_DIR}/../datasets/
else
  RVC_DATA_SRC_DIR=${RVC_DATA_DIR}/
fi

if [ -z "${RVC_JOINED_TRG_DIR}" ]; then
  RVC_DATA_TRG_DIR=${RVC_DATA_SRC_DIR}/rvc_uint8
else
  RVC_DATA_TRG_DIR=${RVC_JOINED_TRG_DIR}/
fi
mkdir -p ${RVC_DATA_TRG_DIR}

if [ ! -d $RVC_SEM_SEG_SCRIPT_DIR/mseg_api ]; then
  # getting defined version of mseg repo
  git -C $RVC_SEM_SEG_SCRIPT_DIR clone https://github.com/mseg-dataset/mseg-api.git $RVC_SEM_SEG_SCRIPT_DIR/mseg_api
  git -C $RVC_SEM_SEG_SCRIPT_DIR/mseg_api checkout 7e72a0f4cfb002786b10f2918ead916d0e2bc22d
  git -C $RVC_SEM_SEG_SCRIPT_DIR/mseg_api apply $RVC_SEM_SEG_SCRIPT_DIR/mseg_api.patch
  pip install -e $RVC_SEM_SEG_SCRIPT_DIR/mseg_api
fi

pushd $RVC_SEM_SEG_SCRIPT_DIR/../common
  if [ -f "$RVC_DATA_SRC_DIR/wilddash/panoptic_0.json" ]; then
    #Creates random split for train/val (currently no specific split supplied)
    python rvc_split_coco.py --input $RVC_DATA_SRC_DIR/wilddash/panoptic.json --split "80;20"
  fi

  #add missing rvc datasets to mseg api
  python rvc_add_dataset_mseg.py --panoptic_json ${RVC_DATA_SRC_DIR}/wilddash/panoptic_{split_idx}.json --orig_dname wilddash2-rvc --img_subfolder images --annot_subfolder panoptic
  python rvc_add_dataset_mseg.py --panoptic_json ${RVC_DATA_SRC_DIR}/viper/{split}/pano.json --orig_dname viper-rvc --img_subfolder {split}/img/{file_name[0]}{file_name[1]}{file_name[2]}  --annot_subfolder panoptic {split}/pano/{file_name[0]}{file_name[1]}{file_name[2]}


  RVC_COMMON_CONV_PARAMS="--remapped_dataroot ${RVC_DATA_TRG_DIR} --mapping_tsv ${RVC_SEM_SEG_SCRIPT_DIR}/ss_mapping_uint8_mseg.tsv --create_symlink_cpy"
  python rvc_remap_dataset_mseg.py --orig_dname ade20k-151 --orig_dataroot ${RVC_DATA_SRC_DIR}/ade20k/ADEChallengeData2016 $RVC_COMMON_CONV_PARAMS
  python rvc_remap_dataset_mseg.py --orig_dname kitti-34 --orig_dataroot ${RVC_DATA_SRC_DIR}/kitti $RVC_COMMON_CONV_PARAMS
  python rvc_remap_dataset_mseg.py --orig_dname cityscapes-34 --orig_dataroot ${RVC_DATA_SRC_DIR}/cityscapes $RVC_COMMON_CONV_PARAMS
  python rvc_remap_dataset_mseg.py --orig_dname coco-panoptic-201 --orig_dataroot ${RVC_DATA_SRC_DIR}/coco --panoptic_json "${RVC_DATA_SRC_DIR}/coco/annotations/panoptic_{split}2017.json" $RVC_COMMON_CONV_PARAMS
  python rvc_remap_dataset_mseg.py --orig_dname viper-rvc-32 --orig_dataroot ${RVC_DATA_SRC_DIR}/viper --panoptic_json "${RVC_DATA_SRC_DIR}/viper/{split}/pano.json" $RVC_COMMON_CONV_PARAMS
  python rvc_remap_dataset_mseg.py --orig_dname wilddash2-rvc-39 --orig_dataroot ${RVC_DATA_SRC_DIR}/wilddash --panoptic_json "${RVC_DATA_SRC_DIR}/wilddash/panoptic_{split_idx}.json" $RVC_COMMON_CONV_PARAMS

popd

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_SEM_SEG_SCRIPT_DIR=

echo "Finished remapping."

