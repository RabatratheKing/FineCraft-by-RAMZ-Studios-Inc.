import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

# Add AAssetManager
imports = """#include "world/ChunkManager.h"
#include <android/asset_manager.h>
#include <android/asset_manager_jni.h>

AAssetManager* globalAssetManager = nullptr;
"""
text = text.replace('#include "world/ChunkManager.h"', imports)

# Update nativeInit
init_pattern = r'Java_com_example_MainActivity_nativeInitSave\(JNIEnv\* env, jclass clazz, jstring path\) \{.*?\}'
init_replacement = """Java_com_example_MainActivity_nativeInitSave(JNIEnv* env, jclass clazz, jstring path) {
    const char* pathStr = env->GetStringUTFChars(path, nullptr);
    SaveManager::Init(pathStr);
    env->ReleaseStringUTFChars(path, pathStr);
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeInit(JNIEnv* env, jclass clazz, jobject assetManager, jstring dataDir, jstring cacheDir) {
    if (assetManager != nullptr) {
        globalAssetManager = AAssetManager_fromJava(env, assetManager);
    }
}"""
text = re.sub(init_pattern, init_replacement, text, flags=re.DOTALL)

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
