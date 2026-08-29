import re

with open("app/src/main/cpp/gameplay/Raycast.cpp", "r") as f:
    text = f.read()

text = text.replace("chunks[{pcx, pcz}].isDirty = true;", "chunks[{pcx, pcz}].isDirty = true;\n                                        chunks[{pcx, pcz}].isModified = true;")
text = text.replace("chunks[{cx, cz}].isDirty = true;", "chunks[{cx, cz}].isDirty = true;\n                            chunks[{cx, cz}].isModified = true;")

with open("app/src/main/cpp/gameplay/Raycast.cpp", "w") as f:
    f.write(text)
