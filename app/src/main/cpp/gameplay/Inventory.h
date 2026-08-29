#pragma once
#include <cstdint>
#include <string>

const int INVENTORY_SIZE = 36;
const int HOTBAR_SIZE = 9;

struct BlockMetadata {
    uint16_t id;
    std::string name;
    uint16_t maxStack;
    bool placeable;
};

struct InventorySlot {
    uint16_t itemId;
    uint16_t count;
};

extern InventorySlot inventory[INVENTORY_SIZE];
extern int selectedHotbarSlot;
extern bool isInventoryOpen;

void initInventory();
bool addItem(uint16_t itemId, uint16_t count);
bool consumeItem(int slotIndex, uint16_t count);
void swapSlots(int slotA, int slotB);
const BlockMetadata& getBlockMetadata(uint16_t id);
