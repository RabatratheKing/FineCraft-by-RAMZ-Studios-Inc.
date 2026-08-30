import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

impl = """
extern "C" JNIEXPORT jboolean JNICALL
Java_com_example_MainActivity_nativeMoveItems(JNIEnv* env, jclass clazz, jint srcType, jint srcSlot, jint destType, jint destSlot, jint amount) {
    return moveItems(srcType, srcSlot, destType, destSlot, amount);
}
"""
if "nativeMoveItems(" not in text:
    text += impl

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
