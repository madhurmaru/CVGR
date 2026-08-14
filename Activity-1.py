import glfw
from OpenGL.GL import *
import math
import ctypes

# Window dimensions
WIDTH, HEIGHT = 800, 600

# Ball properties
ball_x, ball_y = -1.0, 0.0  # Start at the far left edge (-1.0)
ball_radius = 0.05
ball_speed = 0.015          # Controlled automated speed per frame

# Modern OpenGL Shaders
VERTEX_SHADER_SOURCE = """
#version 330 core
layout (location = 0) in vec2 aPos;
uniform vec2 uOffset;
uniform float uAspect;
void main() {
    gl_Position = vec4((aPos.x + uOffset.x) * uAspect, aPos.y + uOffset.y, 0.0, 1.0);
}
"""

FRAGMENT_SHADER_SOURCE = """
#version 330 core
out vec4 FragColor;
void main() {
    FragColor = vec4(0.2, 0.6, 1.0, 1.0); // Light blue ball
}
"""

def compile_shader(shader_type, source):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader).decode('utf-8'))
    return shader

def init_resources():
    vs = compile_shader(GL_VERTEX_SHADER, VERTEX_SHADER_SOURCE)
    fs = compile_shader(GL_FRAGMENT_SHADER, FRAGMENT_SHADER_SOURCE)
    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)
    
    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(program).decode('utf-8'))
        
    glDeleteShader(vs)
    glDeleteShader(fs)

    vertices = [0.0, 0.0]
    num_segments = 100
    for i in range(num_segments + 1):
        theta = 2.0 * math.pi * i / num_segments
        vertices.append(ball_radius * math.cos(theta))
        vertices.append(ball_radius * math.sin(theta))
        
    vertices_array = (ctypes.c_float * len(vertices))(*vertices)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(vertices_array), vertices_array, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return program, vao, num_segments + 2

def init_window():
    if not glfw.init():
        return None
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(WIDTH, HEIGHT, "OpenGL Moving Ball Test", None, None)
    if not window:
        glfw.terminate()
        return None

    glfw.make_context_current(window)
    return window

def update_ball():
    global ball_x
    # Automatically move to the right
    ball_x += ball_speed
    
    # Calculate right boundary limit adjusting for aspect ratio
    aspect_ratio = HEIGHT / WIDTH
    right_boundary = 1.0 / aspect_ratio
    
    # If the ball passes the right screen boundary, reset it back to the far left
    if ball_x > right_boundary + ball_radius:
        ball_x = -right_boundary - ball_radius

def main():
    window = init_window()
    if not window:
        print("Failed to initialize window")
        return

    program, vao, vertex_count = init_resources()

    offset_loc = glGetUniformLocation(program, "uOffset")
    aspect_loc = glGetUniformLocation(program, "uAspect")

    glClearColor(0.1, 0.1, 0.1, 1.0)

    # Enable VSync to make the movement look smooth
    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        # Call the new movement logic
        update_ball()

        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(program)
        glUniform2f(offset_loc, ball_x, ball_y)
        glUniform1f(aspect_loc, HEIGHT / WIDTH)

        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, vertex_count)

        glfw.swap_buffers(window)

    glDeleteVertexArrays(1, [vao])
    glfw.terminate()

if __name__ == "__main__":
    main()
