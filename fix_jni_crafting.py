import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

bindings = """
extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeSwapCraftingSlot(JNIEnv* env, jclass clazz, jint invSlot, jint craftSlot) {
    swapCraftingSlot(invSlot, craftSlot);
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeSwapCraftingToCrafting(JNIEnv* env, jclass clazz, jint craftSlotA, jint craftSlotB) {
    swapCraftingToCrafting(craftSlotA, craftSlotB);
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeTakeCraftingOutput(JNIEnv* env, jclass clazz) {
    takeCraftingOutput();
}

extern "C" JNIEXPORT jintArray JNICALL
Java_com_example_MainActivity_nativeGetCraftingGrid(JNIEnv* env, jclass clazz) {
    jintArray result = env->NewIntArray(4 * 2);
    jint temp[8];
    for (int i = 0; i < 4; i++) {
        temp[i*2] = craftingGrid[i].itemId;
        temp[i*2+1] = craftingGrid[i].count;
    }
    env->SetIntArrayRegion(result, 0, 8, temp);
    return result;
}

extern "C" JNIEXPORT jintArray JNICALL
Java_com_example_MainActivity_nativeGetCraftingOutput(JNIEnv* env, jclass clazz) {
    jintArray result = env->NewIntArray(2);
    jint temp[2] = { craftingOutput.itemId, craftingOutput.count };
    env->SetIntArrayRegion(result, 0, 2, temp);
    return result;
}
"""

if "nativeSwapCraftingSlot" not in text:
    text += "\n" + bindings

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
