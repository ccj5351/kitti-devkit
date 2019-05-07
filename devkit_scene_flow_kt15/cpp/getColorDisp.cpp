#include <iostream>
#include <stdio.h>
#include <math.h>

#include "io_disp.h"
#include "io_integer.h"
#include "utils.h"

//added by CCJ
#include "pfm_rw.h"

using namespace std;

DisparityImage pfm2uint16PNG(std::string disp_pfm){
	PFM pfmIO;
	float * p_disp = pfmIO.read_pfm<float>(disp_pfm);
	const int w = pfmIO.getWidth();
	const int h = pfmIO.getHeight();
	cout << " w by h : " << w << " by " << h << "\n";
	for (int i = 0; i < w*h; ++i){
		// uint16 : 0 to 65535;
		// The maximum value for uint16 is 65535;
		//p_disp[i] = std::isinf(p_disp[i]) ? (uint16_t)65535 : p_disp[i];
		//p_disp[i] = std::isinf(p_disp[i]) ? -1 : p_disp[i];
		p_disp[i] = std::isinf(p_disp[i]) ? 0 : p_disp[i];
	}
	// construct disparity image from data
	DisparityImage D_pfm( p_disp, w, h);
	delete[] p_disp;
	return D_pfm;
}


int32_t main (int32_t argc,char *argv[]) {
  if (argc!=4) {
    cout << "Usage: ./getColorDisp gt_disp_file_pfm input_disp_file_pfm output_disp_file_png" << endl;
    return 1;
  }
  // read arguments
	string gt_disp_file = argv[1];
	string input_disp_file = argv[2];
  string output_disp_file = argv[3];
	
 	DisparityImage  D_gt_0 = pfm2uint16PNG(gt_disp_file);
	// load submitted result and interpolate missing values
  DisparityImage 	D_orig_0 = pfm2uint16PNG(input_disp_file);
	DisparityImage  D_ipol_0;
	D_ipol_0 = DisparityImage(D_orig_0);
	D_ipol_0.interpolateBackground();	

	cout << "read gt from " << gt_disp_file << "\n";
	cout << "read disp from " << input_disp_file << "\n";
	// compute maximum disparity
	float max_disp = D_gt_0.maxDisp();
	//float max_disp = D_ipol_0.maxDisp();
	cout << "max disp = " << max_disp << "\n";
	// save interpolated disparity image false color coded
	D_ipol_0.writeColor(output_disp_file,max_disp);
	cout << "Successfully saved " << output_disp_file << "\n";
  return 0;
}
