import re

with open("app/src/main/cpp/rendering/Renderer.cpp", "r") as f:
    text = f.read()

decls = """uint32_t atlasPixelsARGB[256 * 256];
bool atlasGenerated = false;
uint32_t externalAtlasPixels[256 * 256];
bool useExternalAtlas = false;
"""
text = text.replace("uint32_t atlasPixelsARGB[256 * 256];\nbool atlasGenerated = false;", decls)

gen_pattern = r'void generateTextureAtlas\(GLuint& texID\) \{.*?atlasGenerated = true;\n    glGenTextures\(1, &texID\);'

gen_replacement = """void generateTextureAtlas(GLuint& texID) {
    int size = 256;
    
    if (useExternalAtlas) {
        for(int i = 0; i < size * size; ++i) {
            atlasPixelsARGB[i] = externalAtlasPixels[i];
        }
    } else {
        // Fallback procedural atlas
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
                } else if (tileIndex == 9) { // Scaffolding (Climbable)
                    r = 180; g = 140; b = 80;
                    if ((x % 4 == 0) || (y % 4 == 0)) { r -= 40; g -= 40; b -= 40; } // grid pattern
                    noise = 0;
                } else {
                    r = 100; g = 100; b = 100; // default gray
                    if ((x+y)%2 == 0) { r-=10; g-=10; b-=10; }
                }
                
                r = std::min(255, std::max(0, r + noise));
                g = std::min(255, std::max(0, g + noise));
                b = std::min(255, std::max(0, b + noise));
                
                atlasPixelsARGB[y * size + x] = (255 << 24) | (r << 16) | (g << 8) | b;
            }
        }
    }
    
    atlasGenerated = true;
    glGenTextures(1, &texID);"""

text = re.sub(gen_pattern, gen_replacement, text, flags=re.DOTALL)

with open("app/src/main/cpp/rendering/Renderer.cpp", "w") as f:
    f.write(text)
