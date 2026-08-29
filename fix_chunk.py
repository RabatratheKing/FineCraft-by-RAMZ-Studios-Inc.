import re

with open("app/src/main/cpp/core/Globals.h", "r") as f:
    text = f.read()

text = text.replace("bool isDirty = false;", "bool isDirty = false;\n    bool isModified = false;")

with open("app/src/main/cpp/core/Globals.h", "w") as f:
    f.write(text)
