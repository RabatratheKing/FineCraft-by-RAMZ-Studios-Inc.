import re

with open("app/src/main/cpp/rendering/Renderer.cpp", "r") as f:
    text = f.read()

pattern = r'atlasGenerated = true;\n\s*glGenTextures\(1, \&texID\);'

replacement = """uint8_t* glPixels = new uint8_t[size * size * 4];
    for (int i = 0; i < size * size; ++i) {
        uint32_t c = atlasPixelsARGB[i];
        glPixels[i*4 + 0] = (c >> 16) & 0xFF; // R
        glPixels[i*4 + 1] = (c >> 8) & 0xFF;  // G
        glPixels[i*4 + 2] = (c) & 0xFF;       // B
        glPixels[i*4 + 3] = (c >> 24) & 0xFF; // A
    }
    
    atlasGenerated = true;
    glGenTextures(1, &texID);"""

text = re.sub(pattern, replacement, text, flags=re.DOTALL)
text = text.replace("glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, atlasPixelsARGB);", 
                    "glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, glPixels);\n    delete[] glPixels;")

with open("app/src/main/cpp/rendering/Renderer.cpp", "w") as f:
    f.write(text)
