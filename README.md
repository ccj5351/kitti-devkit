# Updated KITTI devkit Code for Error Maps, Color Disparity Generation, and pfm2uint16png and uint16png2pfm Converting


## Change your disparity estimation:

Assuming your disparity prediciton is in `.pfm` format. KITTI devkit code accepts `PNG` disparity maps for evaluation. So firstly, coverting the `pfm` to `png` ones.

```
# line 43 in file kt_errorMap.sh
./build/pfmDisp2png $pfm_file $png_file
```

where, executable `pfmDisp2png` will convert source file `$pfm_file` to `$png_file`. The detailed commands are shown in file `kt_errorMap.sh`.
