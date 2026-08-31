import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

pattern = r'val texIndex = when\(itemId\) \{.*?\n\s*\}'
replacement = """val texIndex = when(itemId) {
                    1 -> 1 // Grass Side
                    2 -> 3 // Dirt
                    3 -> 4 // Stone
                    4 -> 15 // Log
                    5 -> 20 // Leaves
                    6 -> 56 // Water
                    7 -> 17 // Planks
                    8 -> 5 // Sand
                    9 -> 31 // Scaffolding
                    else -> 0
                }"""

text = re.sub(pattern, replacement, text, flags=re.DOTALL)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
