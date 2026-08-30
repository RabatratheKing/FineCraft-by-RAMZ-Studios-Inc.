import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

# Replace InventoryScreen
inv_screen_start = "fun InventoryScreen(onClose: () -> Unit"
hud_start = "fun HUD("

match = re.search(r'fun InventoryScreen\(onClose.*?fun InventorySlotUI', text, re.DOTALL)
if match:
    old_inv = match.group(0)[:-len("fun InventorySlotUI")]
    new_inv = """fun InventoryScreen(onClose: () -> Unit, atlasBitmap: ImageBitmap?) {
    var inventoryState by remember { mutableStateOf<IntArray>(MainActivity.nativeGetInventory()) }
    var craftingGridState by remember { mutableStateOf<IntArray>(MainActivity.nativeGetCraftingGrid()) }
    var craftingOutputState by remember { mutableStateOf<IntArray>(MainActivity.nativeGetCraftingOutput()) }
    var selectedSlotIndex by remember { mutableStateOf<Int?>(null) }
    var selectedCraftingSlot by remember { mutableStateOf<Int?>(null) }
    
    var splitSourceSlot by remember { mutableStateOf<Int?>(null) }
    var splitSourceType by remember { mutableStateOf<Int>(0) } // 0=inv, 1=craft
    var showSplitDialog by remember { mutableStateOf(false) }
    var splitAmount by remember { mutableIntStateOf(1) }
    var splitDestSlot by remember { mutableStateOf<Int?>(null) }
    var splitDestType by remember { mutableStateOf<Int>(0) }

    LaunchedEffect(Unit) {
        while(true) {
            kotlinx.coroutines.delay(100)
            inventoryState = MainActivity.nativeGetInventory()
            craftingGridState = MainActivity.nativeGetCraftingGrid()
            craftingOutputState = MainActivity.nativeGetCraftingOutput()
        }
    }
    
    if (showSplitDialog && splitSourceSlot != null && splitDestSlot != null) {
        val srcCount = if (splitSourceType == 0) inventoryState[splitSourceSlot!! * 2 + 1] else craftingGridState[splitSourceSlot!! * 2 + 1]
        
        AlertDialog(
            onDismissRequest = { showSplitDialog = false },
            title = { Text("Split Stack", color = Color.White) },
            text = {
                Column {
                    Text("Select amount to move:", color = Color.White)
                    if (srcCount > 1) {
                        Slider(
                            value = splitAmount.toFloat(),
                            onValueChange = { splitAmount = it.toInt() },
                            valueRange = 1f..srcCount.toFloat(),
                            steps = srcCount - 2
                        )
                    }
                    Text("$splitAmount / $srcCount", color = Color.White)
                }
            },
            confirmButton = {
                Button(onClick = {
                    showSplitDialog = false
                    MainActivity.nativeMoveItems(splitSourceType, splitSourceSlot!!, splitDestType, splitDestSlot!!, splitAmount)
                    inventoryState = MainActivity.nativeGetInventory()
                    craftingGridState = MainActivity.nativeGetCraftingGrid()
                    craftingOutputState = MainActivity.nativeGetCraftingOutput()
                    selectedSlotIndex = null
                    selectedCraftingSlot = null
                }) { Text("Move") }
            },
            dismissButton = {
                Button(onClick = { showSplitDialog = false }) { Text("Cancel") }
            },
            containerColor = Color.DarkGray
        )
    }

    Box(modifier = Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.7f)).pointerInput(Unit) {}) {
        Column(
            modifier = Modifier.align(Alignment.Center).background(Color(0xFF222222), RoundedCornerShape(8.dp)).padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("CRAFTING", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 8.dp))
            
            // CRAFTING SECTION
            Row(modifier = Modifier.padding(bottom = 16.dp), verticalAlignment = Alignment.CenterVertically) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    for (row in 0 until 2) {
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            for (col in 0 until 2) {
                                val craftSlot = row * 2 + col
                                val cId = craftingGridState[craftSlot * 2]
                                val cCount = craftingGridState[craftSlot * 2 + 1]
                                InventorySlotUI(
                                    slotIndex = craftSlot, 
                                    itemId = cId,
                                    count = cCount,
                                    isSelected = selectedCraftingSlot == craftSlot,
                                    atlasBitmap = atlasBitmap,
                                    onClick = {
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
                                    },
                                    onLongClick = {
                                        if (selectedSlotIndex != null) {
                                            splitSourceSlot = selectedSlotIndex
                                            splitSourceType = 0
                                            splitDestSlot = craftSlot
                                            splitDestType = 1
                                            splitAmount = 1
                                            showSplitDialog = true
                                        } else if (selectedCraftingSlot != null && selectedCraftingSlot != craftSlot) {
                                            splitSourceSlot = selectedCraftingSlot
                                            splitSourceType = 1
                                            splitDestSlot = craftSlot
                                            splitDestType = 1
                                            splitAmount = 1
                                            showSplitDialog = true
                                        }
                                    }
                                )
                            }
                        }
                    }
                }
                
                Icon(Icons.AutoMirrored.Filled.ArrowForward, contentDescription = "Craft", tint = Color.White, modifier = Modifier.padding(horizontal = 16.dp))
                
                // Output Slot
                val outId = craftingOutputState[0]
                val outCount = craftingOutputState[1]
                InventorySlotUI(
                    slotIndex = 0,
                    itemId = outId,
                    count = outCount,
                    isSelected = false,
                    atlasBitmap = atlasBitmap,
                    onClick = {
                        MainActivity.nativeTakeCraftingOutput()
                        inventoryState = MainActivity.nativeGetInventory()
                        craftingGridState = MainActivity.nativeGetCraftingGrid()
                        craftingOutputState = MainActivity.nativeGetCraftingOutput()
                    },
                    onLongClick = {}
                )
            }
            Text("INVENTORY", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 8.dp))
            
            // Main Inventory (27 slots: 3 rows of 9)
            for (row in 0 until 3) {
                Row(horizontalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier.padding(bottom = 4.dp)) {
                    for (col in 0 until 9) {
                        val slotIndex = row * 9 + col
                        val iId = inventoryState[slotIndex * 2]
                        val iCount = inventoryState[slotIndex * 2 + 1]
                        InventorySlotUI(
                            slotIndex = slotIndex, 
                            itemId = iId,
                            count = iCount,
                            isSelected = selectedSlotIndex == slotIndex,
                            atlasBitmap = atlasBitmap,
                            onClick = {
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
                            },
                            onLongClick = {
                                if (selectedSlotIndex != null && selectedSlotIndex != slotIndex) {
                                    splitSourceSlot = selectedSlotIndex
                                    splitSourceType = 0
                                    splitDestSlot = slotIndex
                                    splitDestType = 0
                                    splitAmount = 1
                                    showSplitDialog = true
                                } else if (selectedCraftingSlot != null) {
                                    splitSourceSlot = selectedCraftingSlot
                                    splitSourceType = 1
                                    splitDestSlot = slotIndex
                                    splitDestType = 0
                                    splitAmount = 1
                                    showSplitDialog = true
                                }
                            }
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
            // Hotbar (9 slots)
            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                for (col in 0 until 9) {
                    val slotIndex = 27 + col
                    val iId = inventoryState[slotIndex * 2]
                    val iCount = inventoryState[slotIndex * 2 + 1]
                    InventorySlotUI(
                        slotIndex = slotIndex, 
                        itemId = iId,
                        count = iCount,
                        isSelected = selectedSlotIndex == slotIndex,
                        atlasBitmap = atlasBitmap,
                        onClick = {
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
                        },
                        onLongClick = {
                            if (selectedSlotIndex != null && selectedSlotIndex != slotIndex) {
                                splitSourceSlot = selectedSlotIndex
                                splitSourceType = 0
                                splitDestSlot = slotIndex
                                splitDestType = 0
                                splitAmount = 1
                                showSplitDialog = true
                            } else if (selectedCraftingSlot != null) {
                                splitSourceSlot = selectedCraftingSlot
                                splitSourceType = 1
                                splitDestSlot = slotIndex
                                splitDestType = 0
                                splitAmount = 1
                                showSplitDialog = true
                            }
                        }
                    )
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = onClose, colors = ButtonDefaults.buttonColors(containerColor = Color.DarkGray)) {
                Text("CLOSE", color = Color.White)
            }
        }
    }
}
"""
    text = text.replace(old_inv, new_inv)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
