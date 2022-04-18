# RCareWorld 1.0
Here is the code for RCareWorld 1.0 version. The project is under active development now. We will keep maintaining the code and model assets.

# Components
## CareURDF
Users can use this module to generate URDF files for SMPL-X model, and plan motion of human limbs.
## CareHomes
Users can use this tool to perform home modification on Matterport dataset.

## Unity Side
We use [RFUniverse](https://wenqiangx.github.io/robotflowproject/project/rfuniverse/) to construct Unity 


## Experiments
### Train
run `python train.py --algo tqc --env KinovaDressing-v1`
### Test
run `python enjoy.py --algo tqc --env KinovaDressing-v1 -f logs/ -n 1000`
### Record Video
run `python -m utils.record_video --algo tqc --env KinovaDressing-v1 -f logs/ -n 1000`
