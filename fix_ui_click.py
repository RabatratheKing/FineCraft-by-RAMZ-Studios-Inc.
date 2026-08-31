import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

text = text.replace("clickable(enabled=false){}", "clickable(interactionSource = remember { MutableInteractionSource() }, indication = null) {}")

if "MutableInteractionSource" not in text:
    text = text.replace("import androidx.compose.ui.Modifier", "import androidx.compose.ui.Modifier\nimport androidx.compose.foundation.interaction.MutableInteractionSource")

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
