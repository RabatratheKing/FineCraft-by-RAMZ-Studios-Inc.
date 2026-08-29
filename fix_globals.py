import re

with open("app/src/main/cpp/core/Globals.h", "r") as f:
    text = f.read()

# Remove struct InventorySlot and related externs
pattern = r"struct InventorySlot \{[\s\S]*?extern int selectedHotbarSlot;"
text = re.sub(pattern, "", text)

with open("app/src/main/cpp/core/Globals.h", "w") as f:
    f.write(text)

with open("app/src/main/cpp/core/Globals.cpp", "r") as f:
    text = f.read()

# Remove hotbar definition and selectedHotbarSlot
pattern2 = r"InventorySlot hotbar\[5\] = \{[\s\S]*?\};\nint selectedHotbarSlot = 0;"
text = re.sub(pattern2, "", text)

with open("app/src/main/cpp/core/Globals.cpp", "w") as f:
    f.write(text)
