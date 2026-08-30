import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

hud_start = "fun HUD(settings: SettingsManager, onPause: () -> Unit, debugMode: Boolean, onToggleDebug: () -> Unit, onToggleInventory: () -> Unit"

match = re.search(r'fun HUD\(settings.*?fun ActionButton', text, re.DOTALL)
if match:
    old_hud = match.group(0)[:-len("fun ActionButton")]
    new_hud = """fun HUD(settings: SettingsManager, onPause: () -> Unit, debugMode: Boolean, onToggleDebug: () -> Unit, onToggleInventory: () -> Unit, atlasBitmap: ImageBitmap?) {
    Box(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        // Top Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top
        ) {
            IconButton(
                onClick = onPause,
                modifier = Modifier
                    .size(48.dp)
                    .background(Color.Black.copy(alpha = 0.3f), CircleShape)
            ) {
                Icon(Icons.Filled.Close, contentDescription = "Pause", tint = Color.White)
            }
            
            if (debugMode) {
                Text("FPS: 60 | CHUNKS: 12", color = Color.White, fontSize = 12.sp, modifier = Modifier.background(Color.Black.copy(alpha=0.5f)).padding(4.dp))
            }
            
            IconButton(
                onClick = onToggleDebug,
                modifier = Modifier
                    .size(48.dp)
                    .background(Color.Black.copy(alpha = 0.3f), CircleShape)
            ) {
                Icon(Icons.Filled.Settings, contentDescription = "Debug", tint = if (debugMode) Color.Green else Color.White)
            }
            
            Spacer(modifier = Modifier.weight(1f))
            IconButton(
                onClick = onToggleInventory,
                modifier = Modifier
                    .size(48.dp)
                    .background(Color.Black.copy(alpha = 0.3f), CircleShape)
            ) {
                Icon(Icons.Filled.Menu, contentDescription = "Inventory", tint = Color.White)
            }
        }

        // Crosshair
        Box(modifier = Modifier.align(Alignment.Center).size(16.dp)) {
            Box(modifier = Modifier.fillMaxHeight().width(2.dp).background(Color.White.copy(alpha = 0.8f)).align(Alignment.Center))
            Box(modifier = Modifier.fillMaxWidth().height(2.dp).background(Color.White.copy(alpha = 0.8f)).align(Alignment.Center))
        }

        // Joystick
        Joystick(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .padding(bottom = 32.dp, start = 16.dp),
            onMove = { x, y ->
                MainActivity.nativeMoveJoystick(x, y)
            }
        )

        // Action Buttons
        Box(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(bottom = 32.dp, end = 16.dp)
                .size(160.dp)
        ) {
            // Jump
            ActionButton(
                icon = Icons.AutoMirrored.Filled.ArrowForward,
                modifier = Modifier.align(Alignment.TopCenter).rotate(-90f),
                onDown = { MainActivity.nativeAction("jump_down") },
                onUp = { MainActivity.nativeAction("jump_up") }
            )
            // Crouch
            ActionButton(
                icon = Icons.AutoMirrored.Filled.ArrowForward,
                modifier = Modifier.align(Alignment.BottomCenter).rotate(90f),
                onDown = { MainActivity.nativeAction("sneak") }
            )
            // Place
            ActionButton(
                icon = Icons.Filled.Add,
                modifier = Modifier.align(Alignment.CenterStart),
                onDown = { MainActivity.nativeAction("place") }
            )
            // Break
            ActionButton(
                icon = Icons.Filled.Close,
                modifier = Modifier.align(Alignment.CenterEnd),
                onDown = { MainActivity.nativeAction("break") }
            )
        }

        // Hotbar
        var inventoryState by remember { mutableStateOf<IntArray>(MainActivity.nativeGetInventory()) }
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
                
                InventorySlotUI(
                    slotIndex = invIndex,
                    itemId = itemId,
                    count = count,
                    isSelected = (i == selectedSlot),
                    atlasBitmap = atlasBitmap,
                    onClick = {
                        MainActivity.nativeAction("select_slot_$i")
                    },
                    onLongClick = {}
                )
            }
        }
    }
}
"""
    text = text.replace(old_hud, new_hud)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
