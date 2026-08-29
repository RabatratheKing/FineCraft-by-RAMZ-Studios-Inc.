import re

with open("app/src/main/cpp/gameplay/Inventory.h", "r") as f:
    text = f.read()

if "craftingGrid" not in text:
    text += """
extern InventorySlot craftingGrid[4];
extern InventorySlot craftingOutput;

void updateCraftingOutput();
void takeCraftingOutput();
void swapCraftingSlot(int invSlot, int craftSlot); // Moves item between inv and 2x2 grid
void swapCraftingToCrafting(int craftSlotA, int craftSlotB);
void clearCraftingGrid(); // put items back to inventory if closed
"""

with open("app/src/main/cpp/gameplay/Inventory.h", "w") as f:
    f.write(text)

with open("app/src/main/cpp/gameplay/Inventory.cpp", "r") as f:
    text = f.read()

text = text.replace('{8, {8, "Sand", 64, true}}', '{8, {8, "Sand", 64, true}},\n    {9, {9, "Sticks", 64, false}}')

if "craftingGrid[4]" not in text:
    text += """
InventorySlot craftingGrid[4] = {{0,0}, {0,0}, {0,0}, {0,0}};
InventorySlot craftingOutput = {0,0};

void updateCraftingOutput() {
    int woodCount = 0;
    int planksCount = 0;
    int otherCount = 0;
    for(int i=0; i<4; i++) {
        if(craftingGrid[i].itemId == 4) woodCount += craftingGrid[i].count;
        else if(craftingGrid[i].itemId == 7) planksCount += craftingGrid[i].count;
        else if(craftingGrid[i].itemId != 0) otherCount++;
    }
    
    craftingOutput = {0, 0};
    
    // Wood -> 4 Planks
    if(otherCount == 0 && planksCount == 0 && woodCount >= 1) {
        craftingOutput = {7, 4};
    }
    // 2 Planks -> 4 Sticks
    else if(otherCount == 0 && woodCount == 0 && planksCount >= 2) {
        craftingOutput = {9, 4};
    }
}

void takeCraftingOutput() {
    updateCraftingOutput();
    if(craftingOutput.itemId != 0) {
        if(addItem(craftingOutput.itemId, craftingOutput.count)) {
            // consume ingredients
            if(craftingOutput.itemId == 7) { // wood -> planks
                int needed = 1;
                for(int i=0; i<4 && needed>0; i++) {
                    if(craftingGrid[i].itemId == 4) {
                        int take = std::min((int)craftingGrid[i].count, needed);
                        craftingGrid[i].count -= take;
                        if(craftingGrid[i].count == 0) craftingGrid[i].itemId = 0;
                        needed -= take;
                    }
                }
            } else if(craftingOutput.itemId == 9) { // planks -> sticks
                int needed = 2;
                for(int i=0; i<4 && needed>0; i++) {
                    if(craftingGrid[i].itemId == 7) {
                        int take = std::min((int)craftingGrid[i].count, needed);
                        craftingGrid[i].count -= take;
                        if(craftingGrid[i].count == 0) craftingGrid[i].itemId = 0;
                        needed -= take;
                    }
                }
            }
            updateCraftingOutput();
        }
    }
}

void swapCraftingSlot(int invSlot, int craftSlot) {
    if(invSlot < 0 || invSlot >= INVENTORY_SIZE || craftSlot < 0 || craftSlot >= 4) return;
    
    if (inventory[invSlot].itemId == craftingGrid[craftSlot].itemId && inventory[invSlot].itemId != 0) {
        // Try to merge
        uint16_t maxStack = getBlockMetadata(inventory[invSlot].itemId).maxStack;
        if (craftingGrid[craftSlot].count < maxStack) {
            uint16_t space = maxStack - craftingGrid[craftSlot].count;
            if (inventory[invSlot].count <= space) {
                craftingGrid[craftSlot].count += inventory[invSlot].count;
                inventory[invSlot].itemId = 0;
                inventory[invSlot].count = 0;
            } else {
                craftingGrid[craftSlot].count += space;
                inventory[invSlot].count -= space;
            }
            updateCraftingOutput();
            return;
        }
    }
    
    InventorySlot temp = inventory[invSlot];
    inventory[invSlot] = craftingGrid[craftSlot];
    craftingGrid[craftSlot] = temp;
    updateCraftingOutput();
}

void swapCraftingToCrafting(int craftSlotA, int craftSlotB) {
    if(craftSlotA < 0 || craftSlotA >= 4 || craftSlotB < 0 || craftSlotB >= 4) return;
    InventorySlot temp = craftingGrid[craftSlotA];
    craftingGrid[craftSlotA] = craftingGrid[craftSlotB];
    craftingGrid[craftSlotB] = temp;
    updateCraftingOutput();
}

void clearCraftingGrid() {
    for(int i=0; i<4; i++) {
        if(craftingGrid[i].itemId != 0) {
            addItem(craftingGrid[i].itemId, craftingGrid[i].count);
            craftingGrid[i] = {0, 0};
        }
    }
    updateCraftingOutput();
}
"""

with open("app/src/main/cpp/gameplay/Inventory.cpp", "w") as f:
    f.write(text)
