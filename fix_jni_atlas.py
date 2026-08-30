import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

bindings = """
extern uint32_t atlasPixelsARGB[256 * 256];
extern bool atlasGenerated;

extern "C" JNIEXPORT jintArray JNICALL
Java_com_example_MainActivity_nativeGetAtlasPixels(JNIEnv* env, jclass clazz) {
    if (!atlasGenerated) return nullptr;
    jintArray result = env->NewIntArray(256 * 256);
    env->SetIntArrayRegion(result, 0, 256 * 256, (const jint*)atlasPixelsARGB);
    return result;
}
"""

text += bindings

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
