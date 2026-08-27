#include <jni.h>
#include <string>
#include <android/log.h>
#include <android/native_window_jni.h>
#include <EGL/egl.h>
#include <GLES3/gl3.h>
#include <thread>
#include <atomic>
#include <unistd.h>
#include <math.h>
#include <vector>
#include <unordered_map>
#include <mutex>
#include <condition_variable>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

#include "core/Logger.h"
#include "shaders/Shaders.h"

#include "core/Globals.h"
#include "rendering/Renderer.h"
#include "world/World.h"
#include "player/Physics.h"
#include "gameplay/Raycast.h"
#include "world/ChunkManager.h"










GLuint compileShader(GLenum type, const char* source) {
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, nullptr);
    glCompileShader(shader);
    GLint success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetShaderInfoLog(shader, 512, nullptr, infoLog);
        LOGE("Shader compilation failed: %s", infoLog);
    }
    return shader;
}

void generateTextureAtlas(GLuint& texID) {
    int size = 256;
    uint8_t* pixels = new uint8_t[size * size * 4];
    
    for(int y=0; y<size; ++y) {
        for(int x=0; x<size; ++x) {
            int tx = x / 16;
            int ty = y / 16;
            int tileIndex = ty * 16 + tx;
            
            int p = (y * size + x) * 4;
            
            int noise = (rand() % 20) - 10;
            int r=255, g=255, b=255;
            
            if (tileIndex == 0) { // Grass top
                r = 45; g = 145; b = 45;
                if ((x+y)%2 == 0) { r-=5; g-=5; }
            } else if (tileIndex == 1) { // Grass side
                if (y % 16 < 3) { r = 45; g = 145; b = 45; noise=(rand()%10)-5;}
                else if (y % 16 == 3 && x % 2 == 0) { r = 45; g = 145; b = 45; noise=(rand()%10)-5;}
                else { r = 120; g = 80; b = 50; }
            } else if (tileIndex == 2) { // Dirt
                r = 120; g = 80; b = 50;
            } else if (tileIndex == 3) { // Stone
                r = 130; g = 130; b = 130;
                if (rand()%10 == 0) { r+=15; g+=15; b+=15; }
                if (rand()%10 == 0) { r-=15; g-=15; b-=15; }
            } else if (tileIndex == 4) { // Wood side
                r = 110; g = 70; b = 40;
                if (x % 4 == 0) { r-=15; g-=15; b-=15; }
                noise = (rand()%10)-5;
            } else if (tileIndex == 5) { // Wood top
                r = 160; g = 120; b = 80;
                if ((x%16-8)*(x%16-8) + (y%16-8)*(y%16-8) < 16) { r-=20; g-=20; b-=20; }
            } else if (tileIndex == 6) { // Leaves
                r = 30; g = 100; b = 30;
                if ((x+y)%2==0) { r+=15; g+=15; b+=10; }
                if ((x*y)%3==0) { r-=10; g-=10; }
            } else if (tileIndex == 7) { // Water
                r = 40; g = 140; b = 210;
                noise = (rand()%10)-5;
            } else if (tileIndex == 8) { // Sand
                r = 230; g = 210; b = 150;
                noise = (rand()%15)-7;
            } else {
                r = 255; g = 0; b = 255; // pink missing tex
            }
            
            r = std::min(255, std::max(0, r + noise));
            g = std::min(255, std::max(0, g + noise));
            b = std::min(255, std::max(0, b + noise));
            
            pixels[p] = r;
            pixels[p+1] = g;
            pixels[p+2] = b;
            pixels[p+3] = 255;
        }
    }
    
    glGenTextures(1, &texID);
    glBindTexture(GL_TEXTURE_2D, texID);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    
    delete[] pixels;
}

