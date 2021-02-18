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
from mpl_toolkits.mplot3d import Axes3D
import sys
import cv2
from collections import Counter
from os.path import join as pjoin

#import pykitti.utils as utils

""" this function is adpoted from https://github.com/utiasSTARS/pykitti/blob/master/pykitti/utils.py """ 
def read_calib_file(filepath):
    """Read in a calibration file and parse into a dictionary."""
    data = {}

    with open(filepath, 'r') as f:
        for line in f.readlines():
            key, value = line.split(':', 1)
            # The only non-float values in these files are dates, which
            # we don't care about anyway
            try:
                data[key] = np.array([float(x) for x in value.split()])
            except ValueError:
                pass

    return data

def sub2ind(matrixSize, rowSub, colSub):
    m, n = matrixSize
    return rowSub * (n-1) + colSub - 1

""" this function is adpoted from monodepth https://github.com/mrharicot/monodepth/blob/master/utils/evaluation_utils.py """
def load_velodyne_points(file_name):
    # adapted from https://github.com/hunse/kitti
    points = np.fromfile(file_name, dtype=np.float32).reshape(-1, 4)
    points[:, 3] = 1.0  # homogeneous
    return points


""" this function is adpoted from monodepth https://github.com/mrharicot/monodepth/blob/master/utils/evaluation_utils.py """
def lin_interp(shape, xyd):
    # taken from https://github.com/hunse/kitti
    from scipy.interpolate import LinearNDInterpolator
    m, n = shape
    ij, d = xyd[:, 1::-1], xyd[:, 2]
    f = LinearNDInterpolator(ij, d, fill_value=0)
    J, I = np.meshgrid(np.arange(n), np.arange(m))
    IJ = np.vstack([I.flatten(), J.flatten()]).T
    disparity = f(IJ).reshape(shape)
    return disparity


""" this function is adpoted from monodepth https://github.com/mrharicot/monodepth/blob/master/utils/evaluation_utils.py """
def generate_depth_map(calib_dir, velo_file_name, im_shape, cam=2, interp=False, vel_depth=False):
    # load calibration files
    print ("[***] loading cam2cam file ", pjoin(calib_dir, 'calib_cam_to_cam.txt'))
    print ("[***] loading velo2cam file ", pjoin(calib_dir, 'calib_velo_to_cam.txt'))
    cam2cam = read_calib_file(pjoin(calib_dir, 'calib_cam_to_cam.txt'))
    velo2cam = read_calib_file(pjoin(calib_dir, 'calib_velo_to_cam.txt'))
    print (velo2cam['R'])
    velo2cam = np.hstack((velo2cam['R'].reshape(3,3), velo2cam['T'][..., np.newaxis]))
    velo2cam = np.vstack((velo2cam, np.array([0, 0, 0, 1.0])))

    # compute projection matrix velodyne->image plane
    R_cam2rect = np.eye(4)
    R_cam2rect[:3,:3] = cam2cam['R_rect_00'].reshape(3,3)
    P_rect = cam2cam['P_rect_0'+str(cam)].reshape(3,4)
    P_velo2im = np.dot(np.dot(P_rect, R_cam2rect), velo2cam)

    # load velodyne points and remove all behind image plane (approximation)
    # each row of the velodyne data is forward, left, up, reflectance
    # i.e., (x, y, z, reflectance)
    velo = load_velodyne_points(velo_file_name)
    velo = velo[velo[:, 0] >= 0, :]

    # project the points to the camera
    velo_pts_im = np.dot(P_velo2im, velo.T).T
    velo_pts_im[:, :2] = velo_pts_im[:,:2] / velo_pts_im[:,2][..., np.newaxis]

    if vel_depth:
        velo_pts_im[:, 2] = velo[:, 0]

    # check if in bounds
    # use minus 1 to get the exact same value as KITTI matlab code
    # get (u, v) along x and y axis, respectively
    velo_pts_im[:, 0] = np.round(velo_pts_im[:,0]) - 1 # x along width;
    velo_pts_im[:, 1] = np.round(velo_pts_im[:,1]) - 1 # y along height;
    # get valid index
    val_inds = (velo_pts_im[:, 0] >= 0) & (velo_pts_im[:, 1] >= 0)
    val_inds = val_inds & (velo_pts_im[:,0] < im_shape[1]) & (velo_pts_im[:,1] < im_shape[0])
    velo_pts_im = velo_pts_im[val_inds, :]

    # project to image
    depth = np.zeros((im_shape))
    depth[velo_pts_im[:, 1].astype(np.int), velo_pts_im[:, 0].astype(np.int)] = velo_pts_im[:, 2]

    # find the duplicate points and choose the closest depth
    inds = sub2ind(depth.shape, velo_pts_im[:, 1], velo_pts_im[:, 0])
    #dupe_inds = [item for item, count in Counter(inds).iteritems() if count > 1]
    #NOTE: added by CCJ:
    # In python3, use dict.items() instead of dict.iteritems(), which was removed in python3;
    dupe_inds = [item for item, count in Counter(inds).items() if count > 1]
    for dd in dupe_inds:
        pts = np.where(inds==dd)[0]
        x_loc = int(velo_pts_im[pts[0], 0])
        y_loc = int(velo_pts_im[pts[0], 1])
        depth[y_loc, x_loc] = velo_pts_im[pts, 2].min()
    depth[depth<0] = 0

    if interp:
        # interpolate the depth map to fill in holes
        depth_interp = lin_interp(im_shape, velo_pts_im)
        return depth, depth_interp
    else:
        return depth, depth

