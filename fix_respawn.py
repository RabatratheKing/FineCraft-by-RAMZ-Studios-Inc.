import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

pattern = r'extern "C" JNIEXPORT void JNICALL Java_com_example_MainActivity_nativeRespawn\(JNIEnv\* env, jclass clazz\) \{.*?\n\}'

replacement = """extern "C" JNIEXPORT void JNICALL Java_com_example_MainActivity_nativeRespawn(JNIEnv* env, jclass clazz) {
    playerHealth = playerMaxHealth;
    isDead = false;
    playerVelocity = glm::vec3(0.0f);
    playerState = LocomotionState::STANDING;
    isCrouching = false;
    isSprinting = false;
    isCrawlingState = false;
    isInWater = false;
    isSubmerged = false;
    isClimbing = false;
    isGrounded = false;
    
    // Explicit camera reset
    cameraEyeY = 1.8f;
    bobAmount = 0.0f;
    bobTime = 0.0f;

    // Reset damage/fall state
    damageCooldown = 1.0f;
    hurtTime = 0.0f;
    fallDistance = 0.0f;

    // Default spawn near origin
    playerX = 0.5f;
    playerZ = 0.5f;
    
    int spawnY = 15; // default height at (0,0) is usually 14
    
    // If chunk at 0,0 is loaded, find true highest block to prevent spawning inside structures
    {
        std::lock_guard<std::mutex> lock(worldMutex);
        if (chunks.find({0, 0}) != chunks.end() && chunks[{0, 0}].state >= ChunkState::Generated) {
            for (int y = CHUNK_HEIGHT - 1; y >= 0; y--) {
                uint8_t b = chunks[{0, 0}].data[0][y][0];
                if (b != 0 && b != 6 && b != 10) { // Not air, water, scaffolding
                    spawnY = y + 1;
                    break;
                }
            }
        }
    }
    
    playerY = (float)spawnY + 0.01f;
    highestY = playerY;
}"""

text = re.sub(pattern, replacement, text, flags=re.DOTALL)

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
