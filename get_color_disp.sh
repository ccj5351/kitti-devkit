#t=14400
#echo "Hi, I'm sleeping for $t seconds..."
#sleep ${t}s
cd /media/ccjData2/research-projects/kitti-devkit
pwd

my_root="/media/ccjData2"
if [ ! -d $my_root ]; then
		my_root="/home/ccj"
    echo "Updated : setting my_root = ${my_root}"
fi


declare -a mbv3=('Adirondack' 'ArtL' 'Jadeplant' 'Motorcycle' 'MotorcycleE' 'Piano' 'PianoL' 'Pipes' 'Playroom' 'Playtable' 'PlaytableP' 'Recycle' 'Shelves' 'Teddy' 'Vintage')
declare -a eth3d=('delivery_area_1s' 'electro_1l' 'electro_2s' 'facade_1s' 'forest_1s' 'forest_2s' 'playground_1l' 'playground_1s' 'playground_2l' 'playground_3l' 
                  'playground_3s' 'terrains_1l' 'terrains_1s' 'terrains_2l' 'terrains_2s' 'playground_2s' 'delivery_area_3l' 'delivery_area_1l' 'delivery_area_3s' 
									'terrace_1s' 'terrace_2s' 'electro_2l' 'delivery_area_2l' 'delivery_area_2s' 'electro_1s' 'electro_3s' 'electro_3l')


declare -a testset=( "PlaytableP" "Recycle" "Shelves" "Teddy" "Vintage"
                     "Adirondack" "ArtL" "Jadeplant" "Motorcycle" "MotorcycleE"
										 "Piano" "PianoL" "Pipes" "Playroom" "Playtable" )



declare -a submitSet=( "Australia"  "AustraliaP"  "Bicycle2" "Classroom2" "Classroom2E"
                       "Computer"   "Crusade"     "CrusadeP"    "Djembe"		"DjembeL"
									 		 "Hoops"      "Livingroom" "Newkuba"    "Plants"      "Staircase")


##### function #####
function makeDir() {
	dstDir="$1"
	if [ ! -d $dstDir ]; then
		mkdir -p $dstDir
		echo "mkdir $dstDir"
	fi
}


#""" Middlebury Half size """
flag=false
#flag=true
app=./build/get_color_disp
if [ "$flag" = true ]; then
	echo "Processing Middlebury V3"
	tmpname="cbmvnet-gc-F8-RMSp-sf-epo26Based-epo30-4dsConv-k5-testMBV3/disp-epo-023"
	#tmpname="gcnet-F8-RMSp-sf-epo30-4dsConv-k5-testMBV3/disp-epo-030"

	for idx in $(seq 0 14)
	#for idx in $(seq 0 0)
	do
		cate=${mbv3[idx]}
		gt_disp_file="${my_root}/datasets/MiddleBury/MiddEval3/trainingH/${cate}/disp0GT.pfm"
		input_disp_file="./results/${tmpname}/${cate}.pfm"
		output_disp_file="$dstDir/${cate}.png"
		$app $gt_disp_file $input_disp_file $output_disp_file
	done
fi


#""" KT2015 """
#flag=false
flag=true
if [ "$flag" = true ]; then
	echo "Processing KT15"
	tmpname="cbmvnet-gc-F8-RMSp-sf-epo26Based-epo30-4dsConv-k5-testKT15/disp-epo-023"
	#tmpname="gcnet-F8-RMSp-sf-epo30-4dsConv-k5-testKT15/disp-epo-030"
	dstDir="./results/${tmpname}/color_disp"
	if [ ! -d $dstDir ]; then
		mkdir -p $dstDir
		echo "mkdir $dstDir"
	fi

	#for idx in $(seq 0 14)
	#for idx in $(seq 0 0)
	for idx in 104
	do
		cate=$(printf "%06d" "$idx")
		gt_disp_file="${my_root}/datasets/KITTI-2015/training/disp_occ_0_pfm/${cate}_10.pfm"
		input_disp_file="./results/${tmpname}/${cate}_10.pfm"
		input_disp_file="${my_root}/datasets/KITTI-2015/training/disp_occ_0_pfm/${cate}_10.pfm"
		output_disp_file="$dstDir/${cate}.png"
		$app $gt_disp_file $input_disp_file $output_disp_file
	done
fi
#if [ ! -d $dstDir ]; then
#		mkdir -p $dstDir
#		echo echo "mkdir $dstDir"
#fi
#for cate in "${testset[@]}"
#for cate in Vintage
