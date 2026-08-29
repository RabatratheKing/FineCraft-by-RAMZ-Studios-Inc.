import re

with open("app/src/main/AndroidManifest.xml", "r") as f:
    text = f.read()

if "android.permission.INTERNET" not in text:
    text = text.replace("<application", '<uses-permission android:name="android.permission.INTERNET" />\n    <application')

with open("app/src/main/AndroidManifest.xml", "w") as f:
    f.write(text)
