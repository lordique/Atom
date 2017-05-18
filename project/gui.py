
# common import
import sys
sys.path.append('..')

from common.core import *
from common.gfxutil import *
from common.leaputil import *
from common.audio import *
from common.mixer import *

from audio import *
from visual import *

import numpy as np

#Listens for gestures on a sound effect. Is responsible for updating the
#sound effect's audio and visual based on the gestures.
class GestureListener(object):
    def __init__(self, orb, sound):
        super(GestureListener, self).__init__()
        self.angle = None
        self.r = None
        self.orb = orb
        self.grab_thresh = 20
        self.grabbed = False
        self.sound = sound
        self.on_orbital = False
        self.changed = False

    #monitors the hand position, fires events if necessary
    def set_hand_pos(self, pos):
        
        #initiate a grab if within reach of the hand and grabbing
        if not self.grabbed and abs(pos[0]-self.orb.get_pos()[0]-self.orb.get_size()/2.)<self.grab_thresh and abs(pos[1]-self.orb.get_pos()[1]-self.orb.get_size()/2.)<self.grab_thresh:
            self.grabbed = True
            self.changed = False
            self.sound.loop()

        #update the position of the orb if grabbed
        if self.grabbed:
            self.orb.set_pos(pos)
            self.sound.set_vol(pos[2])
            dist = ((pos[0]-Window.width/2.)**2+(pos[1]-Window.height/2.)**2)**.5
            
            #snap to an orbital
            if (dist%50<=3 or dist%50<=47) and not dist<50 and not dist>204:
                self.r = np.round(dist/50)*50
                self.orb.set_pos([Window.width/2.+self.r*(pos[0]-Window.width/2.)/dist,Window.height/2.+self.r*(pos[1]-Window.height/2.)/dist])
                self.on_orbital = True
            else:
                self.on_orbital = False
                self.orb.remove_from_orbital()
        return self.grabbed

    # called when the hand releases 
    def release(self):
        self.grabbed = False
        self.sound.stop()

    # updates every frame 
    def on_update(self, playing):
        if not self.grabbed and self.on_orbital:
 			#snap to an orbital
            if not self.changed:
                self.orb.set_on_orbital(self.r)
                self.changed = True
            #plays a sound if the sound effect hits the now bar
            if playing and self.orb.on_update(self.r):
                self.sound.play()
    
    def set_orb(self):
    	if self.on_orbital:
    		self.orb.set_on_orbital(self.r)


# Soundbank contains all the sound effects; their visual representations, called orbs, and their audio, called Sfx
class SoundBank(InstructionGroup):
    def __init__(self,widget,mixer):
        super(SoundBank, self).__init__()

        self.sound_orbs = [GestureListener(Orb(7,widget.canvas,50,110), Sfx(WaveGenerator(WaveFile("../data/snare.wav")),mixer)),
        GestureListener(Orb(7,widget.canvas,100,110), Sfx(WaveGenerator(WaveFile("../data/snare.wav")),mixer)),
        GestureListener(Orb(3,widget.canvas,50,50), Sfx(WaveGenerator(make_wave_buffers('../data/dont.txt','../data/dont.wav')['j'],True),mixer)),
        GestureListener(Orb(3,widget.canvas,100,50), Sfx(WaveGenerator(make_wave_buffers('../data/dont.txt','../data/dont.wav')['j'],True),mixer)),
        GestureListener(Orb(3,widget.canvas,150,50), Sfx(WaveGenerator(make_wave_buffers('../data/dont.txt','../data/dont.wav')['j'],True),mixer)),
        GestureListener(Orb(5,widget.canvas,50,230), Sfx(WaveGenerator(WaveFile("../data/kick.wav")),mixer)),
        GestureListener(Orb(5,widget.canvas,100,230), Sfx(WaveGenerator(WaveFile("../data/kick.wav")),mixer)),
        GestureListener(Orb(5,widget.canvas,150,230), Sfx(WaveGenerator(WaveFile("../data/kick.wav")),mixer)),
        GestureListener(Orb(2,widget.canvas,50,350), Sfx(WaveGenerator(WaveFile("../data/D.wav")),mixer)),
        GestureListener(Orb(2,widget.canvas,100,350), Sfx(WaveGenerator(WaveFile("../data/D.wav")),mixer)),
        GestureListener(Orb(8,widget.canvas,50,170), Sfx(WaveGenerator(WaveFile("../data/coin.wav")),mixer)),
        GestureListener(Orb(8,widget.canvas,100,170), Sfx(WaveGenerator(WaveFile("../data/coin.wav")),mixer)),
        GestureListener(Orb(6,widget.canvas,50,290), Sfx(WaveGenerator(make_wave_buffers('../data/dont.txt','../data/dont.wav')['e'],True),mixer)),
        GestureListener(Orb(6,widget.canvas,100,290), Sfx(WaveGenerator(make_wave_buffers('../data/dont.txt','../data/dont.wav')['e'],True),mixer))]

        self.held_orb = None #orb that is currently being held

    #informs the GestureListeners of the hand position; if the sound effect is within reach of the 
    #hand and there is no other sound effect being grabbed, it will be picked up
    def set_hand_pos(self, pos):
        if self.held_orb != None:
            self.held_orb.set_hand_pos(pos)
        else:
            for orb in self.sound_orbs:
                if orb.set_hand_pos(pos):
                    self.held_orb = orb

    #called when the hand stops grabbing
    def release(self):
        if self.held_orb != None:
            self.held_orb.release()
            self.held_orb = None

    # updates the internal orbs; playing is whether the vocal track is playing or not
    def on_update(self, playing):
        for orb in self.sound_orbs:
            orb.on_update(playing)

    #called when the vocal track begins to play
    def play(self):
    	for orb in self.sound_orbs:
    		orb.set_orb()

