"""
High-performance OpenGL triangle swarm using instanced rendering.
Target: 100,000 triangles at 60fps in a 900x900 window.
Press P to pause/resume. FPS shown in top-left corner. ESC to quit.

Install dependencies:
    pip install pygame PyOpenGL PyOpenGL_accelerate numpy
"""

# ── Imports ────────────────────────────────────────────────────────────────────
import ctypes
import math
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_ESCAPE, K_p
from OpenGL.GL import *
from OpenGL.GL import shaders

# ── Configuration ──────────────────────────────────────────────────────────────
WINDOW_W, WINDOW_H = 900, 900
NUM_TRIANGLES      = 100_000   # try cranking this up — 500_000 works too!
TRI_HALF           = 5         # half-size so triangle fits in ~10x10 px box
MIN_SPEED          = 1.0
MAX_SPEED          = 5.0
TARGET_FPS         = 60

# ── Triangle vertex + instance shader ─────────────────────────────────────────
VERT_SRC = """
#version 330 core

layout(location = 0) in vec2 aVertex;   // triangle shape (shared)

// Per-instance data
layout(location = 1) in vec2  iPos;
layout(location = 2) in float iAngle;
layout(location = 3) in float iHue;

out vec3 vColor;

uniform vec2 uResolution;

vec3 hsv2rgb(float h, float s, float v) {
    float c = v * s;
    float x = c * (1.0 - abs(mod(h * 6.0, 2.0) - 1.0));
    float m = v - c;
    vec3 rgb;
    if      (h < 1.0/6.0) rgb = vec3(c, x, 0);
    else if (h < 2.0/6.0) rgb = vec3(x, c, 0);
    else if (h < 3.0/6.0) rgb = vec3(0, c, x);
    else if (h < 4.0/6.0) rgb = vec3(0, x, c);
    else if (h < 5.0/6.0) rgb = vec3(x, 0, c);
    else                   rgb = vec3(c, 0, x);
    return rgb + m;
}

void main() {
    float c = cos(iAngle);
    float s = sin(iAngle);
    vec2 rotated = vec2(c * aVertex.x - s * aVertex.y,
                        s * aVertex.x + c * aVertex.y);
    vec2 world = iPos + rotated;
    // Map pixel coords [0, resolution] to NDC [-1, 1]
    vec2 ndc = (world / uResolution) * 2.0 - 1.0;
    gl_Position = vec4(ndc, 0.0, 1.0);
    vColor = hsv2rgb(iHue, 0.9, 1.0);
}
"""

FRAG_SRC = """
#version 330 core
in  vec3 vColor;
out vec4 FragColor;
void main() {
    FragColor = vec4(vColor, 1.0);
}
"""

# ── FPS overlay shaders ────────────────────────────────────────────────────────
FPS_VERT = """
#version 330 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aUV;
out vec2 vUV;
uniform vec2 uRes;
void main() {
    vec2 ndc = (aPos / uRes) * 2.0 - 1.0;
    gl_Position = vec4(ndc, 0.0, 1.0);
    vUV = aUV;
}
"""

FPS_FRAG = """
#version 330 core
in  vec2 vUV;
out vec4 FragColor;
uniform sampler2D uTex;
void main() {
    // Sample full RGBA — alpha channel controls transparency
    vec4 t = texture(uTex, vUV);
    FragColor = vec4(t.rgb, t.a);
}
"""


def compile_program(vert_src, frag_src):
    v = shaders.compileShader(vert_src, GL_VERTEX_SHADER)
    f = shaders.compileShader(frag_src, GL_FRAGMENT_SHADER)
    return shaders.compileProgram(v, f)


