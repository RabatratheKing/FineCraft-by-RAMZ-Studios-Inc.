import re

with open("app/src/main/cpp/world/SaveManager.cpp", "r") as f:
    text = f.read()

text = text.replace("// Inventory\n", "clearCraftingGrid();\n        // Inventory\n")

with open("app/src/main/cpp/world/SaveManager.cpp", "w") as f:
    f.write(text)
