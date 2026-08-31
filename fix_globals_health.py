import re

with open("app/src/main/cpp/core/Globals.h", "r") as f:
    text = f.read()

text = text.replace("FLYING", "FLYING,\n    DEAD")

if "extern float playerHealth;" not in text:
    text += """
extern float playerHealth;
extern float playerMaxHealth;
extern bool isDead;
extern float damageCooldown;
extern float fallDistance;
extern float highestY;
extern float hurtTime;
"""
    with open("app/src/main/cpp/core/Globals.h", "w") as f:
        f.write(text)

with open("app/src/main/cpp/core/Globals.cpp", "r") as f:
    text = f.read()

if "float playerHealth" not in text:
    text += """
float playerHealth = 20.0f;
float playerMaxHealth = 20.0f;
bool isDead = false;
float damageCooldown = 0.0f;
float fallDistance = 0.0f;
float highestY = 0.0f;
float hurtTime = 0.0f;
"""
    with open("app/src/main/cpp/core/Globals.cpp", "w") as f:
        f.write(text)
