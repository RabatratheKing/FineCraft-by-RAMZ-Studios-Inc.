import re

with open("app/build.gradle.kts", "r") as f:
    text = f.read()

pattern = r"compileSdk \{ version = release\(36\) \{ minorApiLevel = 1 \} \}"
replacement = """compileSdk { version = release(36) { minorApiLevel = 1 } }
  ndkVersion = "27.2.12479018\""""

text = re.sub(pattern, replacement, text)

with open("app/build.gradle.kts", "w") as f:
    f.write(text)
