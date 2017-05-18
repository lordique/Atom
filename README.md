

Atom is intended for beginners who wish to create electronic music soundtracks. The system provides a vocal track that you can start and stop using voice commands (think of the Amazon Echo), and your role is to create the background track behind the vocal track. In order to do this, the system has several sound effect objects which you can place in 3D space in order to determine a sound effect's volume and time/frequency at which it is played. 

Please refer to interface.png for a labelled image of the interface; terminology from this image will be used throughout the document.
____________________________

Installation instructions:

Requires Python 2.7.

- Additional hardware: Leap Motion, microphone (make sure all audio filtering is turned off)
- Additional software: PyAudio, NumPy, Kivy, Leap

Installation for Mac:
PyAudio: brew install portaudio 
pip install --global-option=build_ext --global-option="-I/usr/local/include" --global-option="-L/usr/local/lib" pyaudio


Numpy: pip install numpy

Kivy: pip install pygame

pip install -I Cython==0.23

USE_OSX_FRAMEWORKS=0 

pip install kivy

Leap: use the Leap Motion dmg in this folder.
____________________________

General instructions:

To run the system, please run the entrypt.py file in the project folder: "python entrypt.py"

There are two modes in the interface: play mode, and edit mode.  When you start the system, you are in edit mode.  

In order to switch modes, use voice commands. Voice commands/modes correspond to the vocal track; in play mode, the vocal track plays; in edit mode, it does not. "Start" or "restart" makes the vocal track begin playing from the beginning. "Pause" pauses the vocal track. "Play" resumes playing the vocal track.  Anytime the vocal track is not playing, the system is in edit mode.  You can see what the system thinks you are saying by reading the live transcript in the command prompt.

Regardless of mode, you can grab and place sound effects on frequency orbitals.  Different orbitals play sound objects at different frequencies; you can see the frequency at which an orbital plays a sound by watching the spinning blue dots. You can control a sound effect's volume by bringing it closer to you or farther from you (changing it's Z value); moving it on the X/Y plane changes its location on the X/Y plane of the interface.
__________________________

