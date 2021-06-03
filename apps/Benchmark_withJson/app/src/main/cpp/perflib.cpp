//
// Created by carlnues on 6/1/21.
//


#include <jni.h>

/*
extern "C" JNIEXPORT jint JNICALL
Java_com_example_benchmark_withjson_MainActivity_hello(JNIEnv *env, jobject instance) {

// Put your code here :)

    return (jint)77;

}
*/

/*

extern "C"
JNIEXPORT jstring JNICALL
Java_com_example_benchmark_1withjson_MainActivity_hello(JNIEnv *env, jobject thiz) {
    // TODO: implement hello()
}
*/


extern "C"
JNIEXPORT jint JNICALL
Java_com_example_benchmark_1withjson_MainActivity_hello(JNIEnv *env, jobject thiz, jint foo) {
    // TODO: implement hello()
    return (jint)(foo * 3 + 1);
}


