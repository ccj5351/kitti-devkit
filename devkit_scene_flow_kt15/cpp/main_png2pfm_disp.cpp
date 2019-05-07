/**
 * @file: main_int_disp2pfm.cpp
 * @brief:
 * @author: Changjiang Cai, ccai1@stevens.edu, caicj5351@gmail.com
 * @version: 0.0.1
 * @creation date: 28-06-2017
 * @last modified: Mon 06 May 2019 04:47:25 PM EDT
 */
#include <iostream>
#include "io_disp.h"
#include "pfm_rw.h"
#include <string>
#include <vector>
#include <cmath> /*INFINITY*/

#define INVALIDE_DISP -1.0f
using namespace std;

int main(int argc, char ** argv){
	if(argc != 3){
		cout << "Error arguments input. You should input parameters:\n"
			<< " * argv[1] : png_file\n"
			<< " * argv[2] : pfm_file\n";
		return 1;
	}
		 
	string png_file = argv[1];
        string pfm_file = argv[2];
	DisparityImage pngDispIO;
	PFM pfmIO;
	float max_disp = -100.0f;

	pngDispIO.read(png_file);
	const int h = pngDispIO.height();
	const int w = pngDispIO.width();
	pfmIO.setHeight(h);
	pfmIO.setWidth(w);
	const int k = h*w;
	float * p_disp_gt = new float [k];
	float valMax = -1.0f;
	for (int j =0; j < k; ++j){
		float val = pngDispIO.data()[j];
		valMax = (valMax < val) ? val : valMax;
		p_disp_gt[j] = (val == INVALIDE_DISP)? INFINITY : val;
	}
  //cout << "Max value = " << valMax << "\t";
	max_disp = (max_disp < valMax)? valMax : max_disp;
	pfmIO.write_pfm(pfm_file, p_disp_gt, 1.0f );
	cout << "Saving " << pfm_file << ", max disparity = " << max_disp << "\n";
	delete [] p_disp_gt;
	return 0;
}
