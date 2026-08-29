import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

# For camera
pattern_cam = r"cameraLookX \+= dx \* 0\.5f \* settingSensitivity;\n\s*cameraLookY -= dy \* 0\.5f \* settingSensitivity \* multY;"
replacement_cam = """if (!isInventoryOpen) {
        cameraLookX += dx * 0.5f * settingSensitivity;
        cameraLookY -= dy * 0.5f * settingSensitivity * multY;
    }"""
text = re.sub(pattern_cam, replacement_cam, text)

# For joystick
pattern_joy = r"inputMoveX = x;\n\s*inputMoveY = y;"
replacement_joy = """if (!isInventoryOpen) {
        inputMoveX = x;
        inputMoveY = y;
    } else {
        inputMoveX = 0.0f;
        inputMoveY = 0.0f;
    }"""
text = re.sub(pattern_joy, replacement_joy, text)

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
