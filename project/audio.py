import sys
sys.path.append('..')

import wave
import numpy as np

#parses .wav file audio data
class WaveFile(object):
    def __init__(self, filepath) :
        super(WaveFile, self).__init__()

        self.wave = wave.open(filepath)
        self.num_channels, self.sampwidth, self.sr, self.end, \
           comptype, compname = self.wave.getparams()

        assert(self.sampwidth == 2)
        assert(self.sr == 44100)

    # read an arbitrary chunk of data from the file
    def get_frames(self, start_frame, end_frame) :
        # get the raw data from wave file as a byte string. If asking for more than is available, it just
        # returns what it can
        self.wave.setpos(start_frame)
        raw_bytes = self.wave.readframes(end_frame - start_frame)

        # convert raw data to numpy array, assuming int16 arrangement
        samples = np.fromstring(raw_bytes, dtype = np.int16)

        # convert from integer type to floating point, and scale to [-1, 1]
        samples = samples.astype(np.float32)
        samples *= (1 / 32768.0)

        return samples

    def get_num_channels(self):
        return self.num_channels

#wrapper around the wavefile that handles the audio buffer
class WaveBuffer(object):
    def __init__(self, filepath, start_frame, num_frames):
        super(WaveBuffer, self).__init__()

        # get a local copy of the audio data from WaveFile
        wr = WaveFile(filepath)
        self.data = wr.get_frames(start_frame, start_frame + num_frames)
        self.num_channels = wr.get_num_channels()

    # start and end args are in units of frames,
    # so take into account num_channels when accessing sample data
    def get_frames(self, start_frame, end_frame) :
        start_sample = start_frame * self.num_channels
        end_sample = end_frame * self.num_channels
        return self.data[start_sample : end_sample]

    def get_num_channels(self):
        return self.num_channels

#A sound generator that reads audio from a .wav file into python
class WaveGenerator(object):
    def __init__(self, wave_source, loop=False):
        super(WaveGenerator, self).__init__()
        self.source = wave_source
        self.frame = 0
        self.gain = .5
        self.playing = True
        self.looping = loop
        self.cont = True

    def reset(self):
        self.frame = 0
        self.cont = True

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False

    def release(self):
        self.cont = False

    def loop(self):
        self.looping = True

    def stop_loop(self):
        self.looping = False

    def set_gain(self,gain):
        self.gain = gain

    def generate(self, num_frames, num_channels) :
        assert(num_channels == self.source.get_num_channels())

        # get data based on our position and requested # of frames
        output = self.playing*self.gain*self.source.get_frames(self.frame, self.frame + num_frames)

        # advance current-frame
        if self.playing:
            self.frame += num_frames

        # check for end-of-buffer condition:
        buff_check = num_frames * num_channels 
        continue_flag = len(output) == buff_check
        
        if not continue_flag:
            #pads the output with zeros so it is the correct size
            t_output = np.zeros(num_frames*num_channels) 
            t_output[:len(output)] = output
            output = t_output
            
            #resets the frame if loop is set to true
            if not self.looping:
                self.playing = False

            self.frame = 0

        # return
        return (output, self.cont)


# a class to hold a sound clip (start time, length) and its name
class AudioRegion(object):
    def __init__(self,name, start_frame, duration):
        super(AudioRegion, self).__init__()
        self.name = name
        self.start_frame = start_frame
        self.duration = duration


# a collection of sound clips that are read from a file
class SongRegions(object):
    def __init__(self, filepath):
        super(SongRegions, self).__init__()
        self.regions = []
        sampleRate = 44100

        #Obtaining the buffer data from a file
        regions = [region.strip().split('\t') for region in open(filepath).readlines()]
        #Parsing the data into the AudioRegion data container
        for region in regions: 
            self.regions.append(AudioRegion(region[3],int(float(region[0])*sampleRate),int(float(region[2])*sampleRate)))
    
    def get_region(self, region):
        return self.regions[region]

# return a dictionary of WaveBuffers, which are clips from a larger audio file
def make_wave_buffers(regions_path, wave_path):
    buffers = {}
    regions = SongRegions(regions_path).regions
    for region in regions:
        buffers[region.name] = WaveBuffer(wave_path,region.start_frame,region.duration)
    return buffers

#Audio representation of a sound effect; wrapper around a generic sound generator object
class Sfx(object):
    def __init__(self, generator, mixer):
        super(Sfx, self).__init__()
        self.gen = generator
        self.gen.reset()
        self.gen.pause()
        mixer.add(self.gen)

    def reset(self):
        self.gen.reset()

    def play(self):
        self.gen.stop_loop()
        self.gen.play()

    def stop(self):
        self.gen.pause()
        self.gen.reset()

    def set_vol(self,volume):
        self.gen.set_gain(volume)

    def loop(self):
        self.gen.loop()
        self.gen.play()

    def generate(self, num_frames, num_channels):
        (output,continue_flag) = self.gen.generate(num, num_channels)
        return (output, continue_flag)