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
isLogColor=false
declare -a result_shas=(
"cbmv-gc-F8-RMSp-KT15-epo1k-4dsConv-k5-testKT15"
#"gcnet-KT15-epo600-4dsConv-k5-testKT15"
#"cbmvnet-gc-F8-RMSp-sfM3kSimR-epo30-4dsConv-k5-testKT15"
#"cbmvnet-gc-F8-RMSp-sfF3kSimR-epo30-4dsConv-k5-testKT15"
#"gcnet-F8-RMSp-sfM3kSimR-epo30-4dsConv-k5-testKT15"
#"gcnet-F8-RMSp-sfF3k-epo31-4dsConv-k5-testKT15"
#"gcnet-F8-RMSp-sf-epo30-4dsConv-k5-testKT15" 
#"cbmvnet-gc-F8-RMSp-sf-epo26Based-epo30-4dsConv-k5-testKT15"
)

flag=true
#flag=false
if [ "$flag" = true ]; then
	for idx in $(seq 0 0)
	do
		result_sha=${result_shas[idx]}
		makeDir "./results/${result_sha}/disp_0"
		### pfm2png first;
		#echo "converting pfm to png disp"
    for name in $(seq 0 199)
		do 
			img_name="$(printf "%06d" "$name")_10"
			pfm_file="./results/${result_sha}/disp-epo-539/${img_name}.pfm"
			png_file="./results/${result_sha}/disp_0/${img_name}.png"
			echo "$pfm_file to $png_file"
			./build/pfmDisp2png $pfm_file $png_file
		done

		echo "Processing KT15: ${result_sha}"
		./build/evaluate_stereokt15 $result_sha $isLogColor
	done
fi


#### KT12
isLogColor=true
declare -a result_shas=(
"cbmvnet-gc-F8-RMSp-sfF3kSimR-epo30-4dsConv-k5-testKT12"
#"gcnet-F8-RMSp-sfF3kSimR-epo30-4dsConv-k5-testKT12"
#"gcnet-F8-RMSp-sf-epo30-4dsConv-k5-testKT12" 
#"cbmvnet-gc-F8-RMSp-sf-epo26Based-epo30-4dsConv-k5-testKT12"
)
#flag=true
flag=false
if [ "$flag" = true ]; then
	for idx in $(seq 0 0)
	do
		result_sha=${result_shas[idx]}
		makeDir "./results/${result_sha}/disp_0"
    for name in $(seq 0 193)
		do 
			img_name="$(printf "%06d" "$name")_10"
			pfm_file="./results/${result_sha}/disp-epo-027/${img_name}.pfm"
			png_file="./results/${result_sha}/disp_0/${img_name}.png"
			echo "$pfm_file to $png_file"
			./build/pfmDisp2png $pfm_file $png_file
		done
		echo "Processing KT12: ${result_sha}"
		./build/evaluate_stereokt12 $result_sha $isLogColor
	done
fi
