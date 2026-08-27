#include "Raycast.h"
#include "../core/Globals.h"
#include "../world/World.h"

void performRaycast(bool placeBlock) {
    float eyeY = isCrouching ? 1.3f : 1.8f;
    glm::vec3 pos = glm::vec3(playerX, playerY + eyeY, playerZ);
    
    glm::vec3 front;
    front.x = cos(glm::radians(cameraLookX)) * cos(glm::radians(cameraLookY));
    front.y = sin(glm::radians(cameraLookY));
    front.z = sin(glm::radians(cameraLookX)) * cos(glm::radians(cameraLookY));
    front = glm::normalize(front);
    
    glm::vec3 prevBlock(-1.0f);
    
    for (float i = 0; i < 8.0f; i += 0.1f) {
        glm::vec3 rayPos = pos + front * i;
        int bx = (int)floor(rayPos.x);
        int by = (int)floor(rayPos.y);
        int bz = (int)floor(rayPos.z);
        
        int cx = bx / CHUNK_SIZE;
        int cz = bz / CHUNK_SIZE;
        if (bx < 0 && bx % CHUNK_SIZE != 0) cx -= 1;
        if (bz < 0 && bz % CHUNK_SIZE != 0) cz -= 1;
        
        int lx = (bx % CHUNK_SIZE + CHUNK_SIZE) % CHUNK_SIZE;
        int lz = (bz % CHUNK_SIZE + CHUNK_SIZE) % CHUNK_SIZE;
        
        if (by >= 0 && by < CHUNK_HEIGHT) {
            std::lock_guard<std::mutex> lock(worldMutex);
            if (chunks.find({cx, cz}) != chunks.end() && chunks[{cx, cz}].state >= ChunkState::Generated) {
                uint8_t currentBlock = chunks[{cx, cz}].data[lx][by][lz];
                if (currentBlock != 0 && currentBlock != 6) { // solid block (not air, not water)
                    if (placeBlock) {
                        if (prevBlock.x != -1.0f) {
                            int pbx = (int)floor(prevBlock.x);
                            int pby = (int)floor(prevBlock.y);
                            int pbz = (int)floor(prevBlock.z);
                            
                            int pcx = pbx / CHUNK_SIZE;
                            int pcz = pbz / CHUNK_SIZE;
                            if (pbx < 0 && pbx % CHUNK_SIZE != 0) pcx -= 1;
                            if (pbz < 0 && pbz % CHUNK_SIZE != 0) pcz -= 1;
                            
                            int plx = (pbx % CHUNK_SIZE + CHUNK_SIZE) % CHUNK_SIZE;
                            int plz = (pbz % CHUNK_SIZE + CHUNK_SIZE) % CHUNK_SIZE;
                            
                            if (pby >= 0 && pby < CHUNK_HEIGHT && chunks.find({pcx, pcz}) != chunks.end()) {
                                glm::vec3 pSize = isCrouching ? glm::vec3(0.6f, 1.5f, 0.6f) : glm::vec3(0.6f, 1.8f, 0.6f);
                                bool intersectX = abs(playerX - (pbx + 0.5f)) * 2.0f < (pSize.x + 1.0f);
                                bool intersectY = abs((playerY + pSize.y/2.0f) - (pby + 0.5f)) * 2.0f < (pSize.y + 1.0f);
                                bool intersectZ = abs(playerZ - (pbz + 0.5f)) * 2.0f < (pSize.z + 1.0f);
                                if (!(intersectX && intersectY && intersectZ)) {
                                    if (hotbar[selectedHotbarSlot].count > 0) {
                                        chunks[{pcx, pcz}].data[plx][pby][plz] = hotbar[selectedHotbarSlot].blockType;
                                        chunks[{pcx, pcz}].isDirty = true;
                                        if (plx == 0 && chunks.find({pcx-1, pcz}) != chunks.end()) chunks[{pcx-1, pcz}].isDirty = true;
                                        if (plx == CHUNK_SIZE-1 && chunks.find({pcx+1, pcz}) != chunks.end()) chunks[{pcx+1, pcz}].isDirty = true;
                                        if (plz == 0 && chunks.find({pcx, pcz-1}) != chunks.end()) chunks[{pcx, pcz-1}].isDirty = true;
                                        if (plz == CHUNK_SIZE-1 && chunks.find({pcx, pcz+1}) != chunks.end()) chunks[{pcx, pcz+1}].isDirty = true;
                                        hotbar[selectedHotbarSlot].count--;
                                    }
                                }
                            }
                        }
                    } else {
                        chunks[{cx, cz}].data[lx][by][lz] = 0;
                        chunks[{cx, cz}].isDirty = true;
                        if (lx == 0 && chunks.find({cx-1, cz}) != chunks.end()) chunks[{cx-1, cz}].isDirty = true;
                        if (lx == CHUNK_SIZE-1 && chunks.find({cx+1, cz}) != chunks.end()) chunks[{cx+1, cz}].isDirty = true;
                        if (lz == 0 && chunks.find({cx, cz-1}) != chunks.end()) chunks[{cx, cz-1}].isDirty = true;
                        if (lz == CHUNK_SIZE-1 && chunks.find({cx, cz+1}) != chunks.end()) chunks[{cx, cz+1}].isDirty = true;
                        
                        // Try to add broken block to inventory
                        for (int k = 0; k < 5; k++) {
                            if (hotbar[k].blockType == currentBlock) {
                                hotbar[k].count++;
                                break;
                            } else if (hotbar[k].count == 0) {
                                hotbar[k].blockType = currentBlock;
                                hotbar[k].count = 1;
                                break;
                            }
                        }
                    }
                    workerCV.notify_one();
                    break;
                }
            }
        }
        prevBlock = rayPos;
    }
}

