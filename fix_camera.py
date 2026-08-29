import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

pattern = r"MainActivity\.nativeCameraLook\(dragAmount\.x, dragAmount\.y\)"
replacement = """if (!showInventory) {
                            MainActivity.nativeCameraLook(dragAmount.x, dragAmount.y)
                        }"""
text = re.sub(pattern, replacement, text)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