def main():
    pygame.init()
    pygame.display.set_mode((WINDOW_W, WINDOW_H), DOUBLEBUF | OPENGL)
    pygame.display.set_caption(f"Triangle Swarm  —  {NUM_TRIANGLES:,} instances")
    font = pygame.font.SysFont("monospace", 20, bold=True)

    # ── Triangle shape: arrow pointing right (+X), apex at tip ────────────────
    verts = np.array([
        [ TRI_HALF,  0.0           ],   # tip
        [-TRI_HALF,  TRI_HALF*0.7  ],   # back-left
        [-TRI_HALF, -TRI_HALF*0.7  ],   # back-right
    ], dtype=np.float32)

    # ── Per-instance state arrays ──────────────────────────────────────────────
    N  = NUM_TRIANGLES
    px = np.random.uniform(0, WINDOW_W, N).astype(np.float32)
    py = np.random.uniform(0, WINDOW_H, N).astype(np.float32)
    pa = np.random.uniform(0, math.tau,  N).astype(np.float32)
    ps = np.random.uniform(MIN_SPEED, MAX_SPEED, N).astype(np.float32)
    ph = np.random.uniform(0, 1, N).astype(np.float32)

    # ── OpenGL state ───────────────────────────────────────────────────────────
    glClearColor(0.05, 0.05, 0.10, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    tri_prog = compile_program(VERT_SRC, FRAG_SRC)
    fps_prog = compile_program(FPS_VERT, FPS_FRAG)

    # ── Triangle VAO ──────────────────────────────────────────────────────────
    tri_vao = glGenVertexArrays(1)
    glBindVertexArray(tri_vao)

    vbo_shape = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_shape)
    glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)

    # Instance VBO:  [px, py, angle, hue]  — 4 floats × 4 bytes = 16-byte stride
    instance_data = np.column_stack([px, py, pa, ph]).astype(np.float32)
    vbo_inst = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_inst)
    glBufferData(GL_ARRAY_BUFFER, instance_data.nbytes, instance_data, GL_STREAM_DRAW)

    stride = 16
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glVertexAttribDivisor(1, 1)

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(8))
    glVertexAttribDivisor(2, 1)

    glEnableVertexAttribArray(3)
    glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
    glVertexAttribDivisor(3, 1)

    glBindVertexArray(0)

    # ── FPS overlay VAO ────────────────────────────────────────────────────────
    fps_vao = glGenVertexArrays(1)
    fps_vbo = glGenBuffers(1)
    fps_tex = glGenTextures(1)

    # Upload resolution uniform once
    glUseProgram(tri_prog)
    glUniform2f(glGetUniformLocation(tri_prog, "uResolution"), WINDOW_W, WINDOW_H)

    # ── Main loop ──────────────────────────────────────────────────────────────
    clock       = pygame.time.Clock()
    paused      = False
    fps_display = 0.0
    fps_accum   = 0.0
    fps_frames  = 0

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == QUIT:
                running = False
            elif ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    running = False
                elif ev.key == K_p:
                    paused = not paused

        clock.tick(TARGET_FPS)
        actual_fps = clock.get_fps()

        # ── Physics update ─────────────────────────────────────────────────────
        if not paused:
            px += np.cos(pa) * ps
            py += np.sin(pa) * ps

            margin = TRI_HALF + 2
            oob = ((px < -margin) | (px > WINDOW_W + margin) |
                   (py < -margin) | (py > WINDOW_H + margin))
            n_oob = int(oob.sum())
            if n_oob:
                px[oob] = np.random.uniform(0, WINDOW_W, n_oob).astype(np.float32)
                py[oob] = np.random.uniform(0, WINDOW_H, n_oob).astype(np.float32)
                pa[oob] = np.random.uniform(0, math.tau,  n_oob).astype(np.float32)
                ps[oob] = np.random.uniform(MIN_SPEED, MAX_SPEED, n_oob).astype(np.float32)
                ph[oob] = np.random.uniform(0, 1, n_oob).astype(np.float32)

            instance_data[:, 0] = px
            instance_data[:, 1] = py
            instance_data[:, 2] = pa
            instance_data[:, 3] = ph
            glBindBuffer(GL_ARRAY_BUFFER, vbo_inst)
            glBufferSubData(GL_ARRAY_BUFFER, 0, instance_data.nbytes, instance_data)

        # ── Draw triangles ─────────────────────────────────────────────────────
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(tri_prog)
        glBindVertexArray(tri_vao)
        glDrawArraysInstanced(GL_TRIANGLES, 0, 3, N)
        glBindVertexArray(0)

        # ── FPS counter (smoothed over 10 frames) ──────────────────────────────
        fps_frames += 1
        fps_accum  += actual_fps
        if fps_frames >= 10:
            fps_display = fps_accum / fps_frames
            fps_accum   = 0.0
            fps_frames  = 0

        status = "  [PAUSED]" if paused else ""
        label  = f" FPS: {fps_display:5.1f}  |  {N:,} triangles{status} "

        # Render text via pygame onto a surface with an opaque background,
        # then upload as RGBA texture.
        # flip=False keeps the image in OpenGL's bottom-left-origin convention.
        text_surf = font.render(label, True, (255, 220, 50), (15, 15, 25))
        tw, th    = text_surf.get_size()
        tex_data  = pygame.image.tostring(text_surf, "RGBA", False)

        glBindTexture(GL_TEXTURE_2D, fps_tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tw, th, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, tex_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        # Quad corners in GL pixel space (Y=0 at bottom of screen)
        PAD = 6
        x0 = PAD
        x1 = PAD + tw
        y0 = WINDOW_H - PAD - th   # bottom of text quad
        y1 = WINDOW_H - PAD        # top of text quad

        quad = np.array([
            x0, y0,  0.0, 0.0,
            x1, y0,  1.0, 0.0,
            x1, y1,  1.0, 1.0,
            x0, y0,  0.0, 0.0,
            x1, y1,  1.0, 1.0,
            x0, y1,  0.0, 1.0,
        ], dtype=np.float32)

        glUseProgram(fps_prog)
        glUniform2f(glGetUniformLocation(fps_prog, "uRes"), WINDOW_W, WINDOW_H)
        glUniform1i(glGetUniformLocation(fps_prog, "uTex"), 0)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, fps_tex)

        glBindVertexArray(fps_vao)
        glBindBuffer(GL_ARRAY_BUFFER, fps_vbo)
        glBufferData(GL_ARRAY_BUFFER, quad.nbytes, quad, GL_STREAM_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()