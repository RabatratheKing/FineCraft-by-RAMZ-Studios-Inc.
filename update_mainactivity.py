import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

jni_methods = """    @JvmStatic external fun nativeInit(assetManager: AssetManager, dataDir: String, cacheDir: String)
    @JvmStatic external fun nativeGetHealth(): Float
    @JvmStatic external fun nativeGetMaxHealth(): Float
    @JvmStatic external fun nativeIsDead(): Boolean
    @JvmStatic external fun nativeGetHurtTime(): Float
    @JvmStatic external fun nativeRespawn()
"""
text = re.sub(r'@JvmStatic external fun nativeInit.*?\)', jni_methods, text, flags=re.DOTALL)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)

