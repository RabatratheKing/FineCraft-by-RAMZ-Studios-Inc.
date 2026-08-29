import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

pattern = r"if \(strcmp\(actionStr, \"jump_down\"\) == 0\) \{"
replacement = """if (isInventoryOpen) {
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
    
    if (strcmp(actionStr, "jump_down") == 0) {"""
text = re.sub(pattern, replacement, text)

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
