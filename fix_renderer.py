import re

with open("app/src/main/cpp/rendering/Renderer.cpp", "r") as f:
    text = f.read()

text = text.replace("void generateTextureAtlas(GLuint& texID) {", """
uint32_t atlasPixelsARGB[256 * 256];
bool atlasGenerated = false;

void generateTextureAtlas(GLuint& texID) {
""")

text = text.replace("uint8_t* pixels = new uint8_t[size * size * 4];", """uint8_t* pixels = new uint8_t[size * size * 4];""")

replacement = """            pixels[p] = r;
            pixels[p+1] = g;
            pixels[p+2] = b;
            pixels[p+3] = 255;
            
            atlasPixelsARGB[y * size + x] = (255 << 24) | (r << 16) | (g << 8) | b;"""
text = text.replace("""            pixels[p] = r;
            pixels[p+1] = g;
            pixels[p+2] = b;
            pixels[p+3] = 255;""", replacement)

text = text.replace("glGenTextures(1, &texID);", "atlasGenerated = true;\n    glGenTextures(1, &texID);")

with open("app/src/main/cpp/rendering/Renderer.cpp", "w") as f:
    f.write(text)
