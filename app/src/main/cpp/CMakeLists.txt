cmake_minimum_required(VERSION 3.22.1)

project("finecraft")

include(FetchContent)
FetchContent_Declare(
    glm
    GIT_REPOSITORY https://github.com/g-truc/glm.git
    GIT_TAG 0.9.9.8
)
FetchContent_MakeAvailable(glm)

add_library(finecraft SHARED rendering/Renderer.cpp platform/android/JNI.cpp core/Globals.cpp world/World.cpp player/Physics.cpp gameplay/Raycast.cpp world/ChunkManager.cpp)

find_library(log-lib log)
find_library(android-lib android)
find_library(egl-lib EGL)
find_library(gles-lib GLESv3)

target_include_directories(finecraft PRIVATE ${glm_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR})

target_link_libraries(finecraft
        ${log-lib}
        ${android-lib}
        ${egl-lib}
        ${gles-lib}
)
