import re

with open("app/src/main/cpp/world/World.cpp", "r") as f:
    text = f.read()

# Replace isOpaque lambda
is_opaque = r'auto isOpaque = \[\]\(uint8_t b\) -> bool \{.*?\n\s*\};'
new_is_opaque = """auto isOpaque = [](uint8_t b) -> bool {
        return b != 0 && b != 5 && b != 6 && b != 9; // Air, Leaves, Water, Scaffolding are non-opaque
    };"""
text = re.sub(is_opaque, new_is_opaque, text, flags=re.DOTALL)

# Replace the mask logic
mask_logic = r'if \(b1 == b2\) \{.*?mask\[n\] = 0;\n\s*\}'
new_mask_logic = """if (b1 == b2) {
                        mask[n] = 0;
                    } else {
                        bool draw1 = (b1 != 0 && b1 != 6 && (b2 == 0 || b2 == 5 || b2 == 6 || b2 == 9));
                        bool draw2 = (b2 != 0 && b2 != 6 && (b1 == 0 || b1 == 5 || b1 == 6 || b1 == 9));
                        
                        // Special rules for water
                        if (b1 == 6 && b2 == 0) draw1 = true;
                        if (b2 == 6 && b1 == 0) draw2 = true;
                        
                        if (draw1 && !draw2) {
                            mask[n] = b1 | (1 << 8); // b1 facing +d
                        } else if (!draw1 && draw2) {
                            mask[n] = b2 | (2 << 8); // b2 facing -d
                        } else if (draw1 && draw2) {
                            // If both want to draw, prioritize the opaque one or just b1 (greedy meshing limitation)
                            // Normally we don't have two non-opaque blocks facing each other that BOTH need faces drawn
                            // except maybe Leaves vs Scaffolding.
                            mask[n] = b1 | (1 << 8);
                        } else {
                            mask[n] = 0;
                        }
                    }"""
text = re.sub(mask_logic, new_mask_logic, text, flags=re.DOTALL)

with open("app/src/main/cpp/world/World.cpp", "w") as f:
    f.write(text)
