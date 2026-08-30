import re

with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    text = f.read()

# Replace InventorySlotUI
old_slot = """@Composable
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
                9 -> Color(0xFF5C3A21) // Sticks
                else -> Color.Gray
            }
            Box(modifier = Modifier.fillMaxSize().padding(4.dp).background(color))
            Text(text = "$count", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.BottomEnd).padding(2.dp))
        }
    }
}"""

new_slot = """@Composable
fun InventorySlotUI(
    slotIndex: Int, 
    itemId: Int,
    count: Int,
    isSelected: Boolean, 
    atlasBitmap: ImageBitmap?, 
    onClick: () -> Unit, 
    onLongClick: () -> Unit = {}
) {
    Box(
        modifier = Modifier
            .size(40.dp)
            .background(if (isSelected) Color.White.copy(alpha = 0.3f) else Color.Black.copy(alpha = 0.5f), RoundedCornerShape(4.dp))
            .border(2.dp, if (isSelected) Color.Yellow else Color.Gray, RoundedCornerShape(4.dp))
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { onClick() },
                    onLongPress = { onLongClick() }
                )
            }
    ) {
        if (itemId > 0) {
            if (atlasBitmap != null) {
                val texIndex = when(itemId) {
                    1 -> 1
                    2 -> 2
                    3 -> 3
                    4 -> 4
                    5 -> 6
                    7 -> 4
                    8 -> 8
                    9 -> 9
                    else -> 0
                }
                val tileX = texIndex % 16
                val tileY = texIndex / 16
                val painter = BitmapPainter(
                    image = atlasBitmap,
                    srcOffset = IntOffset(tileX * 16, tileY * 16),
                    srcSize = IntSize(16, 16),
                    filterQuality = FilterQuality.None
                )
                Image(
                    painter = painter,
                    contentDescription = null,
                    modifier = Modifier.fillMaxSize().padding(4.dp),
                    contentScale = ContentScale.Fit
                )
            } else {
                val color = when(itemId) {
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
            }
            Text(text = "$count", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.BottomEnd).padding(2.dp))
        }
    }
}"""

if old_slot in text:
    text = text.replace(old_slot, new_slot)
else:
    print("Could not find old_slot")

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(text)
