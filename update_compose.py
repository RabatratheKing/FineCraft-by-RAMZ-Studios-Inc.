import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

# Add imports
imports = """
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.graphics.FilterQuality
import androidx.compose.ui.layout.ContentScale
import androidx.compose.foundation.Image
import androidx.compose.material3.Slider
import androidx.compose.material3.AlertDialog
"""
text = text.replace("import androidx.compose.ui.unit.sp", "import androidx.compose.ui.unit.sp" + imports)

# Add external functions
text = text.replace("external fun nativeSurfaceDestroyed()", "external fun nativeSurfaceDestroyed()\n    external fun nativeGetAtlasPixels(): IntArray?\n    external fun nativeMoveItems(srcType: Int, srcSlot: Int, destType: Int, destSlot: Int, amount: Int): Boolean")

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
