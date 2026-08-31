import re

with open("app/src/main/cpp/rendering/Renderer.cpp", "r") as f:
    text = f.read()

# Replace glTexImage2D using 'pixels' with 'atlasPixelsARGB'
text = text.replace("glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels);", "glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, atlasPixelsARGB);")
text = text.replace("delete[] pixels;", "")

with open("app/src/main/cpp/rendering/Renderer.cpp", "w") as f:
    f.write(text)
