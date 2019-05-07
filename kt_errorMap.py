from __future__ import division
import numpy as np 
import scipy
from sklearn.feature_extraction import image
import os
import matplotlib.pyplot as plt
import sys
sys.path.append('/home/ccj/GCNet/src')
import pfmutil as pfm



data_root="/media/ccjData2/"
#kt12=True
kt12=False
if kt12:
    disp_path= data_root + "research-projects/kitti-devkit/results/cbmvnet-gc-F8-RMSp-sf-epo26Based-epo30-4dsConv-k5-testKT12/disp-epo-023/"
    disp_path= data_root + "research-projects/kitti-devkit/results/gcnet-F8-RMSp-sf-epo30-4dsConv-k5-testKT12/disp-epo-030/"
    gt_path= data_root + "datasets/KITTI-2012/training/disp_occ/"
    gt_path_noc= data_root + "datasets/KITTI-2012/training/disp_noc/"
    imgNum = 194
else:
    #disp_path= data_root + "research-projects/kitti-devkit/results/cbmvnet-gc-F8-RMSp-sf-epo26Based-epo30-4dsConv-k5-testKT15/disp-epo-023/"
    disp_path= data_root + "research-projects/kitti-devkit/results/cbmv-gc-F8-RMSp-KT15-epo1k-4dsConv-k5-testKT15/disp-epo-539/"
    gt_path= data_root + "datasets/KITTI-2015/training/disp_occ_0/"
    gt_path_noc= data_root + "datasets/KITTI-2015/training/disp_noc_0/"
    imgNum = 200

#result_path= disp_path + "error_map/"
#if not os.path.exists(result_path):
#    os.makedirs(result_path)

contents = os.listdir(disp_path)
contents.sort()
def save_png(data,path,cmap):
	norm = plt.Normalize(vmin=np.min(data), vmax=np.max(data))
	img = cmap(norm(data))
	plt.imsave(path, img)

#save_png(disp_init,"kitti15_img/init_disp.png",plt.cm.inferno)	


csv_file = os.path.join('/media/ccjData2/research-projects/kitti-devkit/results/tmp_err.csv')
print "write ", csv_file
with open( csv_file, 'a') as fwrite:
    for i in range(0, imgNum):
    #for i in range(0, 200):
    #for i in idx12:
	#disp = scipy.misc.imread( disp_path+contents[i]).astype(float)/256
        disp = pfm.load(disp_path+contents[i][:-4] + ".pfm")
        gt = scipy.misc.imread( gt_path+contents[i][:-4] + ".png" ).astype(float)/256
        gt_noc = scipy.misc.imread( gt_path_noc+contents[i][:-4] + ".png").astype(float)/256
        #plt.imshow(gt)
        #plt.show()
        #sys.exit()

	valid_all = np.greater(gt,0).astype(int)
	valid_noc = np.greater(gt_noc,0).astype(int)
	disp_all = disp*valid_all
	disp_noc = disp*valid_noc

	sum_all = np.sum(valid_all)
	all_res = np.greater( np.abs(disp_all-gt),3).astype(int)
	res_all = np.sum(all_res)/sum_all

	sum_noc = np.sum(valid_noc)
	noc_res = np.greater( np.abs(disp_noc-gt_noc),3).astype(int)
	res_noc = np.sum(noc_res)/sum_noc
        
        messg = '{},{:>.2f},{:>.2f}\n'.format(contents[i][0:-4], res_all*100, res_noc*100)
        print  '## {} : bad3-all: {:>.2f}%, , bad3-noc: {:>.2f}%'.format(contents[i][0:-4], res_all*100, res_noc*100)
        fwrite.write(messg)
        #fig, axes = plt.subplots(nrows=2)
        #axes[0].imshow(disp, cmap="inferno")
        #axes[1].imshow(all_res, cmap="gray")
        #plt.show()
        
        #save_png(disp, os.path.join(result_path, contents[i][:-4]+".png"), plt.cm.inferno)
        #save_png(all_res, os.path.join(result_path, 'bad3-all-binary-' + contents[i][:-4] + ".png"), plt.cm.gray)
        #all_res_abs = np.abs(disp_all-gt)*valid_all
        #save_png(all_res_abs, os.path.join(result_path, 'bad3-all-' + contents[i][:-4] + ".png"), plt.cm.jet)
