import re

with open("app/src/main/cpp/core/Globals.h", "r") as f:
    text = f.read()

if "extern int worldSeed;" not in text:
    text += "\nextern int worldSeed;\n"

with open("app/src/main/cpp/core/Globals.h", "w") as f:
    f.write(text)

with open("app/src/main/cpp/core/Globals.cpp", "r") as f:
    text = f.read()

if "int worldSeed =" not in text:
    text += "\nint worldSeed = 123456;\n"

with open("app/src/main/cpp/core/Globals.cpp", "w") as f:
    f.write(text)
