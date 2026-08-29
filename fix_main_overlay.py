import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

pattern = r"AppState\.GAMEPLAY -> GameplayScreen\(settings, onBack = \{ currentAppState = AppState\.MAIN_MENU \}\)\n\s*\}"
replacement = """AppState.GAMEPLAY -> GameplayScreen(settings, onBack = { currentAppState = AppState.MAIN_MENU })
        }
        val isGenerating by musicManager.isGenerating.collectAsState()
        val hasError by musicManager.hasError.collectAsState()
        if (isGenerating) {
            Box(modifier = Modifier.fillMaxSize().padding(16.dp), contentAlignment = Alignment.BottomCenter) {
                Text("AI is generating background music (Lyria)...", color = Color.White, fontSize = 12.sp, modifier = Modifier.background(Color.Black.copy(alpha=0.6f), RoundedCornerShape(4.dp)).padding(8.dp))
            }
        }
        if (hasError != null) {
            Box(modifier = Modifier.fillMaxSize().padding(16.dp), contentAlignment = Alignment.BottomCenter) {
                Text(hasError!!, color = Color.Red, fontSize = 12.sp, modifier = Modifier.background(Color.Black.copy(alpha=0.8f), RoundedCornerShape(4.dp)).padding(8.dp))
            }
        }"""
text = re.sub(pattern, replacement, text)

# Add collectAsState import
if "import androidx.compose.runtime.collectAsState" not in text:
    text = text.replace("import androidx.compose.runtime.getValue", "import androidx.compose.runtime.getValue\nimport androidx.compose.runtime.collectAsState")

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
