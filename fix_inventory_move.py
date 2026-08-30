import re

with open("app/src/main/cpp/gameplay/Inventory.h", "r") as f:
    text = f.read()

bindings = """
bool moveItems(int srcType, int srcSlot, int destType, int destSlot, int amount);
"""
if "moveItems(" not in text:
    text = text.replace("void swapCraftingToCrafting(int craftSlotA, int craftSlotB);", "void swapCraftingToCrafting(int craftSlotA, int craftSlotB);\n" + bindings)

with open("app/src/main/cpp/gameplay/Inventory.h", "w") as f:
    f.write(text)

with open("app/src/main/cpp/gameplay/Inventory.cpp", "r") as f:
    text = f.read()

impl = """
bool moveItems(int srcType, int srcSlot, int destType, int destSlot, int amount) {
    if (amount <= 0) return false;
    
    InventorySlot* src = nullptr;
    InventorySlot* dest = nullptr;
    
    if (srcType == 0) {
        if (srcSlot < 0 || srcSlot >= INVENTORY_SIZE) return false;
        src = &inventory[srcSlot];
    } else if (srcType == 1) {
        if (srcSlot < 0 || srcSlot >= 4) return false;
        src = &craftingGrid[srcSlot];
    } else return false;
    
    if (destType == 0) {
        if (destSlot < 0 || destSlot >= INVENTORY_SIZE) return false;
        dest = &inventory[destSlot];
    } else if (destType == 1) {
        if (destSlot < 0 || destSlot >= 4) return false;
        dest = &craftingGrid[destSlot];
    } else return false;
    
    if (src->count < amount) amount = src->count;
    if (amount <= 0) return false;
    
    if (dest->itemId == 0) {
        dest->itemId = src->itemId;
        dest->count = amount;
        src->count -= amount;
        if (src->count == 0) src->itemId = 0;
        updateCraftingOutput();
        return true;
    } else if (dest->itemId == src->itemId) {
        uint16_t maxStack = getBlockMetadata(dest->itemId).maxStack;
        if (dest->count < maxStack) {
            uint16_t space = maxStack - dest->count;
            int move = (amount < space) ? amount : space;
            dest->count += move;
            src->count -= move;
            if (src->count == 0) src->itemId = 0;
            updateCraftingOutput();
            return true;
        }
    }
    return false;
}
"""
if "moveItems(" not in text:
    text += impl

with open("app/src/main/cpp/gameplay/Inventory.cpp", "w") as f:
    f.write(text)
