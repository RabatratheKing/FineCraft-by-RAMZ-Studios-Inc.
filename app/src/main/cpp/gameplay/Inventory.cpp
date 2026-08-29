#include "Inventory.h"
#include <unordered_map>

InventorySlot inventory[INVENTORY_SIZE];
int selectedHotbarSlot = 0;
bool isInventoryOpen = false;

static std::unordered_map<uint16_t, BlockMetadata> blockRegistry = {
    {0, {0, "Air", 0, false}},
    {1, {1, "Grass", 64, true}},
    {2, {2, "Dirt", 64, true}},
    {3, {3, "Stone", 64, true}},
    {4, {4, "Wood", 64, true}},
    {5, {5, "Leaves", 64, true}},
    {6, {6, "Water", 64, false}}, // Water is not placeable/collectible normally
    {7, {7, "Planks", 64, true}},
    {8, {8, "Sand", 64, true}}
};

void initInventory() {
    for (int i = 0; i < INVENTORY_SIZE; i++) {
        inventory[i].itemId = 0;
        inventory[i].count = 0;
    }
    // Grass x64, Dirt x64, Stone x64, Wood x32, Sand x32
    // Hotbar is usually slots 27-35 (last 9 slots)
    // We'll put them in the hotbar (slots 27 to 31)
    inventory[27] = {1, 64};
    inventory[28] = {2, 64};
    inventory[29] = {3, 64};
    inventory[30] = {4, 32};
    inventory[31] = {8, 32};
}

const BlockMetadata& getBlockMetadata(uint16_t id) {
    auto it = blockRegistry.find(id);
    if (it != blockRegistry.end()) {
        return it->second;
    }
    return blockRegistry[0]; // Air
}

bool addItem(uint16_t itemId, uint16_t count) {
    if (itemId == 0) return false;
    uint16_t maxStack = getBlockMetadata(itemId).maxStack;
    if (maxStack == 0) return false;

    // First pass: try to add to existing partial stacks
    for (int i = 0; i < INVENTORY_SIZE; i++) {
        if (inventory[i].itemId == itemId && inventory[i].count < maxStack) {
            uint16_t space = maxStack - inventory[i].count;
            if (count <= space) {
                inventory[i].count += count;
                return true;
            } else {
                inventory[i].count += space;
                count -= space;
            }
        }
    }

    // Second pass: find empty slots
    for (int i = 0; i < INVENTORY_SIZE; i++) {
        if (inventory[i].count == 0 || inventory[i].itemId == 0) {
            if (count <= maxStack) {
                inventory[i].itemId = itemId;
                inventory[i].count = count;
                return true;
            } else {
                inventory[i].itemId = itemId;
                inventory[i].count = maxStack;
                count -= maxStack;
            }
        }
    }

    return false; // Could not fit all items
}

bool consumeItem(int slotIndex, uint16_t count) {
    if (slotIndex < 0 || slotIndex >= INVENTORY_SIZE) return false;
    if (inventory[slotIndex].count >= count) {
        inventory[slotIndex].count -= count;
        if (inventory[slotIndex].count == 0) {
            inventory[slotIndex].itemId = 0;
        }
        return true;
    }
    return false;
}

void swapSlots(int slotA, int slotB) {
    if (slotA < 0 || slotA >= INVENTORY_SIZE || slotB < 0 || slotB >= INVENTORY_SIZE) return;
    
    if (inventory[slotA].itemId == inventory[slotB].itemId && inventory[slotA].itemId != 0) {
        // Try to merge
        uint16_t maxStack = getBlockMetadata(inventory[slotA].itemId).maxStack;
        if (inventory[slotB].count < maxStack) {
            uint16_t space = maxStack - inventory[slotB].count;
            if (inventory[slotA].count <= space) {
                inventory[slotB].count += inventory[slotA].count;
                inventory[slotA].itemId = 0;
                inventory[slotA].count = 0;
            } else {
                inventory[slotB].count += space;
                inventory[slotA].count -= space;
            }
            return;
        }
    }
    
    InventorySlot temp = inventory[slotA];
    inventory[slotA] = inventory[slotB];
    inventory[slotB] = temp;
}
