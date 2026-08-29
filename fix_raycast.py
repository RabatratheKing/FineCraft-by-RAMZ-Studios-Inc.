import re

with open("app/src/main/cpp/gameplay/Raycast.cpp", "r") as f:
    text = f.read()

text = text.replace('#include "../core/Globals.h"', '#include "../core/Globals.h"\n#include "Inventory.h"')

pattern_place = r"if \(hotbar\[selectedHotbarSlot\]\.count > 0\) \{[\s\S]*?hotbar\[selectedHotbarSlot\]\.count--;\n\s*\}"
replacement_place = """uint16_t selectedItem = inventory[selectedHotbarSlot + 27].itemId;
                                    if (selectedItem != 0 && getBlockMetadata(selectedItem).placeable) {
                                        chunks[{pcx, pcz}].data[plx][pby][plz] = selectedItem;
                                        chunks[{pcx, pcz}].isDirty = true;
                                        if (plx == 0 && chunks.find({pcx-1, pcz}) != chunks.end()) chunks[{pcx-1, pcz}].isDirty = true;
                                        if (plx == CHUNK_SIZE-1 && chunks.find({pcx+1, pcz}) != chunks.end()) chunks[{pcx+1, pcz}].isDirty = true;
                                        if (plz == 0 && chunks.find({pcx, pcz-1}) != chunks.end()) chunks[{pcx, pcz-1}].isDirty = true;
                                        if (plz == CHUNK_SIZE-1 && chunks.find({pcx, pcz+1}) != chunks.end()) chunks[{pcx, pcz+1}].isDirty = true;
                                        consumeItem(selectedHotbarSlot + 27, 1);
                                    }"""

text = re.sub(pattern_place, replacement_place, text)

pattern_break = r"chunks\[\{cx, cz\}\]\.data\[lx\]\[by\]\[lz\] = 0;\n\s*chunks\[\{cx, cz\}\]\.isDirty = true;[\s\S]*?break;\n\s*\}\n\s*\}"
replacement_break = """// Try to add broken block to inventory
                        if (addItem(currentBlock, 1)) {
                            chunks[{cx, cz}].data[lx][by][lz] = 0;
                            chunks[{cx, cz}].isDirty = true;
                            if (lx == 0 && chunks.find({cx-1, cz}) != chunks.end()) chunks[{cx-1, cz}].isDirty = true;
                            if (lx == CHUNK_SIZE-1 && chunks.find({cx+1, cz}) != chunks.end()) chunks[{cx+1, cz}].isDirty = true;
                            if (lz == 0 && chunks.find({cx, cz-1}) != chunks.end()) chunks[{cx, cz-1}].isDirty = true;
                            if (lz == CHUNK_SIZE-1 && chunks.find({cx, cz+1}) != chunks.end()) chunks[{cx, cz+1}].isDirty = true;
                        }"""

text = re.sub(pattern_break, replacement_break, text)

with open("app/src/main/cpp/gameplay/Raycast.cpp", "w") as f:
    f.write(text)
