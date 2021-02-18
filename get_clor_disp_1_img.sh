gt_disp_file="/media/ccjData1_HDD/Dropbox/temporary-files/proposal-defense/cones/disp2.png"
gt_disp_pfm_file="/media/ccjData1_HDD/Dropbox/temporary-files/proposal-defense/cones/disp2.pfm"
#./build/pngDisp2pfm $gt_disp_file $gt_disp_pfm_file

input_disp_file="/media/ccjData1_HDD/Dropbox/temporary-files/proposal-defense/cones/im2.png"
output_disp_file="/media/ccjData1_HDD/Dropbox/temporary-files/proposal-defense/cones/disp2_clr.png"
./build/get_color_disp $gt_disp_pfm_file $input_disp_file $output_disp_file
