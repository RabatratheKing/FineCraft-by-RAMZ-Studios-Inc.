import re
with open("app/src/main/cpp/CMakeLists.txt", "r") as f:
    text = f.read()

text = text.replace("gameplay/Raycast.cpp", "gameplay/Raycast.cpp gameplay/Inventory.cpp")

with open("app/src/main/cpp/CMakeLists.txt", "w") as f:
    f.write(text)
