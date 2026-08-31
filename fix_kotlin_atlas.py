import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

# Add nativeSetAtlasPixels declaration
methods = """
    @JvmStatic external fun nativeSetAtlasPixels(pixels: IntArray)
    @JvmStatic external fun nativeGetAtlasPixels(): IntArray?
"""
text = text.replace("@JvmStatic external fun nativeGetAtlasPixels(): IntArray?", methods)

# In onCreate, try to load atlas.png
on_create_pattern = r'override fun onCreate.*?super\.onCreate\(savedInstanceState\)'
on_create_replacement = """override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        try {
            val inputStream = assets.open("atlas.png")
            val bmp = android.graphics.BitmapFactory.decodeStream(inputStream)
            if (bmp != null) {
                // Ensure it's 256x256
                val scaledBmp = android.graphics.Bitmap.createScaledBitmap(bmp, 256, 256, false)
                val pixels = IntArray(256 * 256)
                scaledBmp.getPixels(pixels, 0, 256, 0, 0, 256, 256)
                nativeSetAtlasPixels(pixels)
            }
        } catch (e: Exception) {
            e.printStackTrace()
            // Fallback to C++ procedural generation
        }
"""
text = re.sub(on_create_pattern, on_create_replacement, text, flags=re.DOTALL)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
