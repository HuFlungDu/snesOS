import sys
import os
sys.path += ['.']
import time
from OpenGL.GL import *
from OpenGL.GL.shaders import *
from OpenGL.GLU import *
import string
import sf
from xml.etree import ElementTree as ET
import audiere
import traceback
import Image
import numpy
from freetype import *

letterkeys = {sf.Key.A:'a',
              sf.Key.B:'b',
              sf.Key.C:'c',
              sf.Key.D:'d',
              sf.Key.E:'e',
              sf.Key.F:'f',
              sf.Key.G:'g',
              sf.Key.H:'h',
              sf.Key.I:'i',
              sf.Key.J:'j',
              sf.Key.K:'k',
              sf.Key.L:'l',
              sf.Key.M:'m',
              sf.Key.N:'n',
              sf.Key.O:'o',
              sf.Key.P:'p',
              sf.Key.Q:'q',
              sf.Key.R:'r',
              sf.Key.S:'s',
              sf.Key.T:'t',
              sf.Key.U:'u',
              sf.Key.V:'v',
              sf.Key.W:'w',
              sf.Key.X:'x',
              sf.Key.Y:'y',
              sf.Key.Z:'z',
              }
specialkeys = {sf.Key.PERIOD:'.',
               sf.Key.COMMA:',',
               sf.Key.SLASH:'/',
               sf.Key.BACK_SLASH:'\\',
               sf.Key.NUM0:'0',
               sf.Key.NUM1:'1',
               sf.Key.NUM2:'2',
               sf.Key.NUM3:'3',
               sf.Key.NUM4:'4',
               sf.Key.NUM5:'5',
               sf.Key.NUM6:'6',
               sf.Key.NUM7:'7',
               sf.Key.NUM8:'8',
               sf.Key.NUM9:'9',
               sf.Key.SEMI_COLON:';',
               sf.Key.QUOTE:'\'',
               sf.Key.L_BRACKET:'[',
               sf.Key.R_BRACKET:']',
               sf.Key.EQUAL:'=',
               sf.Key.DASH:'-',
               sf.Key.TILDE:'`'}
spkeysupper =  {'.':'>',
                ',':'<',
                '/':'?',
                '\\':'|',
                '0':')',
                '1':'!',
                '2':'@',
                '3':'#',
                '4':'$',
                '5':'%',
                '6':'^',
                '7':'&',
                '8':'*',
                '9':'(',
                ';':':',
                '\'':'"',
                '[':'{',
                ']':'}',
                '=':'+',
                '-':'_',
                '`':'~'}
               

def TexFromPNG(filename):
    img = Image.open(filename)
    exec("mode = GL_%s" % img.mode) 
    img_data = numpy.array(list(img.getdata()), 'B')
    texture = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, mode, img.size[0], img.size[1], 0, mode, GL_UNSIGNED_BYTE, img_data)
    return texture
def MakeBuffer(target, data, size):
    TempBuffer = glGenBuffers(1)
    glBindBuffer(target, TempBuffer)
    glBufferData(target, size, data, GL_STATIC_DRAW)
    return TempBuffer
def ReadFile(filename):
    readfile = open(filename,'r')
    source = readfile.read()
    readfile.close()
    return source
def ReadBinaryFile(filename):
    readfile = open(filename,'rb')
    source = readfile.read()
    readfile.close()
    return source
def makewindow(parent,window):
    global snes
    priority = len(snes.DE.windows)
    snes.DE.windows.append(Window(snes.DE,window,priority))
    snes.DE.clearmenus()

class font:
    global snes
    def __init__(self,filename,size):
        try:
            tmpfile = open(filename,'r')
            tmpfile.close()
        except IOError:
            try:
                tmpfile = open("fonts/" + filename,'r')
                tmpfile.close()
                filename = "fonts/" + filename
            except IOError:
                if sys.platform == "win32":
                    windir = os.environ.get("WINDIR")
                    if windir:
                        filename = os.path.join(windir, "fonts", filename)
                elif sys.platform == "linux2":
                    filename = "/usr/share/fonts/TTF/" + filename
                else:
                    return None
                
        try:
            face = Face(filename)
            face.set_char_size( size*64 )
        except:
            print "Couldn't find specified font, defaulting to \"DejaVu Sans Mono\", 10 point"
            filename = "DejaVuSansMono.ttf"
            try:
                tmpfile = open("fonts/" + filename,'r')
                tmpfile.close()
                filename = "fonts/" + filename
            except IOError:
                if sys.platform == "win32":
                    windir = os.environ.get("WINDIR")
                    if windir:
                        filename = os.path.join(windir, "fonts", filename)
                elif sys.platform == "linux2":
                    filename = "/usr/share/fonts/TTF/" + filename
                else:
                    return None
            try:
                face = Face(filename)
                size = 12
                face.set_char_size( size*64 )
            except:
                return None
        width, height, ascender, descender = 0, 0, 0, 0
        for c in xrange(32,128):
            face.load_char( chr(c), FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT )
            bitmap    = face.glyph.bitmap
            width     = max( width, bitmap.width )
            ascender  = max( ascender, face.glyph.bitmap_top )
            descender = max( descender, bitmap.rows-face.glyph.bitmap_top )
        height = ascender+descender
        print height,width
        Z = numpy.zeros((height*6, width*16), dtype=numpy.ubyte)
        for j in xrange(6):
            for i in xrange(16):
                face.load_char(chr(32+j*16+i), FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT )
                bitmap = face.glyph.bitmap
                x = i*width  + face.glyph.bitmap_left
                y = j*height + ascender - face.glyph.bitmap_top
                Z[y:y+bitmap.rows,x:x+bitmap.width].flat = bitmap.buffer
        self.Tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
        glTexImage2D( GL_TEXTURE_2D, 0, GL_ALPHA, Z.shape[1], Z.shape[0], 0,
                         GL_ALPHA, GL_UNSIGNED_BYTE, Z )
        #print Z.shape[1],Z.shape[0]
        dx, dy = width/float(Z.shape[1]), height/float(Z.shape[0])
        self.w = (width)/512.0
        self.h = (height)/512.0
        #print self.w,self.h
        self.RelativeVertexData = {}
        for i in xrange(8*16):
            c = chr(i)
            x = i%16
            y = i//16-2
            if i >= 32:
                RelativeVertexData = numpy.array([(x)*dx,(y)*dy,
                                                (x+1)*dx,(y)*dy,
                                                (x)*dx,(y+1)*dy,
                                                (x+1)*dx,(y+1)*dy],
                                                numpy.float32)
                self.RelativeVertexData[c] = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)

        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                            GL_VERTEX_SHADER),
                                             compileShader(ReadFile("Shaders/fontf.glsl"),
                                             GL_FRAGMENT_SHADER))
        '''RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)'''
        MainVertexData = numpy.array([0,1,0,1,
                                      1,1,0,1,
                                      0,0,0,1,
                                      1,0,0,1,],
                                     numpy.float32)
        
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
    def drawglyph(self,char,x,y,w,h,red = 0, green = 0, blue = 0, alpha = 1):
        glEnable( GL_BLEND )
        glEnable( GL_DEPTH_TEST )
        glDepthFunc (GL_LEQUAL)
        glBlendEquation( GL_FUNC_ADD )
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        red = red/255.0
        green = green/255.0
        blue = blue/255.0
        glColor(red,green,blue,alpha)
        MainVertexData = numpy.array([x,y+h,0,1,
                                      x+w,y+h,0,1,
                                      x,y,0,1,
                                      x+w,y,0,1,],
                                     numpy.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.MainVertexData)
        glBufferSubData(GL_ARRAY_BUFFER, 0, len(MainVertexData)*4, MainVertexData)
        #print x,y,self.h,self.w
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1f(glGetUniformLocation(self.BaseProgram,"red"), red)
        glUniform1f(glGetUniformLocation(self.BaseProgram,"green"), green)
        glUniform1f(glGetUniformLocation(self.BaseProgram,"blue"), blue)
        glUniform1f(glGetUniformLocation(self.BaseProgram,"calpha"), alpha)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData[char])
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
 
