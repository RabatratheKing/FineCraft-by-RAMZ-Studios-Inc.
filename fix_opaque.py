import re

with open("app/src/main/cpp/world/World.cpp", "r") as f:
    text = f.read()

pattern = r'auto isOpaque = \[\]\(uint8_t b\) -> bool \{.*?\n\s*\};'
replacement = """auto isOpaque = [](uint8_t b) -> bool {
        // Air (0), Leaves (5), Water (6), Scaffolding (9) are transparent
        return b != 0 && b != 5 && b != 6 && b != 9;
    };"""

text = re.sub(pattern, replacement, text, flags=re.DOTALL)

with open("app/src/main/cpp/world/World.cpp", "w") as f:
    f.write(text)
