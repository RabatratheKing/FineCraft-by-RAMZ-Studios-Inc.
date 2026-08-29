import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

pattern = r"var debugMode by remember \{ mutableStateOf\(false\) \}"
replacement = """var debugMode by remember { mutableStateOf(false) }
    var showInventory by remember { mutableStateOf(false) }"""
text = re.sub(pattern, replacement, text)

pattern2 = r"onToggleDebug = \{ debugMode = \!debugMode; MainActivity.nativeAction\(\"debug_fly\"\) \}"
replacement2 = """onToggleDebug = { debugMode = !debugMode; MainActivity.nativeAction("debug_fly") },
            onToggleInventory = { showInventory = !showInventory }"""
text = re.sub(pattern2, replacement2, text)

pattern_hud_decl = r"fun HUD\(settings: SettingsManager, onPause: \(\) -> Unit, debugMode: Boolean, onToggleDebug: \(\) -> Unit\)"
replacement_hud_decl = """fun HUD(settings: SettingsManager, onPause: () -> Unit, debugMode: Boolean, onToggleDebug: () -> Unit, onToggleInventory: () -> Unit)"""
text = re.sub(pattern_hud_decl, replacement_hud_decl, text)

pattern_hud_btn = r"onClick = \{ MainActivity\.nativeSetInventoryOpen\(true\) \}"
replacement_hud_btn = """onClick = onToggleInventory"""
text = re.sub(pattern_hud_btn, replacement_hud_btn, text)

pattern_gameplay_end = r"        HUD\([\s\S]*?\n        \)\n    \}\n\}"
replacement_gameplay_end = """        if (!showInventory) {
            HUD(
                settings = settings,
                onPause = onBack,
                debugMode = debugMode,
                onToggleDebug = { debugMode = !debugMode; MainActivity.nativeAction("debug_fly") },
                onToggleInventory = { showInventory = true; MainActivity.nativeSetInventoryOpen(true) }
            )
        } else {
            InventoryScreen(
                onClose = { showInventory = false; MainActivity.nativeSetInventoryOpen(false) }
            )
        }
    }
}

@Composable
fun InventoryScreen(onClose: () -> Unit) {
    var inventoryState by remember { mutableStateOf(MainActivity.nativeGetInventory()) }
    var selectedSlotIndex by remember { mutableStateOf<Int?>(null) }

    LaunchedEffect(Unit) {
        while(true) {
            kotlinx.coroutines.delay(100)
            inventoryState = MainActivity.nativeGetInventory()
        }
    }

    Box(modifier = Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.7f)).pointerInput(Unit) {}) {
        Column(
            modifier = Modifier.align(Alignment.Center).background(Color(0xFF222222), RoundedCornerShape(8.dp)).padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("INVENTORY", color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 16.dp))

            // Main Inventory (27 slots: 3 rows of 9)
            for (row in 0 until 3) {
                Row(horizontalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier.padding(bottom = 4.dp)) {
                    for (col in 0 until 9) {
                        val slotIndex = row * 9 + col
                        InventorySlotUI(slotIndex, inventoryState, selectedSlotIndex) {
                            if (selectedSlotIndex == null) {
                                selectedSlotIndex = slotIndex
                            } else {
                                MainActivity.nativeSwapSlots(selectedSlotIndex!!, slotIndex)
                                selectedSlotIndex = null
                                inventoryState = MainActivity.nativeGetInventory()
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Hotbar (9 slots)
            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                for (col in 0 until 9) {
                    val slotIndex = 27 + col
                    InventorySlotUI(slotIndex, inventoryState, selectedSlotIndex) {
                        if (selectedSlotIndex == null) {
                            selectedSlotIndex = slotIndex
                        } else {
                            MainActivity.nativeSwapSlots(selectedSlotIndex!!, slotIndex)
                            selectedSlotIndex = null
                            inventoryState = MainActivity.nativeGetInventory()
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(onClick = onClose, colors = ButtonDefaults.buttonColors(containerColor = Color.DarkGray)) {
                Text("CLOSE", color = Color.White)
            }
        }
    }
}

@Composable
fun InventorySlotUI(slotIndex: Int, inventoryState: IntArray, selectedSlotIndex: Int?, onClick: () -> Unit) {
    val itemId = inventoryState[slotIndex * 2]
    val count = inventoryState[slotIndex * 2 + 1]
    val isSelected = selectedSlotIndex == slotIndex

    Box(
        modifier = Modifier
            .size(40.dp)
            .background(if (isSelected) Color.White.copy(alpha = 0.3f) else Color.Black.copy(alpha = 0.5f), RoundedCornerShape(4.dp))
            .border(2.dp, if (isSelected) Color.Yellow else Color.Gray, RoundedCornerShape(4.dp))
            .pointerInput(Unit) {
                detectTapGestures(onPress = { onClick() })
            }
    ) {
        if (itemId > 0) {
            val color = when(itemId) {
                1 -> Color(0xFF2D912D) // Grass
                2 -> Color(0xFF785032) // Dirt
                3 -> Color(0xFF828282) // Stone
                4 -> Color(0xFF6E4628) // Wood
                5 -> Color(0xFF1E641E) // Leaves
                7 -> Color(0xFFA07850) // Planks
                8 -> Color(0xFFE6D296) // Sand
                else -> Color.Gray
            }
            Box(modifier = Modifier.fillMaxSize().padding(4.dp).background(color))
            Text(text = "$count", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.BottomEnd).padding(2.dp))
        }
    }
}"""
text = re.sub(pattern_gameplay_end, replacement_gameplay_end, text)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
