import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

atlas_funcs = """
extern uint32_t externalAtlasPixels[256 * 256];
extern bool useExternalAtlas;

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeSetAtlasPixels(JNIEnv* env, jclass clazz, jintArray pixels) {
    env->GetIntArrayRegion(pixels, 0, 256 * 256, (jint*)externalAtlasPixels);
    useExternalAtlas = true;
}
"""

text = text + atlas_funcs

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
