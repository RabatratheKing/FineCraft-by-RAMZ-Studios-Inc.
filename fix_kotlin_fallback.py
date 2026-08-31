import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

text += """
extern "C" JNIEXPORT jboolean JNICALL
Java_com_example_MainActivity_nativeIsUsingExternalAtlas(JNIEnv* env, jclass clazz) {
    return useExternalAtlas;
}
"""

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text2 = f.read()

text2 = text2.replace("@JvmStatic external fun nativeSetAtlasPixels(pixels: IntArray)", "@JvmStatic external fun nativeSetAtlasPixels(pixels: IntArray)\n    @JvmStatic external fun nativeIsUsingExternalAtlas(): Boolean")

pattern = r'val texIndex = when\(itemId\) \{.*?\n\s*\}'
replacement = """val isExt = MainActivity.nativeIsUsingExternalAtlas()
                val texIndex = if (isExt) {
                    when(itemId) {
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
                    }
                } else {
                    when(itemId) {
                        1 -> 1
                        2 -> 2
                        3 -> 3
                        4 -> 4
                        5 -> 6
                        7 -> 4
                        8 -> 8
                        9 -> 9
                        else -> 0
                    }
                }"""

text2 = re.sub(pattern, replacement, text2, flags=re.DOTALL)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text2)
