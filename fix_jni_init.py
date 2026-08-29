import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

pattern = r"if \(\!isRunning\) \{"
replacement = """if (!isRunning) {
        initInventory();"""

text = re.sub(pattern, replacement, text)

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
