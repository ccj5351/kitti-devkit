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
		#'/media/ccjData2/GCNet/results/KT-raw/cbmvnet-gc-F8-RMSp-sf-epo26Based-epo30-4dsConv-k5-testKTRaw/disp-epo-023' 
		#'/media/ccjData2/GCNet/results/KT-raw/gcnet-F8-RMSp-sf-epo30-4dsConv-k5-testKTRaw/disp-epo-030'
		'/media/ccjData2/research-projects/GCNet/results/cbmvnet-gc-F8-RMSp-sfepo26-kt15epo300-4dsConv-k5-testKT15BenchSubmit/disp-epo-290'
		'/media/ccjData2/research-projects/GCNet/results/cbmvnet-gc-F8-RMSp-sfepo26-kt15epo300-4dsConv-k5-testKT15BenchSubmit/disp-epo-206'
		'/media/ccjData2/research-projects/GCNet/results/cbmvnet-gc-F8-RMSp-sfepo26-kt12epo300-4dsConv-k5-testKT12BenchSubmit/disp-epo-300'
		'/media/ccjData2/research-projects/GCNet/results/cbmvnet-gc-F8-RMSp-sfepo26-kt12epo300-4dsConv-k5-testKT12BenchSubmit/disp-epo-263'
		'/media/ccjData2/research-projects/GCNet/results/cbmvnet-gc-F8-RMSp-sfepo26-kt12epo300-4dsConv-k5-testKT12BenchSubmit/disp-epo-250'
		)

declare -a result_shas2=(
		'/media/ccjData2/research-projects/GCNet/results/cbmvnet-gc-F8-RMSp-sfepo26-kt15epo300-4dsConv-k5-testKT15BenchSubmit/disp-epo-290-png'
		'/media/ccjData2/research-projects/GCNet/results/cbmvnet-gc-F8-RMSp-sfepo26-kt15epo300-4dsConv-k5-testKT15BenchSubmit/disp-epo-206-png'
		'/media/ccjData2/research-projects/GCNet/results/cbmvnet-gc-F8-RMSp-sfepo26-kt12epo300-4dsConv-k5-testKT12BenchSubmit/disp-epo-300-png'
		'/media/ccjData2/research-projects/GCNet/results/cbmvnet-gc-F8-RMSp-sfepo26-kt12epo300-4dsConv-k5-testKT12BenchSubmit/disp-epo-263-png'
		'/media/ccjData2/research-projects/GCNet/results/cbmvnet-gc-F8-RMSp-sfepo26-kt12epo300-4dsConv-k5-testKT12BenchSubmit/disp-epo-250-png'
		)

flag=true
#flag=false
if [ "$flag" = true ]; then
	for idx in $(seq 2 4)
	do
		result_sha=${result_shas[idx]}
		result_sha2=${result_shas2[idx]}
		makeDir ${result_sha2}
		### pfm2png first;
		#echo "converting pfm to png disp"
    #for name in $(seq 599 1149)
    for name in $(seq 0 194)
		do 
			#img_name="$(printf "0%09d" "$name")"
			img_name="$(printf "%06d_10" "$name")"
			pfm_file="${result_sha}/${img_name}.pfm"
			png_file="${result_sha2}/${img_name}.png"
			echo "$pfm_file to $png_file"
			./build/pfmDisp2png $pfm_file $png_file
		done
	done
fi