#constrains the leap to a playing field and maps that playing field to the display window
RANGE_MIN = np.array((-100.0, 150, -100))
RANGE_MAX = np.array((100.0, 350, 100))
def scale_pt(pt):
    pt = np.clip(pt, RANGE_MIN, RANGE_MAX)
    pt[0]= (pt[0]+100)*Window.width/200.
    pt[1]= (pt[1]-150)*Window.height/200.
    pt[2] = (pt[2]+100)/200.
    return pt

#The main event loop run by Kivy
class MainWidget(BaseWidget) :
    def __init__(self,q1,q2):
        super(MainWidget, self).__init__()

        self.q = q1
        self.q2 = q2
        self.playing = False
        self.grabbing = False
        self.leap = Leap.Controller()

        #static images on screen
        Orbital(self.canvas,4)
        Orbital(self.canvas,3)
        Orbital(self.canvas,2)
        Orbital(self.canvas,1)
        NowBar(self.canvas)
        self.frs = [FreqRep(1,self.canvas),FreqRep(2,self.canvas),FreqRep(3,self.canvas),FreqRep(4,self.canvas)]
        
        #Audio setup
        self.audio = Audio(2)
        self.vocals = WaveGenerator(WaveFile("../data/foxx2.wav"))
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)
        self.sound_bank = SoundBank(self,self.mixer)

        #vocals initialization
        self.vocals.loop()
        self.on_restart()
        self.vocals.pause()

        #visual representation of vocal track
        self.vocal = Rectangle(pos=(Window.width/2.-25, Window.height/2.-25), size=(50,50), texture=Image('images/orb1.png').texture)
        self.vocal_color = Color(1,1,1,.65)
        self.canvas.add(self.vocal_color)
        self.canvas.add(self.vocal)
        
        #visual representation of hand position
        self.hand_disp = Cursor3D(Window.size, (0,0), (1, 1, 1), size_range=(2,20))
        self.canvas.add(Color(1,1,1))
        self.canvas.add(self.hand_disp)
 

    #Closes speech recognition process when this process stops
    def on_close(self):
        self.q.put('stop')

    #Callback when the user commands restart
    def on_restart(self):
        self.vocals.reset()
        self.mixer.add(self.vocals)
        self.vocals.play()

    # Called every frame. Changes the state if voice commands occur, and updates audio/visuals
    def on_update(self):

    	#process voice commands
        if not self.q2.empty():
            cmd = self.q2.get()
            print cmd
            if 'start' in cmd:
                self.on_restart()
                self.vocal_color.a = 1
                self.playing = True
                self.sound_bank.play()
            elif 'pause' in cmd or 'because' in cmd:
                self.vocals.pause()
                self.playing = False
                self.vocal_color.a = .65
            elif 'play' in cmd:
                self.vocals.play()
                self.playing = True
                self.vocal_color.a = 1
                self.sound_bank.play()

        #update audio/visuals for sound effects
        self.audio.on_update()
        self.sound_bank.on_update(self.playing)
        for fr in self.frs:
            fr.on_update()

        #update on-screen hand representation
        leap_frame = self.leap.frame()
        norm_pt = scale_pt(leap_one_palm(leap_frame)) 

        if leap_frame.hands.frontmost.grab_strength>.5:
            self.sound_bank.set_hand_pos(norm_pt)
            self.hand_disp.set_color((0,.5,1))
        else: 
            self.sound_bank.release()
            self.hand_disp.set_color((1,1,1))
        
        self.hand_disp.set_pos(norm_pt)


    #replication of Play, Start/Restart, and Pause commands via keys for debugging
    def on_key_down(self, keycode, modifiers):
 
        if keycode[1] == 'r': 
            self.on_restart()
            self.vocal_color.a = 1
            self.playing = True
            self.sound_bank.play()
        elif keycode[1] == 's':
        	self.vocals.pause()
        	self.playing = False
        	self.vocal_color.a = .75
        elif keycode[1] == 'p':
        	self.vocals.play()
        	self.playing = True
        	self.vocal_color.a = 1
        	self.sound_bank.play()

   

