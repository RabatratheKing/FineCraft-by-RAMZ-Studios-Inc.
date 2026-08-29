import re

with open("app/src/main/cpp/world/World.cpp", "r") as f:
    text = f.read()

text = text.replace("int seed = (cx * 73856093) ^ (cz * 19349663);", "int seed = worldSeed ^ (cx * 73856093) ^ (cz * 19349663);")

with open("app/src/main/cpp/world/World.cpp", "w") as f:
    f.write(text)
