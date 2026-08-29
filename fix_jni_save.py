import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

includes = '#include "../../world/SaveManager.h"'
if includes not in text:
    text = text.replace('#include "../../core/Globals.h"', '#include "../../core/Globals.h"\n#include "../../world/SaveManager.h"')

bindings = """
extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeInitSave(JNIEnv* env, jclass clazz, jstring path) {
    const char* pathStr = env->GetStringUTFChars(path, nullptr);
    SaveManager::Init(pathStr);
    env->ReleaseStringUTFChars(path, pathStr);
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_example_MainActivity_nativeHasSave(JNIEnv* env, jclass clazz) {
    return SaveManager::HasSave();
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeLoadGame(JNIEnv* env, jclass clazz) {
    SaveManager::LoadGame();
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeNewGame(JNIEnv* env, jclass clazz) {
    SaveManager::NewGame();
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeSaveGame(JNIEnv* env, jclass clazz) {
    SaveManager::SaveGame();
}
"""

if "nativeInitSave" not in text:
    text += "\n" + bindings

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
