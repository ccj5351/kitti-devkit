cd /media/ccjData2/research-projects/kitti-devkit/
pwd

##### function #####
function makeDir () {
	dstDir="$1"
	if [ ! -d $dstDir ]; then
		mkdir -p $dstDir
		echo "mkdir $dstDir"
	else
		echo $dstDir exists
	fi
}


#### KT15
declare -a result_shas=(
		'/media/ccjData2/GCNet/results/KT-raw/cbmvnet-gc-F8-RMSp-sf-epo26Based-epo30-4dsConv-k5-testKTRaw/disp-epo-023' 
		'/media/ccjData2/GCNet/results/KT-raw/gcnet-F8-RMSp-sf-epo30-4dsConv-k5-testKTRaw/disp-epo-030'
		)

flag=true
#flag=false
if [ "$flag" = true ]; then
	for idx in $(seq 0 0)
	do
		result_sha=${result_shas[idx]}
		### pfm2png first;
		#echo "converting pfm to png disp"
    for name in $(seq 599 1149)
		do 
			img_name="$(printf "0%09d" "$name")"
			pfm_file="${result_sha}/${img_name}.pfm"
			png_file="${result_sha}/${img_name}.png"
			echo "$pfm_file to $png_file"
			./build/pfmDisp2png $pfm_file $png_file
		done
	done
fi
