"""Provides 'vkt2', which loads and parses Virtual KITTI 2 data. 
   The code is adopted from pykitti at https://github.com/utiasSTARS/pykitti
"""

import datetime as dt
import glob
import os
from collections import namedtuple

import numpy as np
from PIL import Image
import cv2

#import pykitti.utils as utils

__author__ = "Changjiang"
__email__ = "changjiangcai2020@gmail.com"


"""
> see: https://www.machinelearningplus.com/python/python-property/
When to use @property decorator?
When an attribute is derived from other attributes in the class, so the derived attribute will update whenever the source attributes is changed.
How to make a @property?
Make an attribute as property by defining it as a function and add the @property decorator before the fn definition.
When to define a setter method for the property?
Typically, if you want to update the source attributes whenever the property is set. It lets you define any other changes as well."
"""

# > see: Virtual KITTI 2 Discription: https://europe.naverlabs.com/research/computer-vision/proxy-virtual-worlds-vkitti-2/
"""
Virtual KITTI 2 Includes:

SceneX/Y/frames/rgb/Camera_Z/rgb_%05d.jpg
SceneX/Y/frames/depth/Camera_Z/depth_%05d.png
SceneX/Y/frames/classsegmentation/Camera_Z/classgt_%05d.png
SceneX/Y/frames/instancesegmentation/Camera_Z/instancegt_%05d.png
SceneX/Y/frames/backwardFlow/Camera_Z/backwardFlow_%05d.png
SceneX/Y/frames/backwardSceneFlow/Camera_Z/backwardSceneFlow_%05d.png
SceneX/Y/frames/forwardFlow/Camera_Z/flow_%05d.png
SceneX/Y/frames/forwardSceneFlow/Camera_Z/sceneFlow_%05d.png
SceneX/Y/colors.txt
SceneX/Y/extrinsic.txt
SceneX/Y/intrinsic.txt
SceneX/Y/info.txt
SceneX/Y/bbox.txt
SceneX/Y/pose.txt

where: 
- X ∈ {01, 02, 06, 18, 20} and represent one of 5 different locations.
- Y ∈ {15-deg-left, 15-deg-right, 30-deg-left, 30-deg-right, clone, fog, morning, overcast, rain, sunset} 
  and represent the different variations.
- Z ∈ [0, 1] and represent the left (same as in virtual kitti) or right camera (offset by 0.532725m to the right). 
Note that our indexes always start from 0. 
"""


def load_image(file, mode):
    """Load an image from file."""
    return Image.open(file).convert(mode)


def yield_images(imfiles, mode):
    """Generator to read image files."""
    for file in imfiles:
        yield load_image(file, mode)


def load_depth(depth_png_filename):
    #NOTE: The depth map in centimeters can be directly loaded
    depth = cv2.imread(depth_png_filename, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH).astype(np.float32)
    depth = depth / 1000 # change cm to meters;
    return depth

def yield_depths(depthfiles):
    """Generator to read depth files."""
    for d_file in depthfiles:
        yield load_depth(d_file)


def subselect_files(files, indices):
    try:
        files = [files[i] for i in indices]
    except:
        pass
    return files


