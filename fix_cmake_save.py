import re

with open("app/src/main/cpp/CMakeLists.txt", "r") as f:
    text = f.read()

text = text.replace("world/World.cpp", "world/World.cpp world/SaveManager.cpp")

with open("app/src/main/cpp/CMakeLists.txt", "w") as f:
    f.write(text)
