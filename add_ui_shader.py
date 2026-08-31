import re

with open("app/src/main/cpp/shaders/Shaders.h", "r") as f:
    text = f.read()

if "uiVertexShaderSource" not in text:
    text += """
const char* uiVertexShaderSource = R"(#version 300 es
    layout(location = 0) in vec2 aPos;
    layout(location = 1) in vec2 aUV;
    uniform mat4 projection;
    uniform mat4 model;
    out vec2 vUV;
    void main() {
        gl_Position = projection * model * vec4(aPos, 0.0, 1.0);
        vUV = aUV;
    }
)";

const char* uiFragmentShaderSource = R"(#version 300 es
    precision mediump float;
    in vec2 vUV;
    uniform vec4 u_color;
    uniform bool u_useTex;
    uniform sampler2D u_tex;
    out vec4 FragColor;
    void main() {
        if (u_useTex) {
            vec4 texColor = texture(u_tex, vUV);
            if (texColor.a < 0.1) discard;
            FragColor = texColor * u_color;
        } else {
            FragColor = u_color;
        }
    }
)";
"""
    with open("app/src/main/cpp/shaders/Shaders.h", "w") as f:
        f.write(text)