class Window:
    global snes
    def __init__(self,parent,window,priority):
        if isinstance(window,str):
            self.window = ET.XML(window)
        else:
            self.window = window
        self.touchx = 0
        self.touchy = 0
        self.priority = priority
        self.items = []
        self.parent = parent
        self.name = self.window[0].text
        self.relw = float(self.window[1].text)
        self.relh = float(self.window[2].text)
        self.x = (-1+self.relw+1)*(parent.w/2)+(parent.x+1)-1
        self.y = (-1+self.relh+1)*(parent.h/2)+(parent.y+1)-1
        self.w = (self.x+self.relw+1)*(parent.w/2)+(parent.x+1)-1 - self.x
        self.h = (self.y+self.relh+1)*(parent.h/2)+(parent.y+1)-1 - self.y
        if len(self.window) >= 4:
            for i in self.window[3:]:
                if i.tag == "fileview":
                    self.fileview = makeitem(i.tag,[self,i])
                    self.items.append(self.fileview)
                else:
                    self.items.append(makeitem(i.tag,[self,i]))
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))

        self.Tex = snes.DE.windowtex
    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
        for i in self.items:
            i.draw()
    def clickaction(self,button,state,x,y):
        global snes
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            if state == 1:
                snes.DE.bumppriority(self)
            
            for i in self.items:
                i.clickaction(button,state,x,y)
            return True
        else:
            return False
    def updatevertex(self):
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*8)
        for i in self.items:
            i.updatevertex()

