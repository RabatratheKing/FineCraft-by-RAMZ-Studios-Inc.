import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

# Fix imports
imports = """
import android.content.res.AssetManager
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
"""
text = text.replace("import androidx.compose.ui.draw.clip\n", imports + "import androidx.compose.ui.draw.clip\n")

# Fix nativeInitSave missing
methods = """
    @JvmStatic external fun nativeInitSave(dataDir: String)
    @JvmStatic external fun nativeInit(assetManager: AssetManager, dataDir: String, cacheDir: String)
"""
text = text.replace("@JvmStatic external fun nativeInit(assetManager: AssetManager, dataDir: String, cacheDir: String)", methods)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
