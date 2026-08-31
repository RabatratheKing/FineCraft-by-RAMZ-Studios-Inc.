import re

with open("app/src/main/cpp/world/World.cpp", "r") as f:
    text = f.read()

pattern = r'if \(b1 == b2\) \{.*?mask\[n\] = 0;\n\s*\}\n\s*\} else if \(isOpaque\(b1\) \&\& \!isOpaque\(b2\)\) \{.*?mask\[n\] = 0;\n\s*\}'

new_logic = """if (b1 == b2) {
                        mask[n] = 0;
                    } else {
                        bool draw1 = (b1 != 0 && b1 != 6 && (b2 == 0 || b2 == 5 || b2 == 6 || b2 == 9));
                        bool draw2 = (b2 != 0 && b2 != 6 && (b1 == 0 || b1 == 5 || b1 == 6 || b1 == 9));
                        
                        if (b1 == 6 && b2 == 0) draw1 = true;
                        if (b2 == 6 && b1 == 0) draw2 = true;
                        
                        if (draw1 && !draw2) {
                            mask[n] = b1 | (1 << 8); 
                        } else if (!draw1 && draw2) {
                            mask[n] = b2 | (2 << 8); 
                        } else if (draw1 && draw2) {
                            mask[n] = b1 | (1 << 8);
                        } else {
                            mask[n] = 0;
                        }
                    }"""

text = re.sub(pattern, new_logic, text, flags=re.DOTALL)
with open("app/src/main/cpp/world/World.cpp", "w") as f:
    f.write(text)
