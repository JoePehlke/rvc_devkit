# Robust Vision Challenge 2020 Devkits

This repository contains the devkits for the [Robust Vision Challenge 2020](http://robustvision.net/).
The devkits make it easy to participate in the challenge by:

* downloading the required datasets,
* converting them to a common format, and
* creating archives for submission to the individual benchmarks.

Any updates to the devkits will be provided via this repository.

Still unsupport and under development: Semantic Segmentation Task; OID for Instance Segmentation; KITTI for Instance Segmentation and Panoptic Segmentation

Notice that using the devkits is not required for participating in the
challenge: alternatively, algorithms can be manually run on each dataset and
results submitted to all benchmarks individually (as long as the same method and
parameters are used for all results).

## Getting started ##

Prerequisites: Install `wget`, `git`, and `python` (both versions 2.7.x and 3.x should work) if they are not installed yet.
These python packages are required for automatic dataset downloading and data conversions:

 ```   
   pip install requests
   pip install imageio
   pip install scipy
   pip install awscli
```

1. Clone this repository:
   ```git clone https://github.com/ozendelait/rvc_devkit.git```
2. See the README in the subfolder of the task you are interested in (depth,
   flow, etc.) for further task-specific instructions.

Note: Windows support is experimental and not recommended. Use an Anaconda environment and gitbash to execute the scripts. The required wget can be installed with  ```conda install -c menpo wget```

## Participating ##

The process for participating in the challenge is as follows.

* After following the instructions for getting started above, download the
  datasets for the task which you are interested in using the devkit for this task.
  See the README in the task subfolder for instructions on this.
* Most datasets come with ground truth data and can be used for training
  your algorithm.
* Once you are happy with the results of your algorithm based on the training datasets,
  run your algorithm on all datasets. See the README for the specific task for
  information on the expected result format.
* Use the devkit to create submission archives for all included benchmarks.
* Submit each archive to the respective benchmark website. Make sure to use "_RVC" as
  a postfix to your method name to signal that your submission participates in
  the challenge. For example, if your original method was called ELAS, name your
  submission ELAS_RVC.
  On some benchmark websites special characters such as &, |, * are prohibited.
  Choose a short method name (up to 10 characters) for your method (allowed characters: + - _ A..Z a..z 0..9)
  to guarantee that you can use exactly the same name on all benchmarks.
* Register your submission at the [submission form](http://robustvision.net/submit.php#register).
