import re

with open("app/src/main/cpp/player/Physics.cpp", "r") as f:
    text = f.read()

pattern = r'if \(isDead\) \{'
replacement = """if (playerY < -64.0f && !isDead && !isDebugFly) {
        applyDamage(20.0f, "void");
    }
    
    if (isDead) {"""
    
if "void" not in text:
    text = text.replace("if (isDead) {", replacement)

with open("app/src/main/cpp/player/Physics.cpp", "w") as f:
    f.write(text)
