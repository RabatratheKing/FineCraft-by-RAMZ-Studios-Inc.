import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

text = text.replace('#include "core/Logger.h"', '#include "core/Logger.h"\n#include "gameplay/Inventory.h"')

pattern = r"\} else if \(strncmp\(actionStr, \"select_slot_\", 12\) == 0\) \{[\s\S]*?\}"
replacement = """} else if (strncmp(actionStr, "select_slot_", 12) == 0) {
        int slot = actionStr[12] - '0';
        if (slot >= 0 && slot < HOTBAR_SIZE) {
            selectedHotbarSlot = slot;
        }
    }"""
text = re.sub(pattern, replacement, text)

# Add extra JNI functions for inventory sync
extra_jni = """
extern "C" JNIEXPORT jintArray JNICALL
Java_com_example_MainActivity_nativeGetInventory(JNIEnv* env, jclass clazz) {
    jintArray result = env->NewIntArray(INVENTORY_SIZE * 2);
    jint fill[INVENTORY_SIZE * 2];
    for (int i = 0; i < INVENTORY_SIZE; i++) {
        fill[i*2] = inventory[i].itemId;
        fill[i*2+1] = inventory[i].count;
    }
    env->SetIntArrayRegion(result, 0, INVENTORY_SIZE * 2, fill);
    return result;
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeSwapSlots(JNIEnv* env, jclass clazz, jint slotA, jint slotB) {
    swapSlots(slotA, slotB);
}

extern "C" JNIEXPORT jint JNICALL
Java_com_example_MainActivity_nativeGetSelectedHotbarSlot(JNIEnv* env, jclass clazz) {
    return selectedHotbarSlot;
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeSetInventoryOpen(JNIEnv* env, jclass clazz, jboolean open) {
    isInventoryOpen = open;
}
"""

text += extra_jni

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
