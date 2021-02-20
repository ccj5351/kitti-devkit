# !/usr/bin/env python3
# -*-coding:utf-8-*-
# @file: warp_src_to_ref_np.py
# @brief:
# @author: Changjiang Cai, ccai1@stevens.edu, caicj5351@gmail.com
# @version: 0.0.1
# @creation date: 11-02-2021
# @last modified: Thu 11 Feb 2021 08:27:51 PM EST

import numpy as np

def get_rel_extrinsicM(ext_ref, ext_src):
    ''' Get the extrinisc matrix from ref_view to src_view '''
    return ext_src.dot( np.linalg.inv( ext_ref))

"""
warp source frame to reference view, based on ref. depth;
- Step 1: For homography H(d), to map ref index (x, y, 1) --> src index (x’, y’, 1)
          I.e., λ*(x', y', 1)^T = H(d)* (x, y, 1)^T 
- Step 2: assigement via Warp_src(x, y) = Img_src(x', y')

- Step 3: Then we can compare Img_ref and Warp_src;

"""
def warp_src_to_ref_naive(img_src, dep_ref, pose_rel_ref_2_src, K_src, K_ref, is_identy = False):
    if is_identy:
        return img_src
    
    #homography
    height, width = dep_ref.shape[0:2]
    #normal vector
    norm_vec = np.array([[.0, .0, 1.]]).astype(np.float32)
    R_rel_ref_2_src = pose_rel_ref_2_src[0:3, 0:3]
    t_rel_ref_2_src = pose_rel_ref_2_src[0:3, 3:4]
    print ("R_ref2_src = \n%s" %R_rel_ref_2_src)
    print ("t_ref2_src = \n%s" %t_rel_ref_2_src)
    tn = t_rel_ref_2_src.dot(norm_vec)
    I = np.eye(3)
    #h1 = K_src.dot(R_rel_ref_2_src.T)
    h1 = K_src.dot(R_rel_ref_2_src)
    h3 = np.linalg.inv(K_ref)
    warped_src = np.zeros((height, width, 3), dtype=np.uint8) # color image
    for y in range(height):
        for x in range(width):
            d = dep_ref[y, x]
            if abs(d) > 1e-3:
                h2 = I - tn/d
                h = np.dot(np.dot(h1, h2), h3)
                r = np.dot(h, np.array([[x], [y], [1]]))
                x_new, y_new = int(r[0, 0]/r[2, 0]), int(r[1, 0]/r[2, 0])
                if 0<= x_new < width and 0<= y_new < height:
                    warped_src[y, x, :] = img_src[y_new, x_new,:]
    return warped_src


def warp_src_to_ref_naive_v2(img_src, dep_ref, pose_rel_ref_2_src, K_src, K_ref, is_identy = False):
    if is_identy:
        return img_src
    
    #homography
    height, width = img_src.shape[0:2]
    #normal vector
    norm_vec = np.array([[.0, .0, 1.]]).astype(np.float32)
    R_rel_ref_2_src = pose_rel_ref_2_src[0:3, 0:3]
    t_rel_ref_2_src = pose_rel_ref_2_src[0:3, 3:4]
    print ("R_ref2_src = \n%s" %R_rel_ref_2_src)
    print ("t_ref2_src = \n%s" %t_rel_ref_2_src)
    tn = t_rel_ref_2_src.dot(norm_vec)
    I = np.eye(3)
    inv_K_ref = np.linalg.inv(K_ref)
    h1 = K_src.dot(R_rel_ref_2_src).dot(inv_K_ref)
    h2 = K_src.dot(tn).dot(inv_K_ref)
    warped_src = np.zeros((height, width, 3), dtype=np.uint8) # color image
    for y in range(height):
        for x in range(width):
            d = dep_ref[y, x]
            if abs(d) > 1e-3:
                H = h1 - h2/d
                r = H.dot(np.array([[x], [y], [1]]))
                x_new, y_new = int(r[0, 0]/r[2, 0]), int(r[1, 0]/r[2, 0])
                if 0<= x_new < width and 0<= y_new < height:
                    warped_src[y, x, :] = img_src[y_new, x_new,:]
    return warped_src