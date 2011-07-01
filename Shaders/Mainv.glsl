#version 110

attribute vec4 position;

attribute vec2 relativeposition;

varying vec2 texcoord;

void main()
{
    gl_Position = position;
    
    texcoord = relativeposition;
}
