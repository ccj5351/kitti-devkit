cd devkit_stereo_flow_kt12/cpp
#g++ -O3 -DNDEBUG -o evaluate_stereokt12 evaluate_stereo.cpp -lpng
cd ../../devkit_scene_flow_kt15/cpp
g++ -O3 -DNDEBUG -o evaluate_kt15 evaluate_scene_flow.cpp -lpng
g++ -O3 -DNDEBUG -o get_color_disp getColorDisp.cpp -lpng