void renderLoop() {
    EGLDisplay display = eglGetDisplay(EGL_DEFAULT_DISPLAY);
    eglInitialize(display, nullptr, nullptr);
    
    const EGLint attribs[] = {
        EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT,
        EGL_BLUE_SIZE, 8,
        EGL_GREEN_SIZE, 8,
        EGL_RED_SIZE, 8,
        EGL_DEPTH_SIZE, 16,
        EGL_NONE
    };
    
    EGLConfig config;
    EGLint numConfigs;
    eglChooseConfig(display, attribs, &config, 1, &numConfigs);
    
    const EGLint contextAttribs[] = {
        EGL_CONTEXT_CLIENT_VERSION, 3,
        EGL_NONE
    };
    EGLContext context = eglCreateContext(display, config, nullptr, contextAttribs);
    
    EGLSurface surface = EGL_NO_SURFACE;

    bool resourcesLoaded = false;
    GLuint shaderProgram;
    GLuint skyShaderProgram;
    GLuint atlasTex = 0;
    GLuint VBO, VAO;
    GLint projLoc = -1;
    GLint viewLoc = -1;
    GLint modelLoc = -1;
    GLint sunDirLoc = -1;
    GLint sunColorLoc = -1;
    GLint horizonColorLoc = -1;
    GLint zenithColorLoc = -1;
    GLint cameraPosLoc = -1;
    GLint uUseFogLoc = -1;
    GLint uUseShadowsLoc = -1;
    GLint uUseCloudsLoc = -1;
    GLint uBrightnessLoc = -1;
    GLint skyBrightnessLoc = -1;
    
    GLint skyInvProjViewLoc = -1;
    GLint skySunDirLoc = -1;
    GLint skyHorizonColorLoc = -1;
    GLint skyZenithColorLoc = -1;
    GLint skySunColorLoc = -1;
    GLint skyTimeLoc = -1;
    GLint skyCameraPosLoc = -1;
    
    auto lastTime = std::chrono::high_resolution_clock::now();

    while (isRunning) {
        auto currentTime = std::chrono::high_resolution_clock::now();
        float dt = std::chrono::duration<float>(currentTime - lastTime).count();
        lastTime = currentTime;
        
        tickPhysics(dt);

        bool hasWindow = false;
        {
            std::unique_lock<std::mutex> lock(windowMutex);
            if (windowChanged) {
                if (surface != EGL_NO_SURFACE) {
                    eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
                    eglDestroySurface(display, surface);
                    surface = EGL_NO_SURFACE;
                }
                if (currentWindow) {
                    surface = eglCreateWindowSurface(display, config, currentWindow, nullptr);
                }
                windowChanged = false;
                windowCV.notify_all();
            }
            hasWindow = (surface != EGL_NO_SURFACE);
        }

        if (hasWindow) {
            eglMakeCurrent(display, surface, surface, context);
            
            if (!resourcesLoaded) {
                GLuint vertexShader = compileShader(GL_VERTEX_SHADER, vertexShaderSource);
                GLuint fragmentShader = compileShader(GL_FRAGMENT_SHADER, fragmentShaderSource);
                shaderProgram = glCreateProgram();
                glAttachShader(shaderProgram, vertexShader);
                glAttachShader(shaderProgram, fragmentShader);
                glLinkProgram(shaderProgram);
                glDeleteShader(vertexShader);
                glDeleteShader(fragmentShader);
                
                GLuint skyVS = compileShader(GL_VERTEX_SHADER, skyVertexShaderSource);
                GLuint skyFS = compileShader(GL_FRAGMENT_SHADER, skyFragmentShaderSource);
                skyShaderProgram = glCreateProgram();
                glAttachShader(skyShaderProgram, skyVS);
                glAttachShader(skyShaderProgram, skyFS);
                glLinkProgram(skyShaderProgram);
                glDeleteShader(skyVS);
                glDeleteShader(skyFS);
                
                generateTextureAtlas(atlasTex);
                glUseProgram(shaderProgram);
                glUniform1i(glGetUniformLocation(shaderProgram, "atlas"), 0);
                
                projLoc = glGetUniformLocation(shaderProgram, "projection");
                viewLoc = glGetUniformLocation(shaderProgram, "view");
                modelLoc = glGetUniformLocation(shaderProgram, "model");
                sunDirLoc = glGetUniformLocation(shaderProgram, "sunDir");
                sunColorLoc = glGetUniformLocation(shaderProgram, "sunColor");
                horizonColorLoc = glGetUniformLocation(shaderProgram, "horizonColor");
                zenithColorLoc = glGetUniformLocation(shaderProgram, "zenithColor");
                cameraPosLoc = glGetUniformLocation(shaderProgram, "cameraPos");
                uUseFogLoc = glGetUniformLocation(shaderProgram, "u_useFog");
                uUseShadowsLoc = glGetUniformLocation(shaderProgram, "u_useShadows");
                uBrightnessLoc = glGetUniformLocation(shaderProgram, "u_brightness");
                
                skyInvProjViewLoc = glGetUniformLocation(skyShaderProgram, "invProjView");
                skySunDirLoc = glGetUniformLocation(skyShaderProgram, "sunDir");
                skyHorizonColorLoc = glGetUniformLocation(skyShaderProgram, "horizonColor");
                skyZenithColorLoc = glGetUniformLocation(skyShaderProgram, "zenithColor");
                skySunColorLoc = glGetUniformLocation(skyShaderProgram, "sunColor");
                skyTimeLoc = glGetUniformLocation(skyShaderProgram, "time");
                skyCameraPosLoc = glGetUniformLocation(skyShaderProgram, "cameraPos");
                uUseCloudsLoc = glGetUniformLocation(skyShaderProgram, "u_useClouds");
                skyBrightnessLoc = glGetUniformLocation(skyShaderProgram, "u_brightness");

                glEnable(GL_DEPTH_TEST);
                
                resourcesLoaded = true;
            }

            glViewport(0, 0, width, height);
            
            timeOfDay += 0.002f;
            float sunH = sin(timeOfDay);
            
            // Sky gradient calculation
            glm::vec3 zenithNight = glm::vec3(0.02f, 0.03f, 0.08f);
            glm::vec3 zenithDay = glm::vec3(0.15f, 0.4f, 0.9f);
            glm::vec3 zenithColor = glm::mix(zenithNight, zenithDay, glm::clamp(sunH + 0.3f, 0.0f, 1.0f));
            
            glm::vec3 horizonNight = glm::vec3(0.05f, 0.06f, 0.12f);
            glm::vec3 horizonSunrise = glm::vec3(0.9f, 0.4f, 0.2f);
            glm::vec3 horizonDay = glm::vec3(0.6f, 0.8f, 1.0f);
            
            glm::vec3 horizonColor;
            if (sunH < -0.2f) {
                horizonColor = horizonNight;
            } else if (sunH < 0.2f) {
                float t = (sunH + 0.2f) / 0.4f; // 0 to 1
                if (t < 0.5f) horizonColor = glm::mix(horizonNight, horizonSunrise, t * 2.0f);
                else horizonColor = glm::mix(horizonSunrise, horizonDay, (t - 0.5f) * 2.0f);
            } else {
                horizonColor = horizonDay;
            }
            
            glm::vec3 sunColor = glm::mix(glm::vec3(1.0f, 0.5f, 0.2f), glm::vec3(1.0f, 1.0f, 1.0f), glm::clamp(sunH * 2.0f, 0.0f, 1.0f));
            glm::vec3 sunDir = glm::normalize(glm::vec3(cos(timeOfDay), sin(timeOfDay), 0.5f));
            
            // Make moon light at night
            if (sunH < -0.1f) {
                sunColor = glm::vec3(0.1f, 0.15f, 0.25f);
                sunDir = glm::normalize(glm::vec3(cos(timeOfDay + 3.14159f), sin(timeOfDay + 3.14159f), 0.5f));
            } else if (sunH < 0.1f) {
                // Transition light intensity
                float t = (sunH + 0.1f) / 0.2f;
                sunColor = glm::mix(glm::vec3(0.1f, 0.15f, 0.25f), sunColor, t);
            }
            
            glClearColor(horizonColor.r, horizonColor.g, horizonColor.b, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
            
            glm::mat4 projection = glm::perspective(glm::radians(settingFOV), (float)width / (float)height, 0.1f, 100.0f);
            
            float eyeY = isCrouching ? 1.3f : 1.8f;
            glm::vec3 cameraPos = glm::vec3(playerX, playerY + eyeY, playerZ);
            
            glm::vec3 front;
            front.x = cos(glm::radians(cameraLookX)) * cos(glm::radians(cameraLookY));
            front.y = sin(glm::radians(cameraLookY));
            front.z = sin(glm::radians(cameraLookX)) * cos(glm::radians(cameraLookY));
            glm::vec3 cameraFront = glm::normalize(front);
            
            glm::vec3 cameraUp    = glm::vec3(0.0f, 1.0f, 0.0f);
            
            glm::mat4 view = glm::lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
            glm::mat4 invProjView = glm::inverse(projection * view);
            
            // Draw Sky Quad
            glDisable(GL_DEPTH_TEST);
            glDepthMask(GL_FALSE);
            glUseProgram(skyShaderProgram);
            if (skyInvProjViewLoc != -1) glUniformMatrix4fv(skyInvProjViewLoc, 1, GL_FALSE, glm::value_ptr(invProjView));
            if (skySunDirLoc != -1) glUniform3fv(skySunDirLoc, 1, glm::value_ptr(sunDir));
            if (skyHorizonColorLoc != -1) glUniform3fv(skyHorizonColorLoc, 1, glm::value_ptr(horizonColor));
            if (skyZenithColorLoc != -1) glUniform3fv(skyZenithColorLoc, 1, glm::value_ptr(zenithColor));
            if (skySunColorLoc != -1) glUniform3fv(skySunColorLoc, 1, glm::value_ptr(sunColor));
            if (skyTimeLoc != -1) glUniform1f(skyTimeLoc, timeOfDay * 10.0f);
            if (skyCameraPosLoc != -1) glUniform3fv(skyCameraPosLoc, 1, glm::value_ptr(cameraPos));
            glUniform1i(uUseCloudsLoc, settingClouds ? 1 : 0);
            glUniform1f(skyBrightnessLoc, settingBrightness);
            
            // Draw 1 full screen triangle
            glDrawArrays(GL_TRIANGLES, 0, 3);
            
            glEnable(GL_DEPTH_TEST);
            glDepthMask(GL_TRUE);
            
            // Draw Terrain
            glUseProgram(shaderProgram);
            glActiveTexture(GL_TEXTURE0);
            glBindTexture(GL_TEXTURE_2D, atlasTex);
            
            glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm::value_ptr(projection));
            glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
            if (modelLoc != -1) glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(glm::mat4(1.0f)));
            if (sunDirLoc != -1) glUniform3fv(sunDirLoc, 1, glm::value_ptr(sunDir));
            if (sunColorLoc != -1) glUniform3fv(sunColorLoc, 1, glm::value_ptr(sunColor));
            if (horizonColorLoc != -1) glUniform3fv(horizonColorLoc, 1, glm::value_ptr(horizonColor));
            if (zenithColorLoc != -1) glUniform3fv(zenithColorLoc, 1, glm::value_ptr(zenithColor));
            if (cameraPosLoc != -1) glUniform3fv(cameraPosLoc, 1, glm::value_ptr(cameraPos));
            glUniform1i(uUseFogLoc, settingFog ? 1 : 0);
            glUniform1i(uUseShadowsLoc, settingShadows ? 1 : 0);
            glUniform1f(uBrightnessLoc, settingBrightness);

            std::vector<GPUUploadJob> localUploads;
            std::vector<GLuint> vaosToDelete;
            std::vector<GLuint> vbosToDelete;
            {
                std::lock_guard<std::mutex> upLock(uploadMutex);
                int uploadsThisFrame = 0;
                while (!uploadQueue.empty() && uploadsThisFrame < 4) {
                    localUploads.push_back(std::move(uploadQueue.front()));
                    uploadQueue.erase(uploadQueue.begin());
                    uploadsThisFrame++;
                }
                
                vaosToDelete = std::move(deleteQueueVAO);
                vbosToDelete = std::move(deleteQueueVBO);
                deleteQueueVAO.clear();
                deleteQueueVBO.clear();
            }

            for (auto& job : localUploads) {
                std::lock_guard<std::mutex> worldLock(worldMutex);
                auto it = chunks.find(job.pos);
                if (it != chunks.end()) {
                    if (it->second.VAO != 0) {
                        vaosToDelete.push_back(it->second.VAO);
                        vbosToDelete.push_back(it->second.VBO);
                    }
                    glGenVertexArrays(1, &it->second.VAO);
                    glGenBuffers(1, &it->second.VBO);
                    
                    glBindVertexArray(it->second.VAO);
                    glBindBuffer(GL_ARRAY_BUFFER, it->second.VBO);
                    glBufferData(GL_ARRAY_BUFFER, job.meshData.size() * sizeof(float), job.meshData.data(), GL_STATIC_DRAW);
                    
                    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 10 * sizeof(float), (void*)0);
                    glEnableVertexAttribArray(0);

                    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 10 * sizeof(float), (void*)(3 * sizeof(float)));
                    glEnableVertexAttribArray(1);

                    glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, 10 * sizeof(float), (void*)(5 * sizeof(float)));
                    glEnableVertexAttribArray(2);

                    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 10 * sizeof(float), (void*)(6 * sizeof(float)));
                    glEnableVertexAttribArray(3);

                    glVertexAttribPointer(4, 1, GL_FLOAT, GL_FALSE, 10 * sizeof(float), (void*)(9 * sizeof(float)));
                    glEnableVertexAttribArray(4);
                    
                    it->second.vertexCount = job.meshData.size() / 10;
                    it->second.state = ChunkState::GPUResident;
                }
            }

            if (!vaosToDelete.empty()) {
                glDeleteVertexArrays(vaosToDelete.size(), vaosToDelete.data());
            }
            if (!vbosToDelete.empty()) {
                glDeleteBuffers(vbosToDelete.size(), vbosToDelete.data());
            }

            glm::mat4 vp = projection * view;
            struct Plane { glm::vec3 normal; float distance; };
            Plane planes[6];
            planes[0] = {glm::vec3(vp[0][3]+vp[0][0], vp[1][3]+vp[1][0], vp[2][3]+vp[2][0]), vp[3][3]+vp[3][0]}; // Left
            planes[1] = {glm::vec3(vp[0][3]-vp[0][0], vp[1][3]-vp[1][0], vp[2][3]-vp[2][0]), vp[3][3]-vp[3][0]}; // Right
            planes[2] = {glm::vec3(vp[0][3]+vp[0][1], vp[1][3]+vp[1][1], vp[2][3]+vp[2][1]), vp[3][3]+vp[3][1]}; // Bottom
            planes[3] = {glm::vec3(vp[0][3]-vp[0][1], vp[1][3]-vp[1][1], vp[2][3]-vp[2][1]), vp[3][3]-vp[3][1]}; // Top
            planes[4] = {glm::vec3(vp[0][3]+vp[0][2], vp[1][3]+vp[1][2], vp[2][3]+vp[2][2]), vp[3][3]+vp[3][2]}; // Near
            planes[5] = {glm::vec3(vp[0][3]-vp[0][2], vp[1][3]-vp[1][2], vp[2][3]-vp[2][2]), vp[3][3]-vp[3][2]}; // Far
            for(int i=0; i<6; i++) {
                float length = glm::length(planes[i].normal);
                planes[i].normal /= length;
                planes[i].distance /= length;
            }

            struct RenderChunk { GLuint VAO; int vertexCount; glm::vec3 pos; };
            std::vector<RenderChunk> renderChunks;
            {
                std::lock_guard<std::mutex> lock(worldMutex);
                for (const auto& pair : chunks) {
                    if (pair.second.state == ChunkState::GPUResident && pair.second.vertexCount > 0) {
                        float dx = (pair.first.x * CHUNK_SIZE + 8) - playerX;
                        float dz = (pair.first.z * CHUNK_SIZE + 8) - playerZ;
                        if (dx*dx + dz*dz <= RenderRadius*RenderRadius*CHUNK_SIZE*CHUNK_SIZE) {
                            glm::vec3 min(pair.first.x * CHUNK_SIZE - 0.5f, -0.5f, pair.first.z * CHUNK_SIZE - 0.5f);
                            glm::vec3 max(pair.first.x * CHUNK_SIZE + CHUNK_SIZE - 0.5f, CHUNK_HEIGHT - 0.5f, pair.first.z * CHUNK_SIZE + CHUNK_SIZE - 0.5f);
                            
                            bool inside = true;
                            for(int i=0; i<6; i++) {
                                glm::vec3 positive(
                                    planes[i].normal.x > 0 ? max.x : min.x,
                                    planes[i].normal.y > 0 ? max.y : min.y,
                                    planes[i].normal.z > 0 ? max.z : min.z
                                );
                                if (glm::dot(planes[i].normal, positive) + planes[i].distance < 0) {
                                    inside = false;
                                    break;
                                }
                            }
                            if (inside) {
                                renderChunks.push_back({pair.second.VAO, pair.second.vertexCount, glm::vec3(pair.first.x * CHUNK_SIZE, 0, pair.first.z * CHUNK_SIZE)});
                            }
                        }
                    }
                }
            }
            
            for (const auto& rc : renderChunks) {
                glm::mat4 model = glm::mat4(1.0f);
                model = glm::translate(model, rc.pos);
                glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
                glBindVertexArray(rc.VAO);
                glDrawArrays(GL_TRIANGLES, 0, rc.vertexCount);
            }

            eglSwapBuffers(display, surface);
        } else {
            usleep(16000);
        }
    }
    
    if (surface != EGL_NO_SURFACE) {
        eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
        eglDestroySurface(display, surface);
    }
    eglDestroyContext(display, context);
    eglTerminate(display);
}

