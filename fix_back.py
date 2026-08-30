import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

text = text.replace("import androidx.activity.compose.setContent", "import androidx.activity.compose.setContent\nimport androidx.activity.compose.BackHandler")

text = text.replace("fun SettingsMenu(settings: SettingsManager, onBack: () -> Unit) {", "fun SettingsMenu(settings: SettingsManager, onBack: () -> Unit) {\n    BackHandler { onBack() }")

text = text.replace("fun GameplayScreen(settings: SettingsManager, onBack: () -> Unit) {", "fun GameplayScreen(settings: SettingsManager, onBack: () -> Unit) {")

gameplay_screen_old = """@Composable
fun GameplayScreen(settings: SettingsManager, onBack: () -> Unit) {
    var debugMode by remember { mutableStateOf(false) }
    var showInventory by remember { mutableStateOf(false) }"""

gameplay_screen_new = """@Composable
fun GameplayScreen(settings: SettingsManager, onBack: () -> Unit) {
    var debugMode by remember { mutableStateOf(false) }
    var showInventory by remember { mutableStateOf(false) }
    
    BackHandler {
        if (showInventory) {
            showInventory = false
            MainActivity.nativeSetInventoryOpen(false)
        } else {
            onBack()
        }
    }"""

text = text.replace(gameplay_screen_old, gameplay_screen_new)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
