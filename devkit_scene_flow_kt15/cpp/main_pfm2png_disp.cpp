/**
 * @file: main_pfm2png_disp.cpp
 * @brief:
 * @author: Changjiang Cai, ccai1@stevens.edu, caicj5351@gmail.com
 * @version: 0.0.1
 * @creation date: 05-06-2019
 * @last modified: Mon 06 May 2019 05:37:19 PM EDT
 */

#include <iostream>
#include "io_integer.h"
#include "io_disp.h"
#include "pfm_rw.h"

#include <string>
#include <vector>
#include <cmath> /*INFINITY*/

//#define INVALIDE_DISP -1.0f
using namespace std;

//************************************
//*** disparity from pfm to png ******
//************************************
inline void pfm2uint16PNG(
		std::string src,
		std::string dst
		){
	
	PFM pfmIO;
	float * p_disp = pfmIO.read_pfm<float>(src);
	// set the inf value to 0;
	const int w = pfmIO.getWidth();
	const int h = pfmIO.getHeight();
	// construct disparity image from data
	DisparityImage D_png( p_disp, w, h);
	D_png.write(dst);
	delete[] p_disp;
}

int main(int argc, char ** argv){
	if(argc != 3){
		cout << "Error arguments input. You should input parameters:\n"
			<< " * argv[1] : pfm_file\n"
			<< " * argv[2] : png_file\n";
		return 1;
	}
	
	string pfm_file = argv[1]; 
	string png_file = argv[2];
	pfm2uint16PNG(pfm_file, png_file);
	return 0;
}

