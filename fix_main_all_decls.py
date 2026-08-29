import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

pattern = r"(@JvmStatic external fun nativeSaveGame\(\))"
replacement = r"""\1
    @JvmStatic external fun nativeSwapCraftingSlot(invSlot: Int, craftSlot: Int)
    @JvmStatic external fun nativeSwapCraftingToCrafting(craftSlotA: Int, craftSlotB: Int)
    @JvmStatic external fun nativeTakeCraftingOutput()
    @JvmStatic external fun nativeGetCraftingGrid(): IntArray
    @JvmStatic external fun nativeGetCraftingOutput(): IntArray"""
text = re.sub(pattern, replacement, text)

# also fix type inference errors: `val outId = craftingOutputState[0]` -> `val outId = craftingOutputState.get(0)`? No, `outId > 0` was failing because `> 0` on `Int` shouldn't fail, but maybe it thought it wasn't an int array?
# Let's fix the type inference errors: 
# Cannot infer type for this parameter. Specify it explicitly. 
# Not enough information to infer type argument for 'T'.
# This is usually `remember { mutableStateOf(...) }` without types.
text = text.replace("mutableStateOf(MainActivity.nativeGetInventory())", "mutableStateOf<IntArray>(MainActivity.nativeGetInventory())")
text = text.replace("mutableStateOf(MainActivity.nativeGetCraftingGrid())", "mutableStateOf<IntArray>(MainActivity.nativeGetCraftingGrid())")
text = text.replace("mutableStateOf(MainActivity.nativeGetCraftingOutput())", "mutableStateOf<IntArray>(MainActivity.nativeGetCraftingOutput())")

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