class textbox:
    global snes
    def __init__(self,parent,textbox):
        if isinstance(textbox,str):
            self.textbox = ET.XML(textbox)
        else:
            self.textbox = textbox
        self.startflash = 0
        self.start = 0
        self.cursorpos = 0
        self.parent = parent
        self.name = self.textbox[0].text
        exec("self.editable = " + self.textbox[1].text)
        self.text = self.textbox[2].text
        self.relx = float(self.textbox[3].text)
        self.rely = float(self.textbox[4].text)
        self.relw = float(self.textbox[5].text)
        self.relh = float(self.textbox[6].text)
        self.x = (self.relx+1)*(parent.w/2)+(parent.x+1)-1
        self.y = (self.rely+1)*(parent.h/2)+(parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(parent.w/2)+(parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(parent.h/2)+(parent.y+1)-1 - self.y
        font = snes.DE.font
        self.maxchars = self.start + int((self.w-font.w*2)/font.w)
        '''if len(self.windowborder) >= 5:
            for i in self.windowborder[4:]:
                self.items.append(makeitem(i.tag,[self,i]))'''
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        self.Tex = snes.DE.textboxtex
    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
        self.drawtext()
        if self.editable and snes.DE.activewidget == self:
            self.drawcursor()

    def drawtext(self):
        font = snes.DE.font
        for i in xrange(self.start,len(self.text)):
            if i - self.start > self.maxchars:
                break
            x = self.x + font.w + font.w*(i-self.start)
            y = self.y + self.h*.5 - font.h*.5
            width = font.w
            height = font.h
            font.drawglyph(self.text[i],x,y,width,height,0,0,0,1)
    def drawcursor(self):
        #print int(time.time()),int(time.time()) % 4
        if int(time.time()-self.startflash) % 2 == 0:
            font = snes.DE.font
            x = self.x + font.w + font.w*(self.cursorpos-self.start) - (font.w/2)
            y = self.y + self.h*.5 - font.h*.5
            width = font.w
            height = font.h
            font.drawglyph("|",x,y,width,height)
    def clickaction(self,button,state,x,y):
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            if self.editable:
                font = snes.DE.font
                if x > self.x + font.w + font.w*len(self.text) - font.w*self.start:
                    if state == 1:
                        self.cursorpos = len(self.text)
                elif x < self.x+font.w:
                    if state == 1:
                        self.cursorpos = self.start
                else:
                    if state == 1:
                        self.cursorpos = int(round(self.start + (x-self.x-font.w)/font.w))
                if state == 1:
                    self.startflash = time.time()
                    snes.DE.activewidget = self
            return True
        else:
            return False
    def updatevertex(self):
        self.x = (self.relx+1)*(self.parent.w/2)+(self.parent.x+1)-1
        self.y = (self.rely+1)*(self.parent.h/2)+(self.parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(self.parent.w/2)+(self.parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(self.parent.h/2)+(self.parent.y+1)-1 - self.y
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        font = snes.DE.font
        self.maxchars = self.start + int((self.w-font.w*2)/font.w)
    def handlekeypress(self,key,alt,control,shift,system):
        #print key
        if self.editable:
            if key == sf.Key.BACK and not (alt or control or shift or system):
                if self.cursorpos != 0:
                    self.text = self.text[:self.cursorpos-1]+self.text[self.cursorpos:]
                    self.cursorpos -= 1
            elif key == sf.Key.DELETE and not (alt or control or shift or system):
                self.text = self.text[:self.cursorpos]+self.text[self.cursorpos+1:]
            elif key == sf.Key.SPACE and not (alt or control or shift or system):
                self.text = self.text[:self.cursorpos]+" "+self.text[self.cursorpos:]
                self.cursorpos += 1
            elif key == sf.Key.LEFT and not (alt or control or shift or system):
                if self.cursorpos != 0:
                    self.cursorpos -= 1
            elif key == sf.Key.RIGHT and not (alt or control or shift or system):
                if self.cursorpos != len(self.text):
                    self.cursorpos += 1
            elif key in letterkeys:
                character = letterkeys[key]
                if shift and not (alt or control or system):
                    character = string.upper(character)
                self.text = self.text[:self.cursorpos]+character+self.text[self.cursorpos:]
                self.cursorpos += 1
            elif key in specialkeys:
                character = specialkeys[key]
                if shift and not (alt or control or system):
                    character = spkeysupper[character]
                self.text = self.text[:self.cursorpos]+character+self.text[self.cursorpos:]
                self.cursorpos += 1
            else:
                return
            self.startflash = time.time()
            font = snes.DE.font
            #self.start = 0
            
            #print self.start,(self.w-font.w*2),font.w
            if self.cursorpos - self.start > self.maxchars:
                self.start = self.cursorpos - self.maxchars
            elif self.cursorpos < self.start:
                self.start = self.cursorpos
            '''if self.x + font.w + font.w*len(self.text) > self.x+self.w:
                for j in xrange(len(i.text)):
                    if not (i.x + font.w + font.w*(len(i.text)-j) > i.x+i.w):
                        i.start = j
                        break'''
        pass

    def handlekeyrelease(self,key,alt,control,shift,system):
        pass
        
class folder:
    global snes
    def __init__(self,parent,name,relx,rely):
        self.clicktime = 0
        self.relx = relx
        self.rely = rely
        self.relw = .2
        self.relh = .2
        self.name = name
        self.parent = parent
        self.x = (self.relx+1)*(self.parent.w/2)+(self.parent.x+1)-1
        self.y = (self.rely+1+(self.parent.scroll*.3))*(self.parent.h/2)+(self.parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(self.parent.w/2)+(self.parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1+(self.parent.scroll*.3))*(self.parent.h/2)+(self.parent.y+1)-1 - self.y
        
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        self.Tex = snes.DE.foldertex
    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
    def updatevertex(self):
        self.x = (self.relx+1)*(self.parent.w/2)+(self.parent.x+1)-1
        self.y = (self.rely+1+(self.parent.scroll*.3))*(self.parent.h/2)+(self.parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(self.parent.w/2)+(self.parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1+(self.parent.scroll*.3))*(self.parent.h/2)+(self.parent.y+1)-1 - self.y
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*8)
    def clickaction(self,button,state,x,y):
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            if button == sf.Mouse.LEFT:
                if state == 1:
                    timedif = time.time() - self.clicktime
                    self.clicktime = time.time()
                    if timedif < 1.0:
                        self.parent.changedir(self.name)
                    return True
        return False

class afile:
    def __init__(self,parent,name,relx,rely):
        self.clicktime = 0
        self.relx = relx
        self.rely = rely
        self.relw = .2
        self.relh = .2
        self.name = name
        self.parent = parent
        self.x = (self.relx+1)*(self.parent.w/2)+(self.parent.x+1)-1
        self.y = (self.rely+1+(self.parent.scroll*.3))*(self.parent.h/2)+(self.parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(self.parent.w/2)+(self.parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1+(self.parent.scroll*.3))*(self.parent.h/2)+(self.parent.y+1)-1 - self.y

        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        extensions = (snes.DE.snesextensions + snes.DE.gbextensions +
                      snes.DE.bsxextensions + snes.DE.sufamiextensions)
        extension = self.name.split(".")
        self.extension = extension[len(extension)-1]
        if self.extension in snes.DE.snesextensions:
            self.Tex = snes.DE.snesfiletex
        elif self.extension in snes.DE.gbextensions:
            self.Tex = snes.DE.gbfiletex
        elif self.extension in snes.DE.bsxextensions:
            self.Tex = snes.DE.bsxfiletex
        elif self.extension in snes.DE.sufamiextensions:
            self.Tex = snes.DE.sufamifiletex
    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)

    def clickaction(self,button,state,x,y):
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            if button == sf.Mouse.LEFT:
                if state == 1:
                    timedif = time.time() - self.clicktime
                    self.clicktime = time.time()
                    if timedif < 1.0:
                        #print self.extension
                        if self.extension in snes.DE.snesextensions:
                            #print self.parent.dir + self.name
                            snes.initsnes("libPysnes")
                            snes.loadsnesgame(self.parent.dir + self.name)
                    return True
        return False
    def updatevertex(self):
        self.x = (self.relx+1)*(self.parent.w/2)+(self.parent.x+1)-1
        self.y = (self.rely+1+(self.parent.scroll*.3))*(self.parent.h/2)+(self.parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(self.parent.w/2)+(self.parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1+(self.parent.scroll*.3))*(self.parent.h/2)+(self.parent.y+1)-1 - self.y
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*8)
class fileview:
    global snes
    def __init__(self,parent,fileview):
        if isinstance(fileview,str):
            self.fileview = ET.XML(fileview)
        else:
            self.fileview = fileview
        self.dir = os.getcwd() + "/"
        newdir = ""
        for i in self.dir:
            if i == "\\":
                newdir += "/"
            else:
                newdir += i
        self.dir = newdir
        self.parent = parent
        for i in self.parent.items:
            if isinstance(i,textbox):
                if i.name == "addressbox":
                    i.text = self.dir
                    font = snes.DE.font
                    i.start = 0
                    if i.x + font.w + font.w*len(i.text) > i.x+i.w:
                        for j in xrange(len(i.text)):
                            if not (i.x + font.w + font.w*(len(i.text)-j) > i.x+i.w):
                                i.start = j
                                break
                    break
        path = self.dir.split("/")
        self.path = path[0:len(path)-1]
        self.directorylisting = os.listdir(self.dir)
        self.files = []
        self.dirs = []
        self.scroll = 0
        for files in self.directorylisting:
            if os.path.isdir(self.dir+"/"+files):
                self.dirs.append(files)
            else:
                self.files.append(files)
        self.files.sort()
        self.dirs.sort()
        self.dirobjs = []
        self.fileobjs = []
        #print self.filesrel
        self.history = []
        self.historypos = 0
        self.items = []
        self.relx = float(self.fileview[0].text)
        self.rely = float(self.fileview[1].text)
        self.relw = float(self.fileview[2].text)
        self.relh = float(self.fileview[3].text)
        self.x = (self.relx+1)*(parent.w/2)+(parent.x+1)-1
        self.y = (self.rely+1)*(parent.h/2)+(parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(parent.w/2)+(parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(parent.h/2)+(parent.y+1)-1 - self.y
        for i in xrange(len(self.dirs)):
            relx = -.8 + (i%4)*.2*2
            rely = .7 - (i/4)*.3
            self.dirobjs.append(folder(self,self.dirs[i],relx,rely))
        folders = i
        extensions = (snes.DE.snesextensions + snes.DE.gbextensions +
                                         snes.DE.bsxextensions + snes.DE.sufamiextensions)
        files = 0
        for i in xrange(folders, folders+len(self.files)):
            extension = self.files[i-folders].split(".")
            extension = extension[len(extension)-1]
            if extension in extensions:
                relx = -.8 + ((folders+files+1)%4)*.2*2
                rely = .7 - ((folders+files+1)/4)*.3
                self.fileobjs.append(afile(self,self.files[i-folders],relx,rely))
                files += 1
        self.maxscroll = (((len(self.dirobjs) + len(self.fileobjs))/4)+1-6)*.5
        if self.maxscroll < 0:
            self.maxscroll = 0
        self.activedirs = []
        self.activefiles = []
        for i in self.dirobjs:
            if not (i.rely + i.relh + self.scroll*.3 >= 1 or i.rely+self.scroll*.3 <= -1):
                self.activedirs.append(i)
        for i in self.fileobjs:
            if not (i.rely + i.relh + self.scroll*.3 >= 1 or i.rely+self.scroll*.3 <= -1):
                self.activefiles.append(i)
        #print self.activedirs
        
        '''if len(self.fileview) >= 5:
            for i in self.fileview[4:]:
                self.items.append(makeitem(i.tag,[self,i]))'''
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        self.Tex = snes.DE.fviewtex
    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
        for i in self.activedirs:
            i.draw()
        for i in self.activefiles:
            i.draw()
    def changedir(self,newdir):
        if newdir == "..":
            if self.path[0:-1] == [''] or self.path[0:-1] == []:
                return
            else:
                self.path = self.path[0:len(self.path)-1]
        else:
            self.path.append(newdir)
        self.history = self.history[0:self.historypos]
        self.history.append(self.dir)
        self.historypos += 1
        self.dir = ""
        for i in self.path:
            self.dir += i+"/"
        for i in self.parent.items:
            if isinstance(i,textbox):
                if i.name == "addressbox":
                    i.text = self.dir
                    font = snes.DE.font
                    i.start = 0
                    if i.x + font.w + font.w*len(i.text) > i.x+i.w:
                        for j in xrange(len(i.text)):
                            if not (i.x + font.w + font.w*(len(i.text)-j) > i.x+i.w):
                                i.start = j
                                break
                    break
        self.directorylisting = os.listdir(self.dir)
        self.files = []
        self.dirs = []
        self.scroll = 0
        for files in self.directorylisting:
            if os.path.isdir(self.dir+"/"+files):
                self.dirs.append(files)
            else:
                self.files.append(files)
        self.files.sort()
        self.dirs.sort()
        self.dirobjs = []
        self.fileobjs = []
        i = 0
        for i in xrange(len(self.dirs)):
            relx = -.8 + (i%4)*.2*2
            rely = .7 - (i/4)*.3
            self.dirobjs.append(folder(self,self.dirs[i],relx,rely))
        folders = i
        extensions = (snes.DE.snesextensions + snes.DE.gbextensions +
                                         snes.DE.bsxextensions + snes.DE.sufamiextensions)
        files = 0
        for i in xrange(folders, folders+len(self.files)):
            extension = self.files[i-folders].split(".")
            extension = extension[len(extension)-1]
            if extension in extensions:
                relx = -.8 + ((folders+files+1)%4)*.2*2
                rely = .7 - ((folders+files+1)/4)*.3
                self.fileobjs.append(afile(self,self.files[i-folders],relx,rely))
                files += 1
        self.maxscroll = ((len(self.dirobjs) + len(self.fileobjs))/4)+1-6
        if self.maxscroll < 0:
            self.maxscroll = 0
        self.activedirs = []
        self.activefiles = []
        for i in self.dirobjs:
            if not (i.rely + i.relh + self.scroll*.3 > 1 or i.rely+self.scroll*.3 < -1):
                self.activedirs.append(i)
        for i in self.fileobjs:
            if not (i.rely + i.relh + self.scroll*.3 > 1 or i.rely+self.scroll*.3 < -1):
                self.activefiles.append(i)
    def goback(self):
        if self.historypos != 0:
            self.historypos -= 1
            self.dir = self.history[self.historypos]
            for i in self.parent.items:
                if isinstance(i,textbox):
                    if i.name == "addressbox":
                        i.text = self.dir
                        font = snes.DE.font
                        i.start = 0
                        if i.x + font.w + font.w*len(i.text) > i.x+i.w:
                            for j in xrange(len(i.text)):
                                if not (i.x + font.w + font.w*(len(i.text)-j) > i.x+i.w):
                                    i.start = j
                                    break
                        break
            path = self.dir.split("/")
            self.path = path[0:len(path)-1]

            self.directorylisting = os.listdir(self.dir)
            self.files = []
            self.dirs = []
            self.scroll = 0
            for files in self.directorylisting:
                if os.path.isdir(self.dir+"/"+files):
                    self.dirs.append(files)
                else:
                    self.files.append(files)
            self.files.sort()
            self.dirs.sort()
            self.dirobjs = []
            self.fileobjs = []
            i = 0
            for i in xrange(len(self.dirs)):
                relx = -.8 + (i%4)*.2*2
                rely = .7 - (i/4)*.3
                self.dirobjs.append(folder(self,self.dirs[i],relx,rely))
            folders = i
            extensions = (snes.DE.snesextensions + snes.DE.gbextensions +
                                             snes.DE.bsxextensions + snes.DE.sufamiextensions)
            files = 0
            for i in xrange(folders, folders+len(self.files)):
                extension = self.files[i-folders].split(".")
                extension = extension[len(extension)-1]
                if extension in extensions:
                    relx = -.8 + ((folders+files+1)%4)*.2*2
                    rely = .7 - ((folders+files+1)/4)*.3
                    self.fileobjs.append(afile(self,self.files[i-folders],relx,rely))
                    files += 1
            self.maxscroll = ((len(self.dirobjs) + len(self.fileobjs))/4)+1-6
            if self.maxscroll < 0:
                self.maxscroll = 0
            self.activedirs = []
            self.activefiles = []
            for i in self.dirobjs:
                if not (i.rely + i.relh + self.scroll*.3 > 1 or i.rely+self.scroll*.3 < -1):
                    self.activedirs.append(i)
            for i in self.fileobjs:
                if not (i.rely + i.relh + self.scroll*.3 > 1 or i.rely+self.scroll*.3 < -1):
                    self.activefiles.append(i)
            
            
    
    def clickaction(self,button,state,x,y):
        global snes
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            if button == sf.Mouse.LEFT:
                if state == 1:
                    clicked = False
                    for i in self.activedirs:
                        clicked = clicked or i.clickaction(button,state,x,y)
                        if clicked:
                            break
                    if not clicked:
                        for i in self.activefiles:
                            clicked = clicked or i.clickaction(button,state,x,y)
                            if clicked:
                                break
                    return clicked
            elif button == 3:
                if state == 1:
                    self.scrollup()
                return True
            elif button == 4:
                if state == 1:
                    self.scrolldown()
        return False
    def scrollup(self):
        if self.scroll > 0:
            self.scroll -= 1
            self.activedirs = []
            self.activefiles = []
            for i in self.dirobjs:
                if not (i.rely + i.relh + self.scroll*.3 > 1 or i.rely+self.scroll*.3 < -1):
                    self.activedirs.append(i)
            for i in self.fileobjs:
                if not (i.rely + i.relh + self.scroll*.3 > 1 or i.rely+self.scroll*.3 < -1):
                    self.activefiles.append(i)
            for i in self.activedirs:
                i.updatevertex()
            for i in self.activefiles:
                i.updatevertex()
    def scrolldown(self):
        if self.scroll < self.maxscroll:
            self.scroll += 1
            self.activedirs = []
            self.activefiles = []
            for i in self.dirobjs:
                if not (i.rely + i.relh + self.scroll*.3 > 1 or i.rely+self.scroll*.3 < -1):
                    self.activedirs.append(i)
            for i in self.fileobjs:
                if not (i.rely + i.relh + self.scroll*.3 > 1 or i.rely+self.scroll*.3 < -1):
                    self.activefiles.append(i)
            for i in self.activedirs:
                i.updatevertex()
            for i in self.activefiles:
                i.updatevertex()
    def updatevertex(self):
        self.x = (self.relx+1)*(self.parent.w/2)+(self.parent.x+1)-1
        self.y = (self.rely+1)*(self.parent.h/2)+(self.parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(self.parent.w/2)+(self.parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(self.parent.h/2)+(self.parent.y+1)-1 - self.y
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*8)
        for i in self.activedirs:
            i.updatevertex()
        for i in self.activefiles:
            i.updatevertex()
class windowborder:
    global snes
    def __init__(self,parent,windowborder):
        if isinstance(windowborder,str):
            self.windowborder = ET.XML(windowborder)
        else:
            self.windowborder = windowborder
        self.dragging = False
        self.items = []
        self.parent = parent
        self.relx = float(self.windowborder[0].text)
        self.rely = float(self.windowborder[1].text)
        self.relw = float(self.windowborder[2].text)
        self.relh = float(self.windowborder[3].text)
        self.x = (self.relx+1)*(parent.w/2)+(parent.x+1)-1
        self.y = (self.rely+1)*(parent.h/2)+(parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(parent.w/2)+(parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(parent.h/2)+(parent.y+1)-1 - self.y
        if len(self.windowborder) >= 5:
            for i in self.windowborder[4:]:
                self.items.append(makeitem(i.tag,[self,i]))
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        self.Tex = snes.DE.wbordertex
    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
        for i in self.items:
            i.draw()
    def clickaction(self,button,state,x,y):
        global snes
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            if button == sf.Mouse.LEFT:
                if state == 1:
                    clicked = False
                    for i in self.items:
                        clicked = clicked or i.clickaction(button,state,x,y)
                    if not clicked:
                        self.dragging = True
                        snes.DE.activewindowmove = self.parent
                        self.parent.touchx = x - self.parent.x
                        self.parent.touchy = y - self.parent.y
                    return True
                elif state == 0:
                    if self.dragging:
                        self.dragging = False
                        snes.DE.activewindowmove = None
        else:
            return False

    def updatevertex(self):
        self.x = (self.relx+1)*(self.parent.w/2)+(self.parent.x+1)-1
        self.y = (self.rely+1)*(self.parent.h/2)+(self.parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(self.parent.w/2)+(self.parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(self.parent.h/2)+(self.parent.y+1)-1 - self.y
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*8)
        for i in self.items:
            i.updatevertex()
class ExitButton:
    global snes
    def __init__(self,parent,button):
        if isinstance(button,str):
            self.button = ET.XML(button)
        else:
            self.button = button
        self.parent = parent
        self.relx = float(self.button[0].text)
        self.rely = float(self.button[1].text)
        self.relw = float(self.button[2].text)
        self.relh = float(self.button[3].text)
        self.x = (self.relx+1)*(parent.w/2)+(parent.x+1)-1
        self.y = (self.rely+1)*(parent.h/2)+(parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(parent.w/2)+(parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(parent.h/2)+(parent.y+1)-1 - self.y
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        self.Tex = snes.DE.exittex
    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
    def clickaction(self,button,state,x,y):
        global snes
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            snes.DE.kill(self.parent.parent)
            #glutPostRedisplay()
            return True
    def updatevertex(self):
        self.x = (self.relx+1)*(self.parent.w/2)+(self.parent.x+1)-1
        self.y = (self.rely+1)*(self.parent.h/2)+(self.parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(self.parent.w/2)+(self.parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(self.parent.h/2)+(self.parent.y+1)-1 - self.y
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*8)

class Menu:
    global snes
    def __init__(self,parent,menu):
        if isinstance(menu,str):
            self.menutree = ET.XML(menu)
        else:
            self.menutree = menu
        self.items = []
        self.parent = parent
        self.relx = float(self.menutree[1].text)
        self.rely = float(self.menutree[2].text)
        self.relw = float(self.menutree[3].text)
        self.relh = float(self.menutree[4].text)
        self.x = (self.relx+1)*(parent.w/2)+(parent.x+1)-1
        self.y = (self.rely+1)*(parent.h/2)+(parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(parent.w/2)+(parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(parent.h/2)+(parent.y+1)-1 - self.y

        if len(self.menutree) >= 6:
            for i in self.menutree[5:]:
                self.items.append(makeitem(i.tag,[self,i]))
    def draw(self):
        for i in self.items:
            i.draw()
    def clickaction(self,button,state,x,y):
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            clicked = False
            for i in self.items:
                clicked = clicked or i.clickaction(button,state,x,y)
            return clicked
        else:
            return False
    def updatevertex(self):
        self.x = (self.relx+1)*(self.parent.w/2)+(self.parent.x+1)-1
        self.y = (self.rely+1)*(self.parent.h/2)+(self.parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(self.parent.w/2)+(self.parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(self.parent.h/2)+(self.parent.y+1)-1 - self.y
        for i in self.items:
            i.updatevertex()
class MenuItem:
    global snes
    def __init__(self,parent,item):
        if isinstance(item,str):
            self.item = ET.XML(item)
        else:
            self.item = item
        self.parent = parent
        self.name = self.item[0].text
        self.label = self.item[1].text
        self.relx = float(self.item[2].text)
        self.rely = float(self.item[3].text)
        self.relw = float(self.item[4].text)
        self.relh = float(self.item[5].text)
        self.action = self.item[6].text
        self.x = (self.relx+1)*(parent.w/2)+(parent.x+1)-1
        self.y = (self.rely+1)*(parent.h/2)+(parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(parent.w/2)+(parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(parent.h/2)+(parent.y+1)-1 - self.y
        self.items = []
        if len(self.item) >= 8:
            for i in self.item[7:]:
                self.items.append(makeitem(i.tag,[self,i]))
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        self.Tex = snes.DE.menuitemtex
        '''self.text = sf.Text(self.label, sf.Font.DEFAULT_FONT, 30)
        self.text.color = sf.Color.WHITE
        self.text.style = sf.Text.BOLD
        self.text.x = snes.window.width / 2.0 - self.text.rect.width / 2.0
        self.text.y = snes.window.height / 2.0 - self.text.rect.height / 2.0'''
    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
        #snes.DE.font.drawglyph(self.label[0],self.x,self.y,.05,.05)
        self.drawlabel()
        for i in self.items:
            i.draw()
        #snes.window.draw(self.text)
    def drawlabel(self):
        font = snes.DE.font
        for i in xrange(len(self.label)):
            x = self.x + font.w + font.w*i
            y = self.y + self.h*.5 - font.h*.5
            width = font.w
            height = font.h
            font.drawglyph(self.label[i],x,y,width,height,0,0,0,1)
    def clickaction(self,button,state,x,y):
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            exec(self.action)
            return True
        else:
            return False

    def makedropdown(self,button,state,x,y):
        if button == sf.Mouse.LEFT and state == 0:
            for i in self.items:
                if isinstance(i,DropdownMenu):
                    i.activate()
    def makegoback(self,button,state,x,y):
        if button == sf.Mouse.LEFT and state == 0:
            self.parent.parent.fileview.goback()
    def makegoup(self,button,state,x,y):
        if button == sf.Mouse.LEFT and state == 0:
            self.parent.parent.fileview.changedir("..")
    def donothing(self,button,state,x,y):
        if button == sf.Mouse.LEFT and state == 0:
            print "I don't do a thing"
    def updatevertex(self):
        self.x = (self.relx+1)*(self.parent.w/2)+(self.parent.x+1)-1
        self.y = (self.rely+1)*(self.parent.h/2)+(self.parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(self.parent.w/2)+(self.parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(self.parent.h/2)+(self.parent.y+1)-1 - self.y
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        #for i in self.items:
        #    i.updatevertex()
        
class DropdownMenu:
    global snes
    def __init__(self,parent,DMenu):
        self.active = False
        if isinstance(DMenu,str):
            self.DMenu = ET.XML(DMenu)
        else:
            self.DMenu = DMenu
        self.parent = parent
        #self.elementw = float(self.DMenu[0].text)
        self.elementh = float(self.DMenu[0].text)
        self.items = []
        itemnum = 1
        self.ysize = self.elementh*(len(self.DMenu[1:]))
        width = 0
        if len(self.DMenu) >= 2:
            for i in self.DMenu[1:]:
                if i.tag == "dmenuitem":
                    width = max(width,len(i.find("label").text))
        self.elementw = snes.DE.font.w*2 + snes.DE.font.w*width
        self.w = self.elementw
        self.h = self.ysize
        #print width
        if isinstance(parent,MenuItem):
            if parent.y - self.ysize < -1:
                self.y = parent.y + self.ysize + parent.h
            else:
                self.y = parent.y
            self.x = parent.x
        else:
            if parent.y - self.ysize < -1:
                self.y = parent.y + self.ysize
            else:
                self.y = parent.y + self.elementh
                
            if parent.x + self.elementw + parent.w> 1:
                self.x = parent.x - self.elementw 
            else:
                self.x = parent.x + parent.w
        if len(self.DMenu) >= 2:
            for i in self.DMenu[1:]:
                self.items.append(makeitem(i.tag,[self,i,itemnum]))
                itemnum += 1

    def draw(self):
        if self.active:
            for i in self.items:
                i.draw()
    def clickaction(self,button,state,x,y):
        clicked = False
        if self.active:
            for i in self.items:
                clicked = clicked or i.clickaction(button,state,x,y)
        return clicked
        
    def activate(self,top = True):
        global snes
        if not self.active:
            if top:
                snes.DE.setdropdownmenu(self)
            self.active = True
            #glutPostRedisplay()
        else:
            if top:
                snes.DE.clearmenus()
            else:
                self.deactivate()
    def deactivate(self, top = True):
        self.active = False
        for i in self.items:
            for j in i.items:
                if isinstance(j,DropdownMenu):
                    j.deactivate(False)
        '''if top:
            glutPostRedisplay()'''
        
class DropdownMenuItem:
    global snes
    def __init__(self,parent,DMenuitem,itemnum):
        if isinstance(DMenuitem,str):
            self.DMenuitem = ET.XML(DMenuitem)
        else:
            self.DMenuitem = DMenuitem
        self.name = self.DMenuitem[0].text
        self.label = self.DMenuitem[1].text
        self.action = self.DMenuitem[2].text
        self.itemnum = itemnum
        self.parent = parent
        self.x = parent.x
        self.y = parent.y - parent.elementh*itemnum
        self.w = parent.elementw
        self.h = parent.elementh
        self.items = []
        if len(self.DMenuitem) >= 4:
            for i in self.DMenuitem[3:]:
                self.items.append(makeitem(i.tag,[self,i]))
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        self.Tex = snes.DE.dmenuitemtex
    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
        self.drawlabel()
        for i in self.items:
            i.draw()
            
    def drawlabel(self):
        font = snes.DE.font
        for i in xrange(len(self.label)):
            x = self.x + font.w + font.w*i
            y = self.y + self.h*.5 - font.h*.5
            width = font.w
            height = font.h
            font.drawglyph(self.label[i],x,y,width,height)   
    def clickaction(self,button,state,x,y):
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            exec(self.action)
            return True
        else:
            clicked = False
            for i in self.items:
                clicked = clicked or i.clickaction(button,state,x,y)
            return clicked
    def makedropdown(self,button,state,x,y):
        if button == sf.Mouse.LEFT and state == 0:
            for i in self.parent.items:
                for j in i.items:
                    if isinstance(j,DropdownMenu):
                        j.deactivate(False)
            for i in self.items:
                if isinstance(i,DropdownMenu):
                    if not i.active:
                        i.activate(False)
                    else:
                        i.deactivate(False)

class Taskbar:
    global snes
    def __init__(self,parent,bar):
        self.priority = 5
        if isinstance(bar,str):
            self.bar = ET.XML(item)
        else:
            self.bar = bar
        self.parent = parent
        self.name = self.bar[0].text
        self.relx = float(self.bar[1].text)
        self.rely = float(self.bar[2].text)
        self.relw = float(self.bar[3].text)
        self.relh = float(self.bar[4].text)
        self.x = (self.relx+1)*(parent.w/2)+(parent.x+1)-1
        self.y = (self.rely+1)*(parent.h/2)+(parent.y+1)-1
        self.w = (self.relx+self.relw+1)*(parent.w/2)+(parent.x+1)-1 - self.x
        self.h = (self.rely+self.relh+1)*(parent.h/2)+(parent.y+1)-1 - self.y
        self.items = []
        if len(self.bar) >= 6:
            for i in self.bar[5:]:
                self.items.append(makeitem(i.tag,[self,i]))
        self.priority = 1
        MainVertexData = numpy.array([self.x,self.y+self.h,0,1,
                                      self.x+self.w,self.y+self.h,0,1,
                                      self.x,self.y,0,1,
                                      self.x+self.w,self.y,0,1,],
                                     numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        self.Tex = snes.DE.taskbartex
    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
        for i in self.items:
            i.draw()
    def clickaction(self,button,state,x,y):
        if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
            self.items.sort(cmp = lambda x,y: cmp(x.priority,y.priority))
            clicked = False
            for i in self.items:
                clicked = clicked or i.clickaction(button,state,x,y)
            return clicked
        else:
            return False
        
class Desktop:
    def __init__(self,user = "nouser"):
        self.user = user
        conf = ET.XML(ReadFile("conf/"+user+"conf.xml"))
        theme = conf.find("theme")
        self.theme = theme.text
        self.desktop = ET.XML(ReadFile("Themes/"+self.theme+"/desktop.xml"))
        extensions = conf.find("extensions")
        self.snesextensions = []
        self.gbextensions = []
        self.bsxextensions = []
        self.sufamiextensions = []
        for i in extensions:
            tag = i.tag
            if tag == "snes":
                self.snesextensions.append(i.text)
            elif tag == "gb":
                self.gbextensions.append(i.text)
            elif tag == "bsx":
                self.bsxextensions.append(i.text)
            elif tag == "sufami":
                self.sufamiextensions.append(i.text)
            
    def make(self):
        tmptime = time.time()
        #self.renderloadingmessage("Loading window textures...")
        self.windowtex = TexFromPNG("Themes/"+self.theme+"/windowtexture.png")
        self.fviewtex = TexFromPNG("Themes/"+self.theme+"/fileview.png")
        #self.renderloadingmessage("Loading folder texture...")
        self.foldertex = TexFromPNG("Themes/"+self.theme+"/folder.png")
        #self.renderloadingmessage("Loading fileview texture...")
        #self.renderloadingmessage("Loading window border texture...")
        self.wbordertex = TexFromPNG("Themes/"+self.theme+"/windowborder.png")
        #self.renderloadingmessage("Loading button textures...")
        self.exittex = TexFromPNG("Themes/"+self.theme+"/exit.png")
        #self.renderloadingmessage("Loading menu textures...")
        self.menuitemtex = TexFromPNG("Themes/"+self.theme+"/MenuItem.png")
        self.dmenuitemtex = TexFromPNG("Themes/"+self.theme+"/dmenuitem.png")
        #self.renderloadingmessage("Loading taskbar texture...")
        self.taskbartex = TexFromPNG("Themes/"+self.theme+"/bar.png")
        self.textboxtex = TexFromPNG("Themes/"+self.theme+"/textbox.png")
        #self.renderloadingmessage("Loading file textures...")
        self.snesfiletex = TexFromPNG("Themes/"+self.theme+"/snes.png")
        self.gbfiletex = TexFromPNG("Themes/"+self.theme+"/gb.png")
        self.bsxfiletex = TexFromPNG("Themes/"+self.theme+"/bsx.png")
        self.sufamifiletex = TexFromPNG("Themes/"+self.theme+"/sufami.png")
        print time.time() - tmptime
        
        conf = ET.XML(ReadFile("conf/"+self.user+"conf.xml"))
        fontname = conf.find("font").find("filename").text
        fontsize = int(conf.find("font").find("size").text)
        self.font = font(fontname,fontsize)
        
        self.relx,self.x = float(self.desktop[1].text),float(self.desktop[1].text)
        self.rely,self.y = float(self.desktop[2].text),float(self.desktop[2].text)
        self.relw,self.w = float(self.desktop[3].text),float(self.desktop[3].text)
        self.relh,self.h = float(self.desktop[4].text),float(self.desktop[4].text)
        MainVertexData = numpy.array([-1,1,0,1,1,1,0,1,-1,-1,0,1,1,-1,0,1],numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        self.Tex = TexFromPNG("Themes/"+self.theme+"/desktop.png")
        self.items = []
        if len(self.desktop) >= 6:
            for i in self.desktop[5:]:
                self.items.append(makeitem(i.tag,[self,i]))
        self.activedmenu = None
        self.activewindowmove = None
        self.activewidget = None
        self.windows = []
    def renderloadingmessage(self,intext):
        snes.window.clear(sf.Color.BLACK)
        self.text = sf.Text(intext, sf.Font.DEFAULT_FONT, 30)
        self.text.color = sf.Color.WHITE
        self.text.style = sf.Text.BOLD
        self.text.x = snes.window.width / 2.0 - self.text.rect.width / 2.0
        self.text.y = snes.window.height / 2.0 - self.text.rect.height / 2.0
        snes.window.draw(self.text)
        snes.window.display()
    def changeuser(self,user = "nouser"):
        self.user = user
        conf = ET.XML(ReadFile("conf/"+user+"conf.xml"))
        theme = conf.find("theme")
        self.theme = theme.text
        self.desktop = ET.XML(ReadFile("Themes/"+self.theme+"/desktop.xml"))
        extensions = conf.find("extensions")
        self.snesextensions = []
        self.gbextensions = []
        self.bsxextensions = []
        self.sufamiextensions = []
        for i in extensions:
            tag = i.tag
            if tag == "snes":
                self.snesextensions.append(i.text)
            elif tag == "gb":
                self.gbextensions.append(i.text)
            elif tag == "bsx":
                self.bsxextensions.append(i.text)
            elif tag == "sufami":
                self.sufamiextensions.append(i.text)
        self.windowtex = TexFromPNG("Themes/"+self.theme+"/windowtexture.png")
        self.foldertex = TexFromPNG("Themes/"+self.theme+"/folder.png")
        self.fviewtex = TexFromPNG("Themes/"+self.theme+"/fileview.png")
        self.wbordertex = TexFromPNG("Themes/"+self.theme+"/windowborder.png")
        self.exittex = TexFromPNG("Themes/"+self.theme+"/exit.png")
        self.menuitemtex = TexFromPNG("Themes/"+self.theme+"/MenuItem.png")
        self.dmenuitemtex = TexFromPNG("Themes/"+self.theme+"/dmenuitem.png")
        self.taskbartex = TexFromPNG("Themes/"+self.theme+"/bar.png")
        self.textboxtex = TexFromPNG("Themes/"+self.theme+"/textbox.png")
        self.snesfiletex = TexFromPNG("Themes/"+self.theme+"/snes.png")
        self.gbfiletex = TexFromPNG("Themes/"+self.theme+"/gb.png")
        self.bsxfiletex = TexFromPNG("Themes/"+self.theme+"/bsx.png")
        self.sufamifiletex = TexFromPNG("Themes/"+self.theme+"/sufami.png")
        
        fontname = conf.find("font").find("filename").text
        self.font = font(fontname,64)
        
        self.relx,self.x = float(self.desktop[1].text),float(self.desktop[1].text)
        self.rely,self.y = float(self.desktop[2].text),float(self.desktop[2].text)
        self.relw,self.w = float(self.desktop[3].text),float(self.desktop[3].text)
        self.relh,self.h = float(self.desktop[4].text),float(self.desktop[4].text)

        self.Tex = TexFromPNG("Themes/"+self.theme+"/desktop.png")
        self.items = []
        if len(self.desktop) >= 6:
            for i in self.desktop[5:]:
                self.items.append(makeitem(i.tag,[self,i]))

    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)


        
        self.windows.sort(cmp = lambda x,y: cmp(x.priority,y.priority))
        for i in self.windows:
            i.draw()
        for i in self.items:
            i.draw()
    def bumppriority(self,window):
        for i in self.windows:
            if i.priority > window.priority:
                i.priority -= 1
        window.priority = len(self.windows)
    def movewindow(self,x,y):
        av = self.activewindowmove
        av.x = x-av.touchx
        av.y = y-av.touchy
        av.updatevertex()

    def clickaction(self,button,state,x,y):
        if self.activedmenu is not None:
            if state == 0:
                keepmenus = self.activedmenu.clickaction(button,state,x,y)
                if not keepmenus:
                    self.clearmenus()
        else:  
            if x >= self.x and x <= self.x+self.w and y >= self.y and y <= self.y + self.h:
                self.items.sort(cmp = lambda x,y: cmp(y.priority,x.priority))
                self.windows.sort(cmp = lambda x,y: cmp(y.priority,x.priority))
                mix = self.items + self.windows
                for i in mix:
                    clicked = i.clickaction(button,state,x,y)
                    if clicked:
                        break

    def setdropdownmenu(self,dmenu):
        self.clearmenus()
        self.activedmenu = dmenu
    def clearmenus(self):
        if self.activedmenu is not None:
            self.activedmenu.deactivate()
        self.activedmenu = None
    def kill(self,obj):
        for i in self.items:
            if obj == i:
                self.items.remove(obj)
                break
        for i in self.windows:
            if obj == i:
                self.windows.remove(obj)
                break
    def handlekeypress(self,key,alt,control,shift,system):
        if self.activewidget is not None:
            self.activewidget.handlekeypress(key,alt,control,shift,system)
    def handlekeyrelease(self,key,alt,control,shift,system):
        if self.activewidget is not None:
            self.activewidget.handlekeyrelease(key,alt,control,shift,system)
    def motion(self,x,y):
        if self.activewindowmove is not None:
            self.movewindow(x,y)
class xsnes:
    global snes
    def __init__(self,core):
        #print dir(sf)
        for i in audiere.get_devices():
            try:
                self.audiodevice = audiere.open_device(i)
                break
            except:
                pass
        self.leftaudio = numpy.zeros(500,dtype=numpy.float32)
        self.rightaudio = numpy.zeros(500,dtype=numpy.float32)
        self.streampos = 0
        self.samplerate = 1
        self.leftoutstream = self.audiodevice.open_array(self.leftaudio, self.samplerate)
        self.rightoutstream = self.audiodevice.open_array(self.rightaudio, self.samplerate)
        self.leftoutstream.repeating = 1
        self.rightoutstream.repeating = 1
        self.ports = ["port1","port2"]
        self.devices = [[None],["gamepad"],["multitapp1","multitapp2","multitapp3", "multitapp4"],
                        ["mouse"],["superscope"],
                        ["justifier1"],["justifier1","justifier2"]]
        self.controllist = [
                            [[],                        #Port1, Empty
                            ["B","Y","select","start","up","down","left","right",
                                "A","X","L","R"],       #Port1, game pad
                            ["B","Y","select","start","up","down","left","right",
                                "A","X","L","R"],       #Port1, Multitap
                            ["xaxis","yaxis","leftbutton",
                                "rightbutton"],         #Port1, Mouse
                            ],                          #Port1
                            [[],                        #Port2, Empty
                            ["B","Y","select","start","up","down","left","right",
                              "A","X","L","R"],         #Port2, game pad
                             ["B","Y","select","start","up","down","left","right",
                              "A","X","L","R"],         #Port2, Multitap
                             ["xaxis","yaxis","leftbutton",
                              "rightbutton"],           #Port2, Mouse
                             ["xaxis","yaxis","trigger",
                              "cursor","turbo"],         #Port2, Super Scope
                             ["xaxis","yaxis",
                              "trigger","start"],        #Port2, Justifier
                             ["xaxis","yaxis",
                              "trigger","start"]        #Port2, Justifiers
                             ]                          #Port2
                            ]                           #Controllist
        self.running = True
        exec("from cores import " + core + " as libPysnes")
        self.libPysnes = libPysnes
        self.libPysnes.Pysnes_set_video_refresh(self.refresh_video)
        self.libPysnes.Pysnes_set_audio_sample(self.audio_sample)
        self.libPysnes.Pysnes_set_input_poll(self.input_poll)
        self.libPysnes.Pysnes_set_input_state(self.input_state)
        self.libPysnes.Pysnes_init()
        self.Desktop = False
        self.Emulator = True
        self.Tex = glGenTextures(1)
        MainVertexData = numpy.array([-1,1,0,1,7,1,0,1,-1,-1,0,1,7,-1,0,1],numpy.float32)
        RelativeVertexData = numpy.array([0,0,1,0,0,1,1,1],
                                     numpy.float32)
        FullWindowVertices = numpy.array([0,1,2,3],numpy.ushort)
        self.MainVertexData = MakeBuffer(GL_ARRAY_BUFFER,MainVertexData,len(MainVertexData)*4)
        self.RelativeVertexData = MakeBuffer(GL_ARRAY_BUFFER,RelativeVertexData,len(RelativeVertexData)*4)
        self.FullWindowVertices = MakeBuffer(GL_ELEMENT_ARRAY_BUFFER,FullWindowVertices,len(FullWindowVertices)*2)
        self.BaseProgram = compileProgram(compileShader(ReadFile("Shaders/Mainv.glsl"),
                                         GL_VERTEX_SHADER),
                                         compileShader(ReadFile("Shaders/Mainf.glsl"),
                                         GL_FRAGMENT_SHADER))
        
        conf = ET.XML(ReadFile("conf/"+snes.DE.user+"conf.xml"))
        controls = conf.find("controls")
        self.populatecontrols(controls)
        self.keyspressed = []
        
    def loadsnesgame(self,gamepath, XML = ""):
        self.romname = gamepath
        self.game = ReadBinaryFile(self.romname)
        if len(self.game)%0x8000:
            self.game = self.game[0x200:]
        self.libPysnes.Pysnes_unload_cartridge()
        self.libPysnes.Pysnes_load_cartridge_normal(XML,self.game,len(self.game))

    def draw(self):
        glUseProgram(self.BaseProgram)
        pos = glGetAttribLocation(self.BaseProgram, "position")
        rpos = glGetAttribLocation(self.BaseProgram, "relativeposition")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.Tex)
        glUniform1i(glGetUniformLocation(self.BaseProgram,"texture"), 0)
        
        glBindBuffer(GL_ARRAY_BUFFER,self.MainVertexData)
        glVertexAttribPointer(pos,
                              4,
                              GL_FLOAT,
                              GL_FALSE,
                              16,
                              None)
        glBindBuffer(GL_ARRAY_BUFFER,self.RelativeVertexData)
        glVertexAttribPointer(rpos,
                              2,
                              GL_FLOAT,
                              GL_FALSE,
                              8,
                              None)
        glEnableVertexAttribArray(pos)
        glEnableVertexAttribArray(rpos)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.FullWindowVertices)
        glDrawElements(GL_TRIANGLE_STRIP,
                       4,
                       GL_UNSIGNED_SHORT,
                       None)
        glDisableVertexAttribArray(pos)
        glDisableVertexAttribArray(rpos)
    def run(self):
        if self.running:
            self.libPysnes.Pysnes_run()
        
    def refresh_video(self,data,width,height):
        
        interlace = (height == 448 or height == 478)
        pitch = 512 if interlace else 1024
        overscan = (height == 239 or height == 478)

        glBindTexture(GL_TEXTURE_2D,self.Tex)
        snespicbuffer = data.returnnumpyarray()

        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, pitch, height, 0, GL_BGRA,
                     GL_UNSIGNED_SHORT_1_5_5_5_REV, snespicbuffer)

    def audio_sample(self,left, right):
        self.leftaudio[self.streampos] = left
        self.rightaudio[self.streampos] = right
        self.streampos += 1
        if not (self.rightoutstream.playing and self.leftoutstream.playing):
            self.rightoutstream.play()
            self.leftoutstream.play()
        if self.streampos >= 500:
            self.streampos = 0

    def input_poll(self):
        return
    def input_state(self, port, device, index, identity):
        try:
            buttoncheck = self.controls[self.ports[port]][self.devices[device][index]][self.controllist[port][device][identity]]
            exec("buttons = " + str(buttoncheck))
            if buttons in self.keyspressed:
                return 1
            else:
                return 0
        except:
            return 0
    def populatecontrols(self,controls):
        self.controls = {}
        for port in controls:
            tmpport = {}
            for controller in port:
                tmpcontroller = {}
                for button in controller:
                    tmpcontroller[button.tag] = button.text
                tmpport[controller.tag] = tmpcontroller
            self.controls[port.tag] = tmpport
    def handlekeypress(self,key,alt,control,shift,system):
        if key == sf.Key.ESCAPE:
            self.running = not self.running
        else:
            rem = None
            for i in self.keyspressed:
                if i[0] == key:
                    rem = i
                    break
            if rem:
                self.keyspressed.remove(rem)
                self.keyspressed = list(set(self.keyspressed))
            self.keyspressed.append((key,alt,control,shift,system))
            self.keyspressed = list(set(self.keyspressed))
    def handlekeyrelease(self,key,alt,control,shift,system):
        if key == sf.Key.ESCAPE:
            pass
        else:
            try:
                rem = None
                for i in self.keyspressed:
                    if i[0] == key:
                        rem = i
                        break
                if rem:
                    self.keyspressed.remove(rem)
                    self.keyspressed = list(set(self.keyspressed))
            except:
                pass
    def motion(self,x,y):
        pass
    def clickaction(self,button,state,x,y):
        pass
        
        
class GLSnes:
    def __init__(self):
        self.xsnes = None
        self.Desktop = True
        self.Emulator = False
        self.FrameWidth = 0
        self.FrameHeight = 0
        self.TexWidth = 0
        self.TexHeight = 0
        self.frames = 0
        self.tempframes = 0
        self.height = 0
        self.width = 0
        self.P1Controller = 1
        self.P2Controller = 0
        self.romstring = ""
        self.Power = False
        self.ROMName = None
        self.ROMBaseName = None
        self.buttonsdown = []
        self.Controls = {}
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendEquation( GL_FUNC_ADD )
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)


        
    def run(self):
        self.DE = Desktop()
        self.window = sf.RenderWindow(sf.VideoMode(640, 480), 'snesOS')
        self.window.clear(sf.Color.BLACK)
        self.window.display()
        self.height = 480
        self.width = 640
        self.window.framerate_limit = 60
        self.DE.make()
        self.mousebuttonsdown = [False,False,False]
        self.execute = True
        frames = 0
        tmpframes = 0
        oldtime = int(time.time())
        while self.execute:
            try:
                for event in self.window.iter_events():
                    if event.type == sf.Event.CLOSED:
                        self.window.close()
                        self.execute = False
                    elif event.type == sf.Event.RESIZED:
                        self.reshape(event.width, event.height)
                    elif event.type == sf.Event.MOUSE_BUTTON_PRESSED:
                        self.mousebuttonsdown[event.button] = True
                        self.click(event.button,1,event.x,event.y)
                    elif event.type == sf.Event.MOUSE_BUTTON_RELEASED:
                        self.mousebuttonsdown[event.button] = False
                        self.click(event.button,0,event.x,event.y)
                    elif event.type == sf.Event.MOUSE_MOVED:
                        if True in self.mousebuttonsdown:
                            self.motion(event.x,event.y)
                        else:
                            self.pmotion(event.x,event.y)
                    elif event.type == sf.Event.MOUSE_WHEEL_MOVED:
                        if event.delta == -1:
                            self.click(4,0,event.x,event.y)
                            self.click(4,1,event.x,event.y)
                        else:
                            self.click(3,0,event.x,event.y)
                            self.click(3,1,event.x,event.y)
                    elif event.type == sf.Event.KEY_PRESSED:
                        self.keypress(event.code,event.alt,event.control,event.shift,event.system)
                    elif event.type == sf.Event.KEY_RELEASED:
                        self.keyrelease(event.code,event.alt,event.control,event.shift,event.system)
                    elif event.type == sf.Event.TEXT_ENTERED:
                        print event
                if self.execute:
                    frames += 1
                    if self.Emulator:
                        if self.xsnes:
                            frames += 1
                            tmpframes += 1
                            if int(time.time()) != oldtime:
                                tmpframes = 0
                            oldtime = int(time.time())
                            self.xsnes.run()

                    self.draw()
                    self.window.display()
                
            except Exception, ex1:
                traceback.print_exc()
                continue

    def loadsnesgame(self,gamepath):
        if self.xsnes:
            self.xsnes.loadsnesgame(gamepath)
    
    def initsnes(self,core):
        self.Desktop = False
        self.Emulator = True
        self.xsnes = xsnes(core)
        
    def click(self,button,state,x,y):
        if self.Desktop:
            self.DE.clickaction(button,state,float(x)/self.width*2-1,-(float(y)/self.height*2-1))
        elif self.Emulator:
            if self.xsnes:
                self.xsnes.clickaction(button,state,float(x)/self.width*2-1,-(float(y)/self.height*2-1))
    def motion(self,x,y):
        self.mousex = float(x)/self.width*2-1
        self.mousey = -(float(y)/self.height*2-1)
        if self.Emulator:
            if self.xsnes:
                self.xsnes.motion(self.mousex,self.mousey)
        elif self.Desktop:
            self.DE.motion(self.mousex,self.mousey)
    def pmotion(self,x,y):
        self.mousex = float(x)/self.width*2-1
        self.mousey = -(float(y)/self.height*2-1)
    def reshape(self, width, height):
        self.width = width
        self.height = height

    def draw(self):
        glViewport(0, 0, self.width, self.height)
        glClearDepth(1)
        glClearColor(0,0,0,0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glEnable(GL_TEXTURE_2D)
        if self.Desktop:
            self.DE.draw()
            
        elif self.Emulator:
            if self.xsnes:
                self.xsnes.draw()
        glDisable(GL_TEXTURE_2D)
        
    def keypress(self,key,alt,control,shift,system):
        if self.Emulator:
            if self.xsnes:
                self.xsnes.handlekeypress(key,alt,control,shift,system)
        elif self.Desktop:
            self.DE.handlekeypress(key,alt,control,shift,system)

    def keyrelease(self,key,alt,control,shift,system):
        if self.Emulator:
            if self.xsnes:
                self.xsnes.handlekeyrelease(key,alt,control,shift,system)
        elif self.Desktop:
            self.DE.handlekeyrelease(key,alt,control,shift,system)

global items
items = {"desktop" : Desktop,
         "taskbar" : Taskbar,
         "menu" : Menu,
         "menuitem" : MenuItem,
         "dropdownmenu" :DropdownMenu,
         "dmenuitem" : DropdownMenuItem,
         "windowborder" : windowborder,
         "exitbutton" : ExitButton,
         "fileview" : fileview,
         "textbox" : textbox}
def makeitem(itemname,args):
    global items
    return items[itemname](*args)
global snes
#glutInit(sys.argv)
snes = GLSnes()
snes.run()
