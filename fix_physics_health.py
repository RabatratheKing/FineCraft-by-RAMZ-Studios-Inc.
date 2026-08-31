import re

with open("app/src/main/cpp/player/Physics.h", "r") as f:
    text = f.read()

if "void applyDamage" not in text:
    text += "\nvoid applyDamage(float amount, const char* source);\n"
    with open("app/src/main/cpp/player/Physics.h", "w") as f:
        f.write(text)

