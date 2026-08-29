import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

pattern = r"(@JvmStatic external fun nativeUpdateSettings[^)]+\))"
replacement = r"""\1
    @JvmStatic external fun nativeInitSave(path: String)
    @JvmStatic external fun nativeHasSave(): Boolean
    @JvmStatic external fun nativeLoadGame()
    @JvmStatic external fun nativeNewGame()
    @JvmStatic external fun nativeSaveGame()"""
text = re.sub(pattern, replacement, text)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
