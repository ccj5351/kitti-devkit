project(kitti_devkit)
cmake_minimum_required(VERSION 2.8)
add_definitions(-std=c++14) # otherwise, error: ‘fabs’ was not declared in this scope

#set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/")
set(CMAKE_CXX_FLAGS "-Wall")
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -msse4.1 -march=core-avx2 -O3 -funroll-loops -ftree-vectorizer-verbose=1")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -msse4 -O3 -funroll-loops -ftree-vectorizer-verbose=1")

#set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Wall")
set(CMAKE_BUILD_TYPE Release)

set(OpenCV_DIR "/usr/local/opencv-3.2.0/share/OpenCV/")
find_package(OpenCV 3 REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS} 
        devkit_stereo_flow_kt12/
        devkit_scene_flow_kt15/
        pgm_pfm/
	# add the following line for vision 6 server
	#/usr/local/lib/python2.7/dist-packages/numpy/core/include
	)

SET(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)
#SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

add_library(pfmIO SHARED pgm_pfm/pfm_rw.cpp )
target_link_libraries( pfmIO ${OpenCV_LIBS} )

add_executable(pngDisp2pfm devkit_scene_flow_kt15/cpp/main_png2pfm_disp.cpp )
target_link_libraries( pngDisp2pfm pfmIO png)
add_executable(pfmDisp2png devkit_scene_flow_kt15/cpp/main_pfm2png_disp.cpp )
target_link_libraries( pfmDisp2png pfmIO png)

# change pfm disp to Kitti-color-space png disp;
add_executable(get_color_disp  devkit_scene_flow_kt15/cpp/getColorDisp.cpp )
target_link_libraries( get_color_disp pfmIO png)

# kt15 evaluation
add_executable(evaluate_stereokt15  devkit_scene_flow_kt15/cpp/evaluate_scene_flow.cpp)
target_link_libraries( evaluate_stereokt15 png)

# kt12 evaluation
add_executable(evaluate_stereokt12 devkit_stereo_flow_kt12/cpp/evaluate_stereo.cpp)
target_link_libraries( evaluate_stereokt12 png)
