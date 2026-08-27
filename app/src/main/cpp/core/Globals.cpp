#include "Globals.h"



std::atomic<bool> isRunning(false);
bool windowChanged = false;
std::mutex windowMutex;
std::condition_variable windowCV;
std::thread renderThread;
std::thread workerThread;
ANativeWindow* currentWindow = nullptr;
int width = 0;
int height = 0;



bool isDebugFly = false;
glm::vec3 playerVelocity(0.0f);
bool isGrounded = false;
bool isCrouching = false;
float inputMoveX = 0.0f;
float inputMoveY = 0.0f;
bool inputJump = false;



std::unordered_map<ChunkPos, Chunk, ChunkPosHash> chunks;
std::mutex worldMutex;

std::mutex queueMutex;
std::condition_variable workerCV;
std::vector<ChunkPos> generateQueue;
std::vector<ChunkPos> meshQueue;

std::mutex uploadMutex;
std::vector<GPUUploadJob> uploadQueue;
std::vector<GLuint> deleteQueueVAO;
std::vector<GLuint> deleteQueueVBO;

float cameraLookX = 0.0f;
float cameraLookY = 0.0f;

float playerX = 0.0f;
float playerY = 16.0f;
float playerZ = 0.0f;

float timeOfDay = 0.0f;

InventorySlot hotbar[5] = {
    {1, 64}, // Grass
    {2, 64}, // Dirt
    {3, 64}, // Stone
    {4, 64}, // Wood
    {8, 64}  // Sand
};
int selectedHotbarSlot = 0;

int LoadRadius = 8;
int MeshRadius = 6;
int RenderRadius = 5;
int UnloadRadius = 10;

float settingFOV = 75.0f;
float settingSensitivity = 1.0f;
bool settingInvertY = false;
int settingRenderDistance = 5;
int settingGraphicsQuality = 1;
bool settingShadows = true;
bool settingClouds = true;
bool settingFog = true;
float settingBrightness = 1.0f;
