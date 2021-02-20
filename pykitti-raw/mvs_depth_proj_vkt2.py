# !/usr/bin/env python3
# -*-coding:utf-8-*-
# @file: exam01.py
# @brief:
# @author: Changjiang Cai, ccai1@stevens.edu, caicj5351@gmail.com
# @version: 0.0.1
# @creation date: 11-02-2021
# @last modified: Thu 11 Feb 2021 08:27:51 PM EST
import matplotlib.pyplot as plt
import pykitti
import os
import numpy as np
import sys
import cv2
from os.path import join as pjoin

from PIL import Image
import vkt2

from warp_src_to_ref_np import get_rel_extrinsicM, warp_src_to_ref_naive_v2, warp_src_to_ref_naive


def kitti_colormap(disparity, maxval=-1):
	"""
	A utility function to reproduce KITTI fake colormap
	Arguments:
	- disparity: numpy float32 array of dimension HxW
	- maxval: maximum disparity value for normalization (if equal to -1, the maximum value in disparity will be used)
	
	Returns a numpy uint8 array of shape HxWx3.
	"""
	if maxval < 0:
		maxval = np.max(disparity)
                #print ('maxval = %f' % maxval)

	colormap = np.asarray([[0,0,0,114],[0,0,1,185],[1,0,0,114],[1,0,1,174],[0,1,0,114],[0,1,1,185],[1,1,0,114],[1,1,1,0]])
	weights = np.asarray([8.771929824561404,5.405405405405405,8.771929824561404,5.747126436781609,8.771929824561404,5.405405405405405,8.771929824561404,0])
	cumsum = np.asarray([0,0.114,0.299,0.413,0.587,0.701,0.8859999999999999,0.9999999999999999])

	colored_disp = np.zeros([disparity.shape[0], disparity.shape[1], 3])
	values = np.expand_dims(np.minimum(np.maximum(disparity/maxval, 0.), 1.), -1)
	bins = np.repeat(np.repeat(np.expand_dims(np.expand_dims(cumsum,axis=0),axis=0), disparity.shape[1], axis=1), disparity.shape[0], axis=0)
	diffs = np.where((np.repeat(values, 8, axis=-1) - bins) > 0, -1000, (np.repeat(values, 8, axis=-1) - bins))
	index = np.argmax(diffs, axis=-1)-1

	w = 1-(values[:,:,0]-cumsum[index])*np.asarray(weights)[index]


	colored_disp[:,:,2] = (w*colormap[index][:,:,0] + (1.-w)*colormap[index+1][:,:,0])
	colored_disp[:,:,1] = (w*colormap[index][:,:,1] + (1.-w)*colormap[index+1][:,:,1])
	colored_disp[:,:,0] = (w*colormap[index][:,:,2] + (1.-w)*colormap[index+1][:,:,2])

	return (colored_disp*np.expand_dims((disparity>0),-1)*255).astype(np.uint8)


if __name__ == "__main__":

    # Change this to the directory where you store KITTI data
    my_base_path = "/media/ccjData2/datasets/Virtual-KITTI-V2/"
    sceneX = "Scene01"
    variantY="15-deg-left"

    # Load the data. 
    my_dataset = vkt2.vkt2(my_base_path, sceneX, variantY, 
                            #frames=range(0, 20, 5)
                            )
    
    # neural rgb2d paper:
    delta_t = 5
    #delta_t = 1
    cur_t = 2*delta_t + 20
    #local_window = [cur_t - 2*delta_t, cur_t - delta_t, cur_t, cur_t + delta_t, cur_t + 2*delta_t]
    #names_local = [r'$I_{-2}$', r'$I_{-1}$', r'$I_{0}$', r'$I_{+1}$', r'$I_{+2}$']
    local_window = [cur_t - delta_t, cur_t, cur_t + delta_t]
    cur_t_idx = local_window.index(cur_t)
    print ("cur_t_idx = ", cur_t_idx)
    #names_local = [r'$I_{-1}$', r'$I_{0}$', r'$I_{+1}$']
    names_local = [r'$I_{%d}$'%(cur_t - delta_t), r'$Ref = I_{%d}$'%(cur_t), r'$I_{%d}$'%(cur_t+delta_t)]
    frames_local = [my_dataset.get_cam0(idx) for idx in local_window]
    #source_frames = [my_dataset.get_cam2(idx) for idx in local_window if idx != cur_t]
    ref_frame = my_dataset.get_cam0(cur_t)

    depths_local = [my_dataset.get_depth0(idx) for idx in local_window]
    ref_depth = my_dataset.get_depth0(cur_t)


    f, ax = plt.subplots(3, len(local_window), figsize=(20, 10))
    for i, n in enumerate(names_local):
        ax[0, i].imshow(frames_local[i])
        ax[0, i].set_title('%s (cam0)'%n)
    
    K_cam0 = my_dataset.cam0_K


    # pose, i.e., extrinsics E = [R | t]
    #cam_relative_poses_local = [] # from ref to src;
    extM_local = [ my_dataset.get_cam0_E(idx) for idx in local_window]
    extM_ref = extM_local[cur_t_idx]
    cam_relative_poses_local = [get_rel_extrinsicM(extM_ref, M) for M in extM_local]
    


    for i, n in enumerate(names_local):
        depth = depths_local[i] 
        #ax[1, i].imshow(depth, cmap='gray')
        #mycmap = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
        #ax[1, i].imshow(depth, cmap= mycmap[4])
        ax[1, i].imshow( kitti_colormap(1.0/depth))
        ax[1, i].set_title('GT depth for %s (rgb left camera, i.e., cam0)'%n)
        #ax[2, i].imshow(count, cmap='gray')
        #ax[2, i].set_title('count depth from velodyne for %s (cam2)'%n)
        
        # warp
        img_src_np = np.asarray(frames_local[i])
        if 1:
            warped_img = warp_src_to_ref_naive(
                img_src_np, ref_depth, 
                pose_rel_ref_2_src = cam_relative_poses_local[i],
                K_src = K_cam0,
                K_ref = K_cam0,
                #is_identy= (i==cur_t_idx)
                )
        else:
            warped_img = warp_src_to_ref_naive_v2(
                img_src_np, ref_depth, 
                pose_rel_ref_2_src = cam_relative_poses_local[i],
                K_src = K_cam0,
                K_ref = K_cam0,
                #is_identy= (i==cur_t_idx)
                )

        ax[2, i].imshow(warped_img)
        ax[2, i].set_title('warped src to ref view for %s (cam0)'%n)

    plt.show()