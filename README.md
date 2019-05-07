# Updated KITTI devkit Code for Error Maps, Color Disparity Generation, and pfm2uint16png and uint16png2pfm Converting

## Compilation

The `CMakeLists.txt` file is provided for convenient compilation. Just run the following:

```
cd kitti-devkit # assuming its the root dir for this reporsitory
mkdir build
cd build
cmake ..
make
```

The compiled libraries or executables will be found at `./lib` and `./build` sub-directory, respectively.

## Change your pfm disparity to png format:

Assuming your disparity prediciton is in `.pfm` format. KITTI devkit code accepts `PNG` disparity maps for evaluation. So firstly, coverting the `pfm` to `png` ones.

```
# line 43 in file kt_errorMap.sh
./build/pfmDisp2png $pfm_file $png_file
```

where, executable `pfmDisp2png` will convert source file `$pfm_file` to target file `$png_file`. The detailed commands are shown in file `kt_errorMap.sh`.

## KITTI 2015 Evaluation for Error Maps and Color Disparities

Based on the png disparity maps, we can do evaluation, via:

```
# line 47 in file kt_errorMap.sh
./build/evaluate_stereokt15 $result_sha $isLogColor
```

where, `$result_sha` is the disparity input for evaluation, and `$isLogColor` is a flag for using KITTI LogColor (if isLogColor=true) or not (if isLogColor=false).
This will result in 
- the error maps at `errors_disp_img_0/`,
- the color disparity maps at `result_disp_img_0/`,

both under the same location as your input disparity maps for evaluation.

The following shows the input disparity, the color version disparity, error map (w/o and w/ log color), and the KITTI error scale:

- ![disp-input](./imgs/kt15_000002_10_input.png)
- ![disp-color](./imgs/kt15_000002_10_color.png)
- ![disp-err](./imgs/kt15_000002_10_errorMap.png)
- ![disp-err](./imgs/kt15_000002_10_logcolorErrorMap.png)
- ![err-scale](./imgs/kitti_scale.png)

## KITTI 2012 Evaluation for Error Maps and Color Disparities 

The KITTI 2012 evaluation code is a little different from that of KITTI 2015, w.r.t the generated error maps. 