def get_depth_from_velodyne(
    imgH, imgW,
    T_velo_to_cam2, # T^{cam2}_{velo}: the velodyne to rectified camera coordinate transforms matrix 4 x 4;
    K_cam2, # the camera intrinsics, 3 x 3
    velo_pts_raw, # list of points [x,y,z,reflectance]
    interp = False
    ):
    res = []

    # check velodyne points and remove all behind image plane (approximation)
    # each row of the velodyne data is forward, left, up, reflectance
    # i.e., (x, y, z, reflectance)
    velo_pts = [p for p in velo_pts_raw if p[0] >= 0]
    # which is eqivalent to `depth[depth<0] = 0`;
    
    for p in velo_pts:
        tmp = np.ones(4)
        tmp[0:3] = p[0:3]
        p_cam2 = T_velo_to_cam2.dot(tmp) # (4 x 4) x (4x1) ==> (4x1), [x,y,z,1]
        # exclude the last "1" of the homogenous coordinates:
        p_img2 = K_cam2.dot(p_cam2[:3]) # (3 x 3) x (3 x 1) ==> (3 x 1), [λu, λv, λ] and λ = depth z in cam2;
        # get λ(u, v, 1)^T = p_img2
        # ==> (u, v) = p_img2[0:2]/p_img2[2]
        p_img2[0:2] = p_img2[0:2] / p_img2[2]
        #p_img2[2] = p_cam2[2] # z in cam2, i.e., depth;
        res.append(p_img2)
    depth = np.zeros((imgH, imgW))
    count = np.zeros((imgH, imgW))
    for r in res:
        u,v,z = r[:] # u : x axis; v is along y axis;
        if 0 <= u < imgW and 0 <= v < imgH:
            # considering occlusion to assign small depth;
            depth[int(v), int(u)] = z if depth[int(v), int(u)] == 0 else min(z, depth[int(v), int(u)])
            count[int(v), int(u)] += 1

    #depth[depth<0] = 0
    # interpolate the depth map to fill in holes
    if interp:
        im_shape = [imgH, imgW]
        # check if in bounds
        res_inbound = [r for r in res if 0<=r[0]<imgW and 0<=r[1]<imgH]
        velo_pts_im = np.zeros((len(res_inbound), 3), np.float)
        velo_pts_im[:, :] = res_inbound[:][:]
        # use minus 1 to get the exact same value as KITTI matlab code
        # get (u, v) along x and y axis, respectively
        velo_pts_im[:, 0:2] = np.round(velo_pts_im[:, 0:2]) - 1
        depth_interp = lin_interp(im_shape, velo_pts_im)
        return depth_interp, count, res
    else:
        return depth, count, res


def get_rel_extrinsicM(ext_ref, ext_src):
    ''' Get the extrinisc matrix from ref_view to src_view '''
    return ext_src.dot( np.linalg.inv( ext_ref))

