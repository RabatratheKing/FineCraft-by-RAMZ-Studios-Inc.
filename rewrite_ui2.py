import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

# Update GameplayScreen atlas loading
gp_screen_old = """@Composable
fun GameplayScreen(settings: SettingsManager, onBack: () -> Unit) {
    var debugMode by remember { mutableStateOf(false) }
    var showInventory by remember { mutableStateOf(false) }
    
    BackHandler {"""
gp_screen_new = """@Composable
fun GameplayScreen(settings: SettingsManager, onBack: () -> Unit) {
    var debugMode by remember { mutableStateOf(false) }
    var showInventory by remember { mutableStateOf(false) }
    var atlasBitmap by remember { mutableStateOf<ImageBitmap?>(null) }
    
    androidx.compose.runtime.LaunchedEffect(Unit) {
        while (atlasBitmap == null) {
            val pixels = MainActivity.nativeGetAtlasPixels()
            if (pixels != null) {
                val bmp = android.graphics.Bitmap.createBitmap(pixels, 256, 256, android.graphics.Bitmap.Config.ARGB_8888)
                atlasBitmap = bmp.asImageBitmap()
            } else {
                kotlinx.coroutines.delay(100)
            }
        }
    }
    
    BackHandler {"""
text = text.replace(gp_screen_old, gp_screen_new)

# Update HUD call
text = text.replace("HUD(\n                settings = settings,\n                onPause = onBack,\n                debugMode = debugMode,\n                onToggleDebug = { debugMode = !debugMode; MainActivity.nativeAction(\"debug_fly\") },\n                onToggleInventory = { showInventory = true; MainActivity.nativeSetInventoryOpen(true) }\n            )", "HUD(\n                settings = settings,\n                onPause = onBack,\n                debugMode = debugMode,\n                onToggleDebug = { debugMode = !debugMode; MainActivity.nativeAction(\"debug_fly\") },\n                onToggleInventory = { showInventory = true; MainActivity.nativeSetInventoryOpen(true) },\n                atlasBitmap = atlasBitmap\n            )")

# Update InventoryScreen call
text = text.replace("InventoryScreen(\n                onClose = { showInventory = false; MainActivity.nativeSetInventoryOpen(false) }\n            )", "InventoryScreen(\n                onClose = { showInventory = false; MainActivity.nativeSetInventoryOpen(false) },\n                atlasBitmap = atlasBitmap\n            )")

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
