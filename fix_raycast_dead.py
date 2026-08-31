import re

with open("app/src/main/cpp/gameplay/Raycast.cpp", "r") as f:
    text = f.read()

pattern = r'void tickInteraction\(float dt\) \{'
replacement = """void tickInteraction(float dt) {
    if (isDead) return;"""
if "if (isDead) return;" not in text:
    text = text.replace("void tickInteraction(float dt) {", replacement)

with open("app/src/main/cpp/gameplay/Raycast.cpp", "w") as f:
    f.write(text)
