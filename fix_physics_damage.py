import re

with open("app/src/main/cpp/player/Physics.cpp", "r") as f:
    text = f.read()

pattern_headers = r'#include "../world/World.h"'
replacement_headers = """#include "../world/World.h"
#include <algorithm>
"""
if "#include <algorithm>" not in text:
    text = text.replace(pattern_headers, replacement_headers)

apply_damage_func = """
void applyDamage(float amount, const char* source) {
    if (isDead || isDebugFly) return;
    if (damageCooldown > 0.0f) return;
    
    playerHealth -= amount;
    if (playerHealth <= 0.0f) {
        playerHealth = 0.0f;
        isDead = true;
        playerState = LocomotionState::DEAD;
    } else {
        hurtTime = 0.5f;
        damageCooldown = 0.5f;
    }
}
"""

if "void applyDamage" not in text:
    text = text.replace("void tickPhysics(float dt) {", apply_damage_func + "\nvoid tickPhysics(float dt) {")

# Add death check at start of tickPhysics
pattern_dt = r'void tickPhysics\(float dt\) \{\n\s*if \(dt > 0\.1f\) dt = 0\.1f;'
replacement_dt = """void tickPhysics(float dt) {
    if (dt > 0.1f) dt = 0.1f;
    
    if (damageCooldown > 0.0f) damageCooldown -= dt;
    if (hurtTime > 0.0f) hurtTime -= dt;

    if (isDead) {
        playerState = LocomotionState::DEAD;
        playerVelocity.x = 0;
        playerVelocity.z = 0;
        // Still apply gravity
        playerVelocity.y -= 28.0f * dt;
        glm::vec3 pos(playerX, playerY, playerZ);
        pos.y += playerVelocity.y * dt;
        glm::vec3 size(0.6f, 0.6f, 0.6f); // Crawling size for dead player? or just let them fall
        if (checkCollision(pos, size)) {
            if (playerVelocity.y < 0) {
                pos.y = floor(pos.y) + 1.001f;
            }
            playerVelocity.y = 0;
        }
        playerY = pos.y;
        
        // Lower camera
        cameraEyeY = glm::mix(cameraEyeY, 0.2f, 10.0f * dt);
        bobAmount = glm::mix(bobAmount, 0.0f, 10.0f * dt);
        return;
    }"""
if "if (isDead) {" not in text:
    text = re.sub(pattern_dt, replacement_dt, text)

# Add fall damage tracking
pattern_fall = r'\} else \{\n\s*isGrounded = false;\n\s*\}'
replacement_fall = """} else {
        isGrounded = false;
    }
    
    // Fall damage logic
    if (playerState == LocomotionState::SWIMMING || playerState == LocomotionState::CLIMBING || isDebugFly) {
        highestY = pos.y;
    } else if (!isGrounded && playerVelocity.y < 0) {
        if (pos.y > highestY) highestY = pos.y;
    } else if (isGrounded) {
        if (highestY > pos.y) {
            float fallDist = highestY - pos.y;
            if (fallDist >= 3.0f) {
                float damage = fallDist - 3.0f;
                applyDamage(damage, "fall");
            }
        }
        highestY = pos.y;
    }"""
if "Fall damage logic" not in text:
    text = re.sub(pattern_fall, replacement_fall, text)

with open("app/src/main/cpp/player/Physics.cpp", "w") as f:
    f.write(text)