class vkt2:
    """Load and parse raw data into a usable format."""

    def __init__(self, 
                base_path = '/media/ccjData2/datasets/Virtual-KITTI-V2/', 
                sceneX = 'Scene01', 
                variantY = '15-deg-left', 
                **kwargs):
        """Set the path and pre-load calibration data and timestamps."""
        self.base_path = base_path 
        self.sceneX = sceneX
        self.variantY = variantY
        self.calib_path = os.path.join(self.base_path, 'vkitti_2.0.3_textgt', self.sceneX, self.variantY)

        self.frames = kwargs.get('frames', None)

        # Default image and depth files extensions
        self.imtype = kwargs.get('imtype', 'jpg')
        self.depthtype = kwargs.get('depthtype', 'png')

        # Find all the data files
        self._get_file_lists()
        
        # read intrinsic K
        self._get_intrinsic()
        # read extrinsic E for frames
        self._read_extrinsic_file()


    def __len__(self):
        """Return the number of frames loaded."""
        # already do Subselect the chosen range of frames, if any
        return len(self.cam0_img_files)

    @property
    def cam0(self):
        """Generator to read image files for cam0 (RGB left)."""
        # mode = 'L' for monochrome
        # mode = 'RGB' for RGB color
        return yield_images(self.cam0_img_files, mode='RGB')

    def get_cam0(self, idx):
        """Read image file for cam0 (RGB left) at the specified index."""
        return load_image(self.cam0_img_files[idx], mode='RGB')

    @property
    def cam1(self):
        """Generator to read image files for cam1 (RGB right)."""
        return yield_images(self.cam1_img_files, mode='RGB')

    def get_cam1(self, idx):
        """Read image file for cam1 (RGB right) at the specified index."""
        return load_image(self.cam1_img_files[idx], mode='RGB')


    @property
    def depth0(self):
        """Generator to read depth files for cam0 (RGB left)."""
        return yield_depths(self.cam0_depth_files)

    def get_depth0(self, idx):
        """Read depth file for cam0 (RGB left) at the specified index."""
        return load_depth(self.cam0_depth_files[idx])


    @property
    def depth1(self):
        """Generator to read depth files for cam1 (RGB right)."""
        return yield_depths(self.cam1_depth_files)

    def get_depth1(self, idx):
        """Read depth file for cam1 (RGB right) at the specified index."""
        return load_depth(self.cam1_depth_files[idx])



    @property
    def rgb(self):
        """Generator to read RGB stereo pairs from file.
        """
        return zip(self.cam0, self.cam1)

    def get_rgb(self, idx):
        """Read RGB stereo pair at the specified index."""
        return (self.get_cam0(idx), self.get_cam1(idx))

    def _get_file_lists(self):
        """Find and list data files for each sensor."""
        self.cam0_img_files = sorted(glob.glob(
            os.path.join(self.base_path, 'vkitti_2.0.3_rgb', self.sceneX, self.variantY,
                         'frames/rgb/Camera_0', '*.{}'.format(self.imtype))))

        self.cam1_img_files = sorted(glob.glob(
            os.path.join(self.base_path, 'vkitti_2.0.3_rgb', self.sceneX, self.variantY,
                         'frames/rgb/Camera_1', '*.{}'.format(self.imtype))))

        self.cam0_depth_files = sorted(glob.glob(
            os.path.join(self.base_path, 'vkitti_2.0.3_depth', self.sceneX, self.variantY,
                         'frames/depth/Camera_0', '*.{}'.format(self.depthtype))))

        self.cam1_depth_files = sorted(glob.glob(
            os.path.join(self.base_path, 'vkitti_2.0.3_depth', self.sceneX, self.variantY,
                         'frames/depth/Camera_1', '*.{}'.format(self.depthtype))))
        
        # Subselect the chosen range of frames, if any
        if self.frames is not None:
            self.cam0_img_files = subselect_files(
                self.cam0_img_files, self.frames)
            self.cam1_img_files = subselect_files(
                self.cam1_img_files, self.frames)
            self.cam0_depth_files = subselect_files(
                self.cam0_depth_files, self.frames)
            self.cam1_depth_files = subselect_files(
                self.cam1_depth_files, self.frames)

    
    # fixed intrinsic
    def _get_intrinsic(self):
        K = np.eye(3, dtype=np.float32)
        K[0,0] = 725.0087 
        K[1,1] = 725.0087 
        K[0,2] = 620.5
        K[1,2] = 187.0
        self.cam0_K = K
        self.cam1_K = K

    def _read_extrinsic_file(self):
        """Read in a calibration file and parse into a dictionary."""
        filepath = os.path.join(self.calib_path, 'extrinsic.txt')
        cam0_E = []
        data = {}
        # cameraID = {0, 1}
        data['cam0'] = []
        data['cam1'] = []
        with open(filepath, 'r') as f:
            for line in f.readlines():
                if line.startswith('frame'):
                    continue
                # line format: frame cameraID r1,1 r1,2 r1,3 t1 r2,1 r2,2 r2,3 t2 r3,1 r3,2 r3,3 t3 0 0 0 1;
                line = line.split()
                frame_idx = int(line[0])
                cam_idx = int(line[1])
                # Extrinsic E includes r1,1 r1,2 r1,3 t1 r2,1 r2,2 r2,3 t2 r3,1 r3,2 r3,3 t3 0 0 0 1;
                E = [float(x) for x in line[2:18]]
                data['cam%d'%(cam_idx)].append(E)
        self.cam0_E = data['cam0']
        self.cam1_E = data['cam1']
        # Subselect the chosen range of frames, if any
        if self.frames is not None:
            self.cam0_E = subselect_files(
                self.cam0_E, self.frames)
            self.cam1_E = subselect_files(
                self.cam1_E, self.frames)

    def get_cam0_E(self, idx):
        """get Extrinsic for cam0 (RGB left) at the specified index."""
        return np.array(self.cam0_E[idx], dtype=np.float32).reshape(4, 4)
    def get_cam1_E(self, idx):
        """get Extrinsic for cam1 (RGB right) at the specified index."""
        return np.array(self.cam1_E[idx], dtype=np.float32).reshape(4, 4) 