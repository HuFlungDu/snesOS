#version 110

uniform sampler2D texture;
uniform float red;
uniform float green;
uniform float blue;
uniform float calpha;
varying vec2 texcoord;

void main()
{
    vec4 alpha = texture2D(texture, texcoord).aaaa;
    gl_FragColor = alpha*vec4(red,green,blue,calpha);
}
