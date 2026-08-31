import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

hearts_pattern = r'for \(i in 0 until maxHearts\) \{.*?\n\s*\}\n\s*\}\n\s*\}'

hearts_replacement = """val isExt = MainActivity.nativeIsUsingExternalAtlas()
            
            for (i in 0 until maxHearts) {
                Box(modifier = Modifier.size(24.dp)) {
                    if (isExt && atlasBitmap != null) {
                        // Empty Heart (tile 242)
                        Image(
                            painter = BitmapPainter(atlasBitmap, IntOffset(242 % 16 * 16, 242 / 16 * 16), IntSize(16, 16), FilterQuality.None),
                            contentDescription = null, modifier = Modifier.fillMaxSize()
                        )
                        if (i < fullHearts) {
                            // Full Heart (tile 240)
                            Image(
                                painter = BitmapPainter(atlasBitmap, IntOffset(240 % 16 * 16, 240 / 16 * 16), IntSize(16, 16), FilterQuality.None),
                                contentDescription = null, modifier = Modifier.fillMaxSize()
                            )
                        } else if (i == fullHearts && halfHeart) {
                            // Half Heart (tile 241)
                            Image(
                                painter = BitmapPainter(atlasBitmap, IntOffset(241 % 16 * 16, 241 / 16 * 16), IntSize(16, 16), FilterQuality.None),
                                contentDescription = null, modifier = Modifier.fillMaxSize()
                            )
                        }
                    } else {
                        // Fallback icons
                        Icon(androidx.compose.material.icons.Icons.Filled.FavoriteBorder, contentDescription = null, tint = androidx.compose.ui.graphics.Color.Black.copy(alpha = 0.5f), modifier = Modifier.fillMaxSize())
                        if (i < fullHearts) {
                            Icon(androidx.compose.material.icons.Icons.Filled.Favorite, contentDescription = null, tint = androidx.compose.ui.graphics.Color.Red, modifier = Modifier.fillMaxSize())
                        } else if (i == fullHearts && halfHeart) {
                            Box(modifier = Modifier.fillMaxHeight().fillMaxWidth(0.5f).clipToBounds()) {
                                Icon(androidx.compose.material.icons.Icons.Filled.Favorite, contentDescription = null, tint = androidx.compose.ui.graphics.Color.Red, modifier = Modifier.size(24.dp))
                            }
                        }
                    }
                }
            }"""

text = re.sub(hearts_pattern, hearts_replacement, text, flags=re.DOTALL)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
