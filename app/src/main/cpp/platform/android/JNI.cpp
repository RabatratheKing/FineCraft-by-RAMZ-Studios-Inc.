#include <jni.h>
#include <string>
#include <android/native_window_jni.h>
#include "core/Globals.h"
#include "world/SaveManager.h"
#include "core/Logger.h"
#include "gameplay/Inventory.h"
#include "player/Physics.h"
#include "gameplay/Raycast.h"

#include "rendering/Renderer.h"
#include "world/ChunkManager.h"

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_MainActivity_stringFromJNI(
        JNIEnv* env,
        jobject /* this */) {
    std::string hello = "Hello from FineCraft C++ Engine";
    return env->NewStringUTF(hello.c_str());
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeSurfaceCreated(JNIEnv* env, jclass clazz, jobject surfaceObj) {
    {
        std::unique_lock<std::mutex> lock(windowMutex);
        if (currentWindow) {
            ANativeWindow_release(currentWindow);
        }
        currentWindow = ANativeWindow_fromSurface(env, surfaceObj);
        windowChanged = true;
    }
    
    if (!isRunning) {
        initInventory();
        isRunning = true;
        renderThread = std::thread(renderLoop);
        workerThread = std::thread(chunkWorkerLoop);
    }
    LOGI("Surface Created");
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeSurfaceChanged(JNIEnv* env, jclass clazz, jint w, jint h) {
    width = w;
    height = h;
    LOGI("Surface Changed: %dx%d", width, height);
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeSurfaceDestroyed(JNIEnv* env, jclass clazz) {
    {
        std::unique_lock<std::mutex> lock(windowMutex);
        if (currentWindow) {
            ANativeWindow_release(currentWindow);
            currentWindow = nullptr;
        }
        windowChanged = true;
        while (windowChanged && isRunning) {
            windowCV.wait_for(lock, std::chrono::milliseconds(50));
        }
    }
    LOGI("Surface Destroyed");
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeCameraLook(JNIEnv* env, jclass clazz, jfloat dx, jfloat dy) {
    float multY = settingInvertY ? -1.0f : 1.0f;
    if (!isInventoryOpen) {
        cameraLookX += dx * 0.5f * settingSensitivity;
        cameraLookY -= dy * 0.5f * settingSensitivity * multY;
    }
    if (cameraLookY > 89.0f) cameraLookY = 89.0f;
    if (cameraLookY < -89.0f) cameraLookY = -89.0f;
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeMoveJoystick(JNIEnv* env, jclass clazz, jfloat x, jfloat y) {
    if (!isInventoryOpen) {
        inputMoveX = x;
        inputMoveY = y;
    } else {
        inputMoveX = 0.0f;
        inputMoveY = 0.0f;
    }
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeAction(JNIEnv* env, jclass clazz, jstring action) {
    const char *actionStr = env->GetStringUTFChars(action, nullptr);
    if (isInventoryOpen) {
        // Only allow select slot when inventory is open, or nothing
        if (strncmp(actionStr, "select_slot_", 12) == 0) {
            int slot = actionStr[12] - '0';
            if (slot >= 0 && slot < HOTBAR_SIZE) {
                selectedHotbarSlot = slot;
            }
        }
        env->ReleaseStringUTFChars(action, actionStr);
        return;
    }
    
    if (strcmp(actionStr, "jump_down") == 0) {
        inputJump = true;
    } else if (strcmp(actionStr, "jump_up") == 0) {
        inputJump = false;
    } else if (strcmp(actionStr, "sneak") == 0) {
        if (isCrouching) {
            glm::vec3 standingSize = glm::vec3(0.6f, 2.0f, 0.6f);
            glm::vec3 pos = glm::vec3(playerX, playerY, playerZ);
            if (!checkCollision(pos, standingSize)) {
                isCrouching = false;
            }
        } else {
            isCrouching = true;
        }
    } else if (strcmp(actionStr, "debug_fly") == 0) {
        isDebugFly = !isDebugFly;
        playerVelocity = glm::vec3(0.0f);
    } else if (strcmp(actionStr, "place") == 0) {
        performRaycast(true);
    } else if (strcmp(actionStr, "break") == 0) {
        performRaycast(false);
    } else if (strncmp(actionStr, "select_slot_", 12) == 0) {
        int slot = actionStr[12] - '0';
        if (slot >= 0 && slot < HOTBAR_SIZE) {
            selectedHotbarSlot = slot;
        }
    }
    LOGI("Action: %s", actionStr);
    env->ReleaseStringUTFChars(action, actionStr);
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_MainActivity_nativeUpdateSettings(JNIEnv* env, jclass clazz, jfloat fov, jfloat sensitivity, jboolean invertY, jint renderDist, jint graphicsQuality, jboolean shadows, jboolean clouds, jboolean fog, jfloat brightness) {
    settingFOV = fov;
    settingSensitivity = sensitivity;
    settingInvertY = invertY;
    settingRenderDistance = renderDist;
    settingGraphicsQuality = graphicsQuality;
    settingShadows = shadows;
    settingClouds = clouds;
    settingFog = fog;
    settingBrightness = brightness;

    RenderRadius = renderDist;
    MeshRadius = renderDist + 1;
    LoadRadius = renderDist + 2;
    UnloadRadius = renderDist + 4;
}

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

extern uint32_t atlasPixelsARGB[256 * 256];
extern bool atlasGenerated;

extern "C" JNIEXPORT jintArray JNICALL
Java_com_example_MainActivity_nativeGetAtlasPixels(JNIEnv* env, jclass clazz) {
    if (!atlasGenerated) return nullptr;
    jintArray result = env->NewIntArray(256 * 256);
    env->SetIntArrayRegion(result, 0, 256 * 256, (const jint*)atlasPixelsARGB);
    return result;
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_example_MainActivity_nativeMoveItems(JNIEnv* env, jclass clazz, jint srcType, jint srcSlot, jint destType, jint destSlot, jint amount) {
    return moveItems(srcType, srcSlot, destType, destSlot, amount);
}
