import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

# Fix conflicting IntOffset import
text = text.replace("import androidx.compose.ui.unit.IntOffset\n", "", 1) # Just in case

text = text.replace("fun InventorySlotUI(", "@Composable\nfun InventorySlotUI(")
text = text.replace("fun ActionButton(", "@Composable\nfun ActionButton(")

# If we added too many @Composable, let's fix it
text = re.sub(r'(@Composable\s*){2,}fun InventorySlotUI', '@Composable\nfun InventorySlotUI', text)
text = re.sub(r'(@Composable\s*){2,}fun ActionButton', '@Composable\nfun ActionButton', text)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
