import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

pattern_hud = r"// Hotbar[\s\S]*?\}\n\s*\}\n\s*\}"
replacement_hud = """// Hotbar
        var inventoryState by remember { mutableStateOf(MainActivity.nativeGetInventory()) }
        var selectedSlot by remember { mutableIntStateOf(MainActivity.nativeGetSelectedHotbarSlot()) }
        
        // Polling inventory state
        LaunchedEffect(Unit) {
            while(true) {
                kotlinx.coroutines.delay(100)
                inventoryState = MainActivity.nativeGetInventory()
                selectedSlot = MainActivity.nativeGetSelectedHotbarSlot()
            }
        }

        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            for (i in 0 until 9) {
                val invIndex = 27 + i
                val itemId = inventoryState[invIndex * 2]
                val count = inventoryState[invIndex * 2 + 1]
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(Color.Black.copy(alpha = 0.4f), RoundedCornerShape(4.dp))
                        .border(2.dp, if (i == selectedSlot) Color.White else Color.Transparent, RoundedCornerShape(4.dp))
                        .pointerInput(Unit) {
                            detectTapGestures(
                                onPress = {
                                    MainActivity.nativeAction("select_slot_$i")
                                }
                            )
                        }
                ) {
                    if (itemId > 0) {
                        // Very simple display: Text showing item ID (e.g. Grass) and count
                        // Real textures would require loading the atlas into Compose, but we can do a simple colored block or text for now.
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
            }
        }
    }
}
"""

text = re.sub(pattern_hud, replacement_hud, text)

# Add an inventory button
pattern_top_bar = r"Icon\(Icons\.Filled\.Settings, contentDescription = \"Debug\", tint = if \(debugMode\) Color\.Green else Color\.White\)\n\s*\}"
replacement_top_bar = """Icon(Icons.Filled.Settings, contentDescription = "Debug", tint = if (debugMode) Color.Green else Color.White)
            }
            
            Spacer(modifier = Modifier.weight(1f))

            IconButton(
                onClick = { MainActivity.nativeSetInventoryOpen(true) },
                modifier = Modifier
                    .size(48.dp)
                    .background(Color.Black.copy(alpha = 0.3f), CircleShape)
            ) {
                Icon(Icons.Filled.Menu, contentDescription = "Inventory", tint = Color.White)
            }"""

text = re.sub(pattern_top_bar, replacement_top_bar, text)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
