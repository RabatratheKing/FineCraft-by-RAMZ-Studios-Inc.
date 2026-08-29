import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

pattern = r"@JvmStatic external fun nativeAction\(action: String\)"
replacement = """@JvmStatic external fun nativeAction(action: String)
    @JvmStatic external fun nativeGetInventory(): IntArray
    @JvmStatic external fun nativeSwapSlots(slotA: Int, slotB: Int)
    @JvmStatic external fun nativeGetSelectedHotbarSlot(): Int
    @JvmStatic external fun nativeSetInventoryOpen(open: Boolean)"""

text = re.sub(pattern, replacement, text)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
