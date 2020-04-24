## Common tools for the Robust Vision Challenge 2020 dev kit

### Unified label space

Combining multiple datasets requires a joint label space (JLS). The dev kit provides a best-effort mapping but you are free to extend/change this mapping to your liking. 
During submission time the same mapping is applied backwards. This dev kit is provided as-is without warrenty. 
Each benchmark participating at the challenge still expects data in their respective format and will rank submissions based on this. Please remember that you should not emply methods to deliberatly train different versions for different benchmarks. Your training should try to fit the union of all training data.

The mapping file joint_mapping.json contains information to unify labels for all four task related to labels:
object detection, semantic segmentation, instance segmentation, panoptic segmentation

The resulting mappings have been generated in part from existing mappings:

[TODO: all contributions]

Official ADE20K label list:
https://github.com/CSAILVision/sceneparsing/blob/master/objectInfo150.csv
Official OID label lists: https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-label300-segmentable-hierarchy.json
and https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-label500-hierarchy.json
Boxable COCO labels compiled by github user amikelive: https://github.com/amikelive/coco-labels/blob/master/coco-labels-2014_2017.txt
Official COCO panoptic label list: https://raw.githubusercontent.com/cocodataset/panopticapi/master/panoptic_coco_categories.json

Label merging efforts supported by:
**MSeg: A Composite Dataset for Multi-domain Semantic Segmentation** [[PDF]](http://vladlen.info/papers/MSeg.pdf)
<br>
[John Lambert*](https://johnwlambert.github.io/),
[Zhuang Liu*](https://liuzhuang13.github.io/),
[Ozan Sener](http://ozansener.net/),
[James Hays](https://www.cc.gatech.edu/~hays/),
[Vladlen Koltun](http://vladlen.info/)
<br>
Presented at [CVPR 2020](http://cvpr2018.thecvf.com/)
