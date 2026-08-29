import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

bindings = """    @JvmStatic external fun nativeSwapCraftingSlot(invSlot: Int, craftSlot: Int)
    @JvmStatic external fun nativeSwapCraftingToCrafting(craftSlotA: Int, craftSlotB: Int)
    @JvmStatic external fun nativeTakeCraftingOutput()
    @JvmStatic external fun nativeGetCraftingGrid(): IntArray
    @JvmStatic external fun nativeGetCraftingOutput(): IntArray"""

if "nativeGetCraftingGrid" not in text:
    text = text.replace("    @JvmStatic external fun nativeSaveGame()", "    @JvmStatic external fun nativeSaveGame()\n" + bindings)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
