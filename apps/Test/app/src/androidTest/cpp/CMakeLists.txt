
cmake_minimum_required(
	VERSION 3.10 )

add_library(
        perflib
        SHARED
        perflib.cpp )

find_library(
	log-lib
	log )

target_link_libraries(
	perflib
	${log-lib} )

