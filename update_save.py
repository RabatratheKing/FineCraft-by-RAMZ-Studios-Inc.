import re

with open("app/src/main/cpp/world/SaveManager.cpp", "r") as f:
    text = f.read()

# Update SaveGame
save_game_pattern = r'uint32_t version = 1;\n\s*out\.write\(\(char\*\)&version, sizeof\(version\)\);\n\n\s*// Globals\n\s*out\.write\(\(char\*\)&worldSeed, sizeof\(worldSeed\)\);\n\s*out\.write\(\(char\*\)&playerX, sizeof\(playerX\)\);\n\s*out\.write\(\(char\*\)&playerY, sizeof\(playerY\)\);\n\s*out\.write\(\(char\*\)&playerZ, sizeof\(playerZ\)\);\n\s*out\.write\(\(char\*\)&cameraLookX, sizeof\(cameraLookX\)\);\n\s*out\.write\(\(char\*\)&cameraLookY, sizeof\(cameraLookY\)\);\n\s*out\.write\(\(char\*\)&timeOfDay, sizeof\(timeOfDay\)\);'

save_game_replacement = """uint32_t version = 2;
        out.write((char*)&version, sizeof(version));

        // Globals
        out.write((char*)&worldSeed, sizeof(worldSeed));
        out.write((char*)&playerX, sizeof(playerX));
        out.write((char*)&playerY, sizeof(playerY));
        out.write((char*)&playerZ, sizeof(playerZ));
        out.write((char*)&cameraLookX, sizeof(cameraLookX));
        out.write((char*)&cameraLookY, sizeof(cameraLookY));
        out.write((char*)&timeOfDay, sizeof(timeOfDay));
        out.write((char*)&playerHealth, sizeof(playerHealth));
        out.write((char*)&isDead, sizeof(isDead));"""

text = re.sub(save_game_pattern, save_game_replacement, text)

# Update LoadGame
load_game_pattern = r'if \(version != 1\) \{\n\s*LOGE\("Unsupported save file version"\);\n\s*return;\n\s*\}\n\n\s*in\.read\(\(char\*\)&worldSeed, sizeof\(worldSeed\)\);\n\s*in\.read\(\(char\*\)&playerX, sizeof\(playerX\)\);\n\s*in\.read\(\(char\*\)&playerY, sizeof\(playerY\)\);\n\s*in\.read\(\(char\*\)&playerZ, sizeof\(playerZ\)\);\n\s*in\.read\(\(char\*\)&cameraLookX, sizeof\(cameraLookX\)\);\n\s*in\.read\(\(char\*\)&cameraLookY, sizeof\(cameraLookY\)\);\n\s*in\.read\(\(char\*\)&timeOfDay, sizeof\(timeOfDay\)\);'

load_game_replacement = """if (version != 1 && version != 2) {
            LOGE("Unsupported save file version");
            return;
        }

        in.read((char*)&worldSeed, sizeof(worldSeed));
        in.read((char*)&playerX, sizeof(playerX));
        in.read((char*)&playerY, sizeof(playerY));
        in.read((char*)&playerZ, sizeof(playerZ));
        in.read((char*)&cameraLookX, sizeof(cameraLookX));
        in.read((char*)&cameraLookY, sizeof(cameraLookY));
        in.read((char*)&timeOfDay, sizeof(timeOfDay));
        
        if (version >= 2) {
            in.read((char*)&playerHealth, sizeof(playerHealth));
            in.read((char*)&isDead, sizeof(isDead));
            if (isDead) {
                playerState = LocomotionState::DEAD;
            } else {
                playerState = LocomotionState::STANDING;
            }
        } else {
            playerHealth = playerMaxHealth;
            isDead = false;
        }"""

text = re.sub(load_game_pattern, load_game_replacement, text)

# Update NewGame
new_game_pattern = r'timeOfDay = 0\.0f;'
new_game_replacement = """timeOfDay = 0.0f;
        playerHealth = playerMaxHealth;
        isDead = false;
        playerState = LocomotionState::STANDING;
        highestY = playerY;"""

text = re.sub(new_game_pattern, new_game_replacement, text)

with open("app/src/main/cpp/world/SaveManager.cpp", "w") as f:
    f.write(text)
