# !/usr/bin/env python3
# -*-coding:utf-8-*-
# @file: pick_disp_err.py
# @brief:
# @author: Changjiang Cai, ccai1@stevens.edu, caicj5351@gmail.com
# @version: 0.0.1
# @creation date: 26-04-2019
# @last modified: Fri 26 Apr 2019 07:22:18 PM EDT

import matplotlib.pyplot as plt

def show_2_imgs_2_row( imgs, img_names, cmap = ['gray']*4):
    fig = plt.figure()
    for i in range(0, len(imgs)):
        a = fig.add_subplot(2,2,i+1)
        imgplot = plt.imshow(imgs[i])
        a.set_title(img_names[i])
        #plt.colorbar(ticks=[0.1, 0.3,0.5,0.7], orientation='horizontal')
    plt.show()


# for KT15
base='/media/ccjData2/research-projects' 
