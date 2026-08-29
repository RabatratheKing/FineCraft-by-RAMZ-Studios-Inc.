import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

# Add native function declarations
if "nativeGetCraftingGrid" not in text:
    native_decls = """    @JvmStatic external fun nativeSwapCraftingSlot(invSlot: Int, craftSlot: Int)
    @JvmStatic external fun nativeSwapCraftingToCrafting(craftSlotA: Int, craftSlotB: Int)
    @JvmStatic external fun nativeTakeCraftingOutput()
    @JvmStatic external fun nativeGetCraftingGrid(): IntArray
    @JvmStatic external fun nativeGetCraftingOutput(): IntArray"""
    text = text.replace("  @JvmStatic external fun nativeSaveGame()", "  @JvmStatic external fun nativeSaveGame()\n" + native_decls)

inventory_screen_old = """@Composable
fun InventoryScreen(onClose: () -> Unit) {
    var inventoryState by remember { mutableStateOf(MainActivity.nativeGetInventory()) }
    var selectedSlotIndex by remember { mutableStateOf<Int?>(null) }"""

inventory_screen_new = """@Composable
fun InventoryScreen(onClose: () -> Unit) {
    var inventoryState by remember { mutableStateOf(MainActivity.nativeGetInventory()) }
    var craftingGridState by remember { mutableStateOf(MainActivity.nativeGetCraftingGrid()) }
    var craftingOutputState by remember { mutableStateOf(MainActivity.nativeGetCraftingOutput()) }
    var selectedSlotIndex by remember { mutableStateOf<Int?>(null) }
    var selectedCraftingSlot by remember { mutableStateOf<Int?>(null) }"""

text = text.replace(inventory_screen_old, inventory_screen_new)

launched_effect_old = """    LaunchedEffect(Unit) {
        while(true) {
            kotlinx.coroutines.delay(100)
            inventoryState = MainActivity.nativeGetInventory()
        }
    }"""

launched_effect_new = """    LaunchedEffect(Unit) {
        while(true) {
            kotlinx.coroutines.delay(100)
            inventoryState = MainActivity.nativeGetInventory()
            craftingGridState = MainActivity.nativeGetCraftingGrid()
            craftingOutputState = MainActivity.nativeGetCraftingOutput()
        }
    }"""
text = text.replace(launched_effect_old, launched_effect_new)

slot_click_old = """                        InventorySlotUI(slotIndex, inventoryState, selectedSlotIndex) {
                            if (selectedSlotIndex == null) {
                                selectedSlotIndex = slotIndex
                            } else {
                                MainActivity.nativeSwapSlots(selectedSlotIndex!!, slotIndex)
                                selectedSlotIndex = null
                                inventoryState = MainActivity.nativeGetInventory()
                            }
                        }"""

slot_click_new = """                        InventorySlotUI(slotIndex, inventoryState, selectedSlotIndex) {
                            if (selectedSlotIndex == null && selectedCraftingSlot == null) {
                                selectedSlotIndex = slotIndex
                            } else if (selectedSlotIndex != null) {
                                MainActivity.nativeSwapSlots(selectedSlotIndex!!, slotIndex)
                                selectedSlotIndex = null
                                inventoryState = MainActivity.nativeGetInventory()
                            } else if (selectedCraftingSlot != null) {
                                MainActivity.nativeSwapCraftingSlot(slotIndex, selectedCraftingSlot!!)
                                selectedCraftingSlot = null
                                inventoryState = MainActivity.nativeGetInventory()
                                craftingGridState = MainActivity.nativeGetCraftingGrid()
                                craftingOutputState = MainActivity.nativeGetCraftingOutput()
                            }
                        }"""

text = text.replace(slot_click_old, slot_click_new)

# Add Crafting UI section before main inventory
crafting_ui = """
            // CRAFTING SECTION
            Row(modifier = Modifier.padding(bottom = 16.dp), verticalAlignment = Alignment.CenterVertically) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    for (row in 0 until 2) {
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            for (col in 0 until 2) {
                                val craftSlot = row * 2 + col
                                InventorySlotUI(craftSlot, craftingGridState, if(selectedCraftingSlot == craftSlot) craftSlot else null) {
                                    if (selectedSlotIndex == null && selectedCraftingSlot == null) {
                                        selectedCraftingSlot = craftSlot
                                    } else if (selectedCraftingSlot != null) {
                                        MainActivity.nativeSwapCraftingToCrafting(selectedCraftingSlot!!, craftSlot)
                                        selectedCraftingSlot = null
                                    } else if (selectedSlotIndex != null) {
                                        MainActivity.nativeSwapCraftingSlot(selectedSlotIndex!!, craftSlot)
                                        selectedSlotIndex = null
                                    }
                                    inventoryState = MainActivity.nativeGetInventory()
                                    craftingGridState = MainActivity.nativeGetCraftingGrid()
                                    craftingOutputState = MainActivity.nativeGetCraftingOutput()
                                }
                            }
                        }
                    }
                }
                
                Icon(Icons.AutoMirrored.Filled.ArrowForward, contentDescription = "Craft", tint = Color.White, modifier = Modifier.padding(horizontal = 16.dp))
                
                // Output Slot
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .background(Color.Black.copy(alpha = 0.5f), RoundedCornerShape(4.dp))
                        .border(2.dp, Color.Gray, RoundedCornerShape(4.dp))
                        .pointerInput(Unit) {
                            detectTapGestures(onPress = {
                                MainActivity.nativeTakeCraftingOutput()
                                inventoryState = MainActivity.nativeGetInventory()
                                craftingGridState = MainActivity.nativeGetCraftingGrid()
                                craftingOutputState = MainActivity.nativeGetCraftingOutput()
                            })
                        }
                ) {
                    val outId = craftingOutputState[0]
                    val outCount = craftingOutputState[1]
                    if (outId > 0) {
                        val color = when(outId) {
                            1 -> Color(0xFF2D912D)
                            2 -> Color(0xFF785032)
                            3 -> Color(0xFF828282)
                            4 -> Color(0xFF6E4628)
                            5 -> Color(0xFF1E641E)
                            7 -> Color(0xFFA07850)
                            8 -> Color(0xFFE6D296)
                            9 -> Color(0xFF5C3A21)
                            else -> Color.Gray
                        }
                        Box(modifier = Modifier.fillMaxSize().padding(4.dp).background(color))
                        Text(text = "$outCount", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.BottomEnd).padding(2.dp))
                    }
                }
            }
"""
text = text.replace('Text("INVENTORY", color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 16.dp))', 'Text("CRAFTING", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 8.dp))\n' + crafting_ui + '\n            Text("INVENTORY", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 8.dp))')

# Support new color for sticks
if "9 -> Color(0xFF5C3A21) // Sticks" not in text:
    text = text.replace("8 -> Color(0xFFE6D296) // Sand", "8 -> Color(0xFFE6D296) // Sand\n                9 -> Color(0xFF5C3A21) // Sticks")

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
