import re

with open("app/src/main/cpp/world/World.cpp", "r") as f:
    text = f.read()

tex_pattern = r'auto getTexIndex = \[\&\]\(uint8_t blockType, int faceType\) -> float \{.*?\n\s*return \(float\)texIndex;\n\s*\};'

tex_replacement = """extern bool useExternalAtlas;

    auto getTexIndex = [&](uint8_t blockType, int faceType) -> float {
        int texIndex = 0;
        if (useExternalAtlas) {
            if (blockType == 1) { // Grass
                if (faceType == 2) texIndex = 0;
                else if (faceType == 3) texIndex = 3; // Dirt
                else texIndex = 1; 
            }
            else if (blockType == 2) { texIndex = 3; } // Dirt
            else if (blockType == 3) { texIndex = 4; } // Stone
            else if (blockType == 4) { texIndex = (faceType == 2 || faceType == 3) ? 16 : 15; } // Log
            else if (blockType == 5) { texIndex = 20; } // Leaves
            else if (blockType == 6) { texIndex = 56; } // Water
            else if (blockType == 7) { texIndex = 17; } // Planks
            else if (blockType == 8) { texIndex = 5; } // Sand
            else if (blockType == 9) { texIndex = 31; } // Scaffolding
            else { texIndex = 0; }
        } else {
            if (blockType == 1) { 
                if (faceType == 2) texIndex = 0;
                else if (faceType == 3) texIndex = 2;
                else texIndex = 1; 
            }
            else if (blockType == 2) { texIndex = 2; }
            else if (blockType == 3) { texIndex = 3; }
            else if (blockType == 4) { texIndex = (faceType == 2 || faceType == 3) ? 5 : 4; }
            else if (blockType == 5) { texIndex = 6; }
            else if (blockType == 6) { texIndex = 7; }
            else if (blockType == 7) { texIndex = 4; }
            else if (blockType == 8) { texIndex = 8; }
            else { texIndex = 9; }
        }
        return (float)texIndex;
    };"""

text = re.sub(tex_pattern, tex_replacement, text, flags=re.DOTALL)

with open("app/src/main/cpp/world/World.cpp", "w") as f:
    f.write(text)
