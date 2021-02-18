# !/usr/bin/env python3
# -*-coding:utf-8-*-
# @file: exam01.py
# @brief:
# @author: Changjiang Cai, ccai1@stevens.edu, caicj5351@gmail.com
# @version: 0.0.1
# @creation date: 11-02-2021
# @last modified: Thu 11 Feb 2021 08:27:51 PM EST

#import pykitti
import os
import numpy as np
import pykitti.utils as utils

# Change this to the directory where you store KITTI data
my_base_path = '/media/ccjData3_HDD/datasets/kitti_raw/rawdata'

# Specify the dataset to load
#date = '2011_09_30'
#drive = '0034'
date = '2011_09_26'
drive = '0001'
dataset = 'sync'

my_drive = date + '_drive_' + drive + '_' + dataset
my_calib_path = os.path.join(my_base_path, date)
my_data_path = os.path.join(my_base_path, date, my_drive)

cam_to_cam_file = 'calib_cam_to_cam.txt'
data = {}
# Load and parse the cam-to-cam calibration data
cam_to_cam_filepath = os.path.join(my_calib_path, cam_to_cam_file)
filedata = utils.read_calib_file(cam_to_cam_filepath)

# Create 4x4 matrices from the rectifying rotation matrices
R_rect_00 = np.eye(4)
R_rect_00[0:3, 0:3] = np.reshape(filedata['R_rect_00'], (3, 3))

R_rect_10 = np.eye(4)
R_rect_10[0:3, 0:3] = np.reshape(filedata['R_rect_01'], (3, 3))

R_rect_20 = np.eye(4)
R_rect_20[0:3, 0:3] = np.reshape(filedata['R_rect_02'], (3, 3))

R_rect_30 = np.eye(4)
R_rect_30[0:3, 0:3] = np.reshape(filedata['R_rect_03'], (3, 3))

data['R_rect_00'] = R_rect_00
data['R_rect_10'] = R_rect_10
data['R_rect_20'] = R_rect_20
data['R_rect_30'] = R_rect_30

for i in range(0,4):
    k = 'R_rect_%d0'%(i)
    print ("data[%s] = \n%s" %(k, data[k]))

# Create 4x4 matrices from the raw rotation matrices
R_00 = np.eye(4)
R_00[0:3, 0:3] = np.reshape(filedata['R_00'], (3, 3))

R_10 = np.eye(4)
R_10[0:3, 0:3] = np.reshape(filedata['R_01'], (3, 3))

R_20 = np.eye(4)
R_20[0:3, 0:3] = np.reshape(filedata['R_02'], (3, 3))

R_30 = np.eye(4)
R_30[0:3, 0:3] = np.reshape(filedata['R_03'], (3, 3))

data['R_00'] = R_00
data['R_10'] = R_10
data['R_20'] = R_20
data['R_30'] = R_30
for i in range(0,4):
    k = 'R_%d0'%(i)
    print ("data[%s] (i.e., 0 --> %d(ref)) = \n%s" %(k, i, data[k]))
# T
for i in range(0,4):
    k = 'T_%d0'%(i)
    data['%s'%k] = np.reshape(filedata['T_0%d'%(i)], (3, 1))
    print ("data[%s] (i.e., 0 --> %d(ref)) = \n%s" %(k, i, data[k]))

# P
for i in range(0,4):
    k = 'P_%d0'%(i)
    data['%s'%k] = utils.transform_from_rot_trans(R=data['R_%d0'%(i)][:3,:3], t=data['T_%d0'%(i)])
    print ("data[%s] (i.e., 0 --> %d(ref)) = \n%s" %(k, i, data[k]))


# Load the data. Optionally, specify the frame range to load.
#dataset = pykitti.raw(my_base_path, date, drive, frames=range(0, 20, 5))