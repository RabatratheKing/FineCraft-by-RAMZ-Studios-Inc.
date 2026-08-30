import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

text = text.replace("external fun nativeGetAtlasPixels()", "@JvmStatic external fun nativeGetAtlasPixels()")
text = text.replace("external fun nativeMoveItems(", "@JvmStatic external fun nativeMoveItems(")

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
