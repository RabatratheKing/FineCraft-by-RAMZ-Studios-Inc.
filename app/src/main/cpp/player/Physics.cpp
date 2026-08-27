#include "Physics.h"
#include "../core/Globals.h"
#include "../world/World.h"

bool checkCollision(glm::vec3 pos, glm::vec3 size) {
    int minX = floor(pos.x - size.x / 2.0f + 0.001f);
    int maxX = floor(pos.x + size.x / 2.0f - 0.001f);
    int minY = floor(pos.y + 0.001f);
    int maxY = floor(pos.y + size.y - 0.001f);
    int minZ = floor(pos.z - size.z / 2.0f + 0.001f);
    int maxZ = floor(pos.z + size.z / 2.0f - 0.001f);

    for (int x = minX; x <= maxX; x++) {
        for (int y = minY; y <= maxY; y++) {
            for (int z = minZ; z <= maxZ; z++) {
                if (isBlockSolid(x, y, z)) {
                    return true;
                }
            }
        }
    }
    return false;
}

void tickPhysics(float dt) {
    if (dt > 0.1f) dt = 0.1f;

    glm::vec3 size = isCrouching ? glm::vec3(0.6f, 1.5f, 0.6f) : glm::vec3(0.6f, 2.0f, 0.6f);
    
    if (isDebugFly) {
        glm::vec3 front;
        front.x = cos(glm::radians(cameraLookX));
        front.y = 0.0f;
        front.z = sin(glm::radians(cameraLookX));
        front = glm::normalize(front);
        glm::vec3 right = glm::normalize(glm::cross(front, glm::vec3(0.0f, 1.0f, 0.0f)));
        
        float speed = 20.0f * dt;
        playerX += (front.x * -inputMoveY + right.x * inputMoveX) * speed;
        playerZ += (front.z * -inputMoveY + right.z * inputMoveX) * speed;
        if (inputJump) playerY += speed;
        if (isCrouching) playerY -= speed;
        return;
    }
    
    playerVelocity.y += -25.0f * dt;

    if (isGrounded && inputJump) {
        playerVelocity.y = 8.5f;
        isGrounded = false;
    }

    glm::vec3 front;
    front.x = cos(glm::radians(cameraLookX));
    front.y = 0.0f;
    front.z = sin(glm::radians(cameraLookX));
    if (glm::length(front) > 0.001f) front = glm::normalize(front);
    else front = glm::vec3(0,0,1);
    
    glm::vec3 right = glm::normalize(glm::cross(front, glm::vec3(0.0f, 1.0f, 0.0f)));

    float currentSpeed = isCrouching ? 2.5f : 6.5f;
    glm::vec3 wishDir = front * -inputMoveY + right * inputMoveX;
    if (glm::length(wishDir) > 1.0f) wishDir = glm::normalize(wishDir);
    
    // Smooth acceleration/friction horizontally
    float friction = 10.0f;
    playerVelocity.x = glm::mix(playerVelocity.x, wishDir.x * currentSpeed, friction * dt);
    playerVelocity.z = glm::mix(playerVelocity.z, wishDir.z * currentSpeed, friction * dt);

    glm::vec3 pos(playerX, playerY, playerZ);
    
    pos.x += playerVelocity.x * dt;
    if (checkCollision(pos, size)) {
        pos.x -= playerVelocity.x * dt;
        playerVelocity.x = 0;
    }

    pos.y += playerVelocity.y * dt;
    if (checkCollision(pos, size)) {
        if (playerVelocity.y < 0) {
            pos.y = floor(pos.y) + 1.001f;
            isGrounded = true;
        } else if (playerVelocity.y > 0) {
            pos.y -= playerVelocity.y * dt;
        } else {
            pos.y -= playerVelocity.y * dt;
        }
        playerVelocity.y = 0;
    } else {
        isGrounded = false;
    }

    pos.z += playerVelocity.z * dt;
    if (checkCollision(pos, size)) {
        pos.z -= playerVelocity.z * dt;
        playerVelocity.z = 0;
    }

    playerX = pos.x;
    playerY = pos.y;
    playerZ = pos.z;
}