if __name__ == "__main__":

    # Change this to the directory where you store KITTI data
    my_base_path = '/media/ccjData3_HDD/datasets/kitti_raw/rawdata'
    # Specify the dataset to load
    date = '2011_09_26'
    drive = '0093'

    # Load the data. Optionally, specify the frame range to load.
    my_dataset = pykitti.raw(my_base_path, date, drive, 
                            #frames=range(0, 20, 5)
                            )
    
    # neural rgb2d paper:
    #delta_t = 5
    delta_t = 1
    cur_t = 2*delta_t
    #local_window = [cur_t - 2*delta_t, cur_t - delta_t, cur_t, cur_t + delta_t, cur_t + 2*delta_t]
    #names_local = [r'$I_{-2}$', r'$I_{-1}$', r'$I_{0}$', r'$I_{+1}$', r'$I_{+2}$']
    local_window = [cur_t - delta_t, cur_t, cur_t + delta_t]
    cur_t_idx = local_window.index(cur_t)
    print ("cur_t_idx = ", cur_t_idx)
    #names_local = [r'$I_{-1}$', r'$I_{0}$', r'$I_{+1}$']
    names_local = [r'$I_{%d}$'%(cur_t - delta_t), r'$Ref = I_{%d}$'%(cur_t), r'$I_{%d}$'%(cur_t+delta_t)]
    frames_local = [my_dataset.get_cam2(idx) for idx in local_window]
    #source_frames = [my_dataset.get_cam2(idx) for idx in local_window if idx != cur_t]
    ref_frame = my_dataset.get_cam2(cur_t)


    # Read velodyne [x,y,z,reflectance] scan at the specified index
    velo_pts_local = [my_dataset.get_velo(idx) for idx in local_window]


    f, ax = plt.subplots(3, len(local_window), figsize=(20, 10))
    for i, n in enumerate(names_local):
        ax[0, i].imshow(frames_local[i])
        ax[0, i].set_title('%s (cam2)'%n)
    
    T_velo_to_cam2_local = [my_dataset.calib.T_cam0_velo for idx in local_window]
    K_cam2 = my_dataset.calib.K_cam2 


    # pose, i.e., extrinsics E = [R | t]
    # my_dataset.oxts: List of OXTS packets and 6-dof poses as named tuples;
    #cam_relative_poses_local = [] # from ref to src;
    extM_local = []
    # IMU to camera #
    T_imu2cam = my_dataset.calib.T_cam2_imu # T^{cam}_{imu}, 4 x 4 matrix;
    for i, idx in enumerate(local_window):
        T_w_imu = my_dataset.oxts[idx].T_w_imu # T^{w}_{imu}, w: world; 4 x 4 matrix;
        # Extrinsic E = T^{cam}_{w} = T^{cam}_{imu} * T^{imu}_{w} = T^{cam}_{imu} * inv(T^{w}_{imu})
        extM = T_imu2cam.dot(np.linalg.inv(T_w_imu)) 
        extM_local.append(extM)
    
    extM_ref = extM_local[cur_t_idx]
    
    #for i, idx in enumerate(local_window):
        #if idx == cur_t: # ref img
        #    cam_relative_poses_local.append(np.eye(4))
        #else: # source imgs
        #    rel_extM = get_rel_extrinsicM(extM_ref, extM_local[i])
        #    cam_relative_poses_local.append(rel_extM)
    cam_relative_poses_local = [get_rel_extrinsicM(extM_ref, M) for M in extM_local]
    
    def warp_ref_to_src_extM_v1(
        img_ref, dep_ref, 
        extM_ref, extM_src, 
        K_ref, K_src,
        is_identy = False):
        if is_identy:
            return img_ref
        
        #homography
        height, width = img_ref.shape[0:2]
        #normal vector
        R_ref, t_ref = extM_ref[0:3, 0:3], extM_ref[0:3, 3:4]
        R_src, t_src = extM_src[0:3, 0:3], extM_src[0:3, 3:4]
        #fronto_direction = R_ref[2:3, :]
        fronto_direction = np.array([[.0, .0, 1.]]).astype(np.float32)
        c_ref = - np.dot(R_ref.T, t_ref)
        c_src = - np.dot(R_src.T, t_src)
        c_relative = c_src - c_ref

        # compute
        c_rel_n =  np.dot(c_relative, fronto_direction)
        I = np.eye(3)
        h1 = np.dot(K_src, R_src) 
        h3 = np.dot(R_ref.T, np.linalg.inv(K_ref))

        warped_img = np.zeros((height, width, 3), dtype=np.uint8) # color image
        for y in range(height):
            for x in range(width):
                d = dep_ref[y, x]
                if abs(d) > 1e-3:
                    h2 = I - c_rel_n/d
                    r = np.dot(np.dot(h1, h2), h3)
                    x_new, y_new = int(r[0, 0]/r[2, 0]), int(r[1, 0]/r[2, 0])
                    if 0<= x_new < width and 0<= y_new < height:
                        warped_img[y_new, x_new,:] = img_ref[y,x,:]
                        #print ("pixel (%d,%d) == warped ==> (%d, %d), val = %s" %(y,x,y_new,x_new,warped_img[y_new,x_new,:]))
        return warped_img

    
    def warp_ref_to_src_naive_v2(img_ref, dep_ref, pose_rel_ref_2_src, K_src, K_ref, is_identy = False):
        if is_identy:
            return img_ref
        
        #homography
        height, width = img_ref.shape[0:2]
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
        warped_img = np.zeros((height, width, 3), dtype=np.uint8) # color image
        for y in range(height):
            for x in range(width):
                d = dep_ref[y, x]
                if abs(d) > 1e-3:
                    H = h1 - h2/d
                    r = H.dot(np.array([[x], [y], [1]]))
                    x_new, y_new = int(r[0, 0]/r[2, 0]), int(r[1, 0]/r[2, 0])
                    if 0<= x_new < width and 0<= y_new < height:
                        warped_img[y_new, x_new,:] = img_ref[y,x,:]
                        #print ("pixel (%d,%d) == warped ==> (%d, %d), val = %s" %(y,x,y_new,x_new,warped_img[y_new,x_new,:]))
        return warped_img
    
    
    def warp_ref_to_src_naive(img_src, dep_ref, pose_rel_ref_2_src, K_src, K_ref, is_identy = False):
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
                        #print ("pixel (%d,%d) == warped ==> (%d, %d), val = %s" %(y,x,y_new,x_new,warped_img[y_new,x_new,:]))
        return warped_src




    #f2 = plt.figure()
    #ax2 = f2.add_subplot(100+10*len(local_window)+len(local_window))
    #f2, ax2 = plt.subplots(1, len(local_window))
    
    my_calib_path = os.path.join(my_base_path, date)
    my_drive = date + '_drive_' + drive + '_sync'
    my_velo_path = os.path.join(my_base_path, date, my_drive, 'velodyne_points/data')
    velo_files_local = [pjoin(my_velo_path, '%010d.bin'%idx) for idx in local_window]

    # warp
    img_ref_np = np.asarray(ref_frame)
    imgH, imgW = img_ref_np.shape[0:2] 
    dep_ref = generate_depth_map(
            calib_dir = pjoin(my_base_path, date), 
            velo_file_name = velo_files_local[cur_t_idx], 
            im_shape = [imgH, imgW], 
            cam=2, 
            #interp=False, 
            interp=True, 
            vel_depth=False)[1]

    for i, n in enumerate(names_local):
        imgW, imgH = frames_local[i].size # due to PIL Image
        depth, count, pts = get_depth_from_velodyne(imgH, imgW, 
        T_velo_to_cam2_local[i], 
        K_cam2,
        velo_pts_local[i], # list of points [x,y,z,reflectance]
        interp= True
        )
        ax[1, i].imshow(depth, cmap='gray')
        ax[1, i].set_title('Our depth from velodyne for %s (cam2)'%n)
        #ax[2, i].imshow(count, cmap='gray')
        #ax[2, i].set_title('count depth from velodyne for %s (cam2)'%n)
        
        _, depth_good = generate_depth_map(
            calib_dir = pjoin(my_base_path, date), 
            velo_file_name = velo_files_local[i], 
            im_shape = [imgH, imgW], 
            cam=2, 
            interp=False, 
            #interp=True, 
            vel_depth=False)
        #ax[2, i].imshow(depth_good, cmap='gray')
        #ax[2, i].set_title('good depth from velodyne for %s (cam2)'%n)
        
        if 1:
            warped_img = warp_ref_to_src_naive(
                img_ref_np, dep_ref, 
                pose_rel_ref_2_src = cam_relative_poses_local[i],
                K_src = K_cam2,
                K_ref = K_cam2,
                #is_identy= (i==cur_t_idx)
                )
        else:
            warped_img =  warp_ref_to_src_extM_v1(
                img_ref_np, dep_ref, 
                extM_ref = extM_local[cur_t_idx], 
                extM_src = extM_local[i], 
                K_ref = K_cam2, 
                K_src = K_cam2,
                is_identy = False)

        ax[2, i].imshow(warped_img)
        ax[2, i].set_title('warped ref to src view for %s (cam2)'%n)
        
        if 0:
            x_img = [p[0] for p in pts]
            y_img = [p[1] for p in pts]
            print (pts[15:20])
            print ("plot ax2[0,%d]"%i)
            ax2[i].scatter(x= x_img, y = y_img )
            ax2[i].set_title('scatter of img coordinates from velodyne for %s (cam2)'%n)
    
    
    if 0:
        f2 = plt.figure()
        ax2 = f2.add_subplot(111, projection='3d')
        # Plot every 100th point so things don't get too bogged down
        velo_range = range(0, velo_pts.shape[0], 100)
        ax2.scatter(velo_pts[velo_range, 0],
                    velo_pts[velo_range, 1],
                    velo_pts[velo_range, 2],
                    c = velo_pts[velo_range, 3],
                    cmap ='gray'
                )
        ax2.set_title('Third Velodyne scan (subsampled)')

    plt.show()