import re

with open("app/src/main/cpp/platform/android/JNI.cpp", "r") as f:
    text = f.read()

text = text.replace('#include "core/Globals.h"', '#include "core/Globals.h"\n#include "world/SaveManager.h"')

with open("app/src/main/cpp/platform/android/JNI.cpp", "w") as f:
    f.write(text)
